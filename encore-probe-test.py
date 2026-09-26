#!/usr/bin/python3
"""Tests for encore-probe.py.

Standard library only, like the thing it tests. Run by hand:

    python3 encore-probe-test.py

No test here needs a network, a real RDP host, or root. Anything that cannot
be proved without one is not a test in this file — it is Test 11 in
docs/tests.md, and it is run by a human on a terminal.
"""

import contextlib
import importlib.util
import io
import os
import shutil
import socket
import ssl
import subprocess
import tempfile
import threading
import time
import unittest
import warnings

_HERE = os.path.dirname(os.path.abspath(__file__))


def load_probe():
    """Execute encore-probe.py afresh and return it as a module.

    A function rather than four lines at import time because one test needs a
    module that has not been imported yet: whatever the file does to
    process-global state, it does while it is being executed, and that is only
    watchable on an execution the test itself starts.
    """
    spec = importlib.util.spec_from_file_location(
        "encore_probe", os.path.join(_HERE, "encore-probe.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = load_probe()


class TestNegotiationRequest(unittest.TestCase):
    """The 19 bytes are copied from MS-RDPBCGR, not reasoned out, so they
    are written again here independently and compared."""

    def test_is_exactly_the_documented_nineteen_bytes(self):
        expected = (
            b"\x03\x00\x00\x13"                  # TPKT v3, length 19
            b"\x0e\xe0\x00\x00\x00\x00\x00"      # X.224 Connection Request, LI 14
            b"\x01\x00\x08\x00\x03\x00\x00\x00"  # RDP_NEG_REQ, SSL|HYBRID
        )
        self.assertEqual(probe.NEGOTIATION_REQUEST, expected)
        self.assertEqual(len(probe.NEGOTIATION_REQUEST), 19)


# The exchange ADR-0008 records as observed end to end, quoted from the raw
# capture in docs/architecture/NOTES.md. Selected protocol 0x02, HYBRID.
#   TPKT 03 00 00 13 | X.224 CC 0e d0 00 00 00 00 00
#   | RDP_NEG_RSP 02 0b 08 00  02 00 00 00
CAPTURED_RESPONSE = bytes.fromhex("030000130ed00000000000020b080002000000")


def negotiation_response(selected):
    """The captured frame with a different selectedProtocol."""
    return CAPTURED_RESPONSE[:15] + selected.to_bytes(4, "little")


def negotiation_failure(code):
    """The captured frame turned into an RDP_NEG_FAILURE carrying `code`."""
    return (
        CAPTURED_RESPONSE[:11]
        + b"\x03\x00\x08\x00"
        + code.to_bytes(4, "little")
    )


BARE_CONNECTION_CONFIRM = bytes(
    [0x03, 0x00, 0x00, 0x0B, 0x06, 0xD0, 0x00, 0x00, 0x00, 0x00, 0x00]
)


class TestParseNegotiationResponse(unittest.TestCase):
    def assertProbeError(self, status, data):
        with self.assertRaises(probe.ProbeError) as caught:
            probe.parse_negotiation_response(data)
        self.assertEqual(caught.exception.status, status)
        return caught.exception

    def test_captured_response_selects_hybrid(self):
        self.assertEqual(probe.parse_negotiation_response(CAPTURED_RESPONSE), 2)

    def test_selected_ssl_is_accepted(self):
        self.assertEqual(
            probe.parse_negotiation_response(negotiation_response(1)), 1
        )

    def test_selected_plain_rdp_has_no_certificate_to_see(self):
        self.assertProbeError(
            probe.STATUS_NO_TLS_OFFERED, negotiation_response(0)
        )

    def test_unknown_selected_protocol_has_no_certificate_to_see(self):
        self.assertProbeError(
            probe.STATUS_NO_TLS_OFFERED, negotiation_response(8)
        )

    def test_negotiation_failure_names_its_code(self):
        error = self.assertProbeError(
            probe.STATUS_NO_TLS_OFFERED, negotiation_failure(5)
        )
        self.assertIn("5", error.message)

    def test_bare_connection_confirm_means_plain_rdp_security(self):
        self.assertProbeError(
            probe.STATUS_NO_TLS_OFFERED, BARE_CONNECTION_CONFIRM
        )

    def test_truncated_frame_is_not_rdp(self):
        self.assertProbeError(probe.STATUS_NOT_RDP, CAPTURED_RESPONSE[:10])

    def test_a_tls_server_answering_directly_is_not_rdp(self):
        self.assertProbeError(
            probe.STATUS_NOT_RDP, b"\x16\x03\x01\x00\x50" + b"\x00" * 75
        )

    def test_wrong_x224_code_is_not_rdp(self):
        not_a_confirm = (
            CAPTURED_RESPONSE[:5] + b"\xe0" + CAPTURED_RESPONSE[6:]
        )
        self.assertProbeError(probe.STATUS_NOT_RDP, not_a_confirm)

    def test_empty_response_is_not_rdp(self):
        self.assertProbeError(probe.STATUS_NOT_RDP, b"")

    def test_absurd_declared_length_is_not_rdp(self):
        self.assertProbeError(
            probe.STATUS_NOT_RDP, b"\x03\x00\x00\x02" + b"\x00" * 20
        )

    def test_unknown_negotiation_type_is_not_rdp(self):
        unknown = CAPTURED_RESPONSE[:11] + b"\x09" + CAPTURED_RESPONSE[12:]
        self.assertProbeError(probe.STATUS_NOT_RDP, unknown)

    def test_frame_too_short_for_its_negotiation_structure_is_not_rdp(self):
        short = bytes([0x03, 0x00, 0x00, 0x0C, 0x07, 0xD0, 0x00, 0x00,
                       0x00, 0x00, 0x00, 0x02])
        self.assertProbeError(probe.STATUS_NOT_RDP, short)


class Certificate:
    """A throwaway self-signed certificate, generated by openssl into a
    temporary directory. `pem`/`key` are paths; `der` and `fingerprint` are
    what openssl itself says about it, so the probe can be cross-checked
    against the tool ADR-0008's fingerprint was originally produced with."""

    def __init__(self, directory, keyspec="rsa:2048", digest=None):
        self.pem = os.path.join(directory, "cert.pem")
        self.key = os.path.join(directory, "key.pem")
        command = [
            "openssl", "req", "-x509", "-newkey", keyspec, "-nodes",
            "-subj", "/CN=probe-test", "-days", "1",
            "-keyout", self.key, "-out", self.pem,
        ]
        if digest:
            command.append(digest)
        subprocess.run(command, check=True, capture_output=True)
        self.der = subprocess.run(
            ["openssl", "x509", "-in", self.pem, "-outform", "DER"],
            check=True, capture_output=True,
        ).stdout
        printed = subprocess.run(
            ["openssl", "x509", "-in", self.pem, "-noout",
             "-fingerprint", "-sha256"],
            check=True, capture_output=True, text=True,
        ).stdout
        self.fingerprint = printed.split("=", 1)[1].replace(":", "").strip().lower()


def openssl_or_skip(test):
    if shutil.which("openssl") is None:
        test.skipTest(
            "openssl is not on this machine, so the cross-check against the "
            "tool the recorded fingerprint came from was NOT made"
        )


class TestFingerprint(unittest.TestCase):
    def test_empty_input_matches_the_known_sha256_of_nothing(self):
        self.assertEqual(
            probe.fingerprint_sha256(b""),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )

    def test_is_sixty_four_lower_case_hex_characters(self):
        result = probe.fingerprint_sha256(b"anything at all")
        self.assertEqual(len(result), 64)
        self.assertRegex(result, r"\A[0-9a-f]{64}\Z")

    def test_agrees_with_openssl_on_a_real_certificate(self):
        openssl_or_skip(self)
        with tempfile.TemporaryDirectory() as directory:
            certificate = Certificate(directory)
            self.assertEqual(
                probe.fingerprint_sha256(certificate.der),
                certificate.fingerprint,
            )


class TestRequireCertificate(unittest.TestCase):
    def test_returns_the_der_it_was_given(self):
        self.assertEqual(probe.require_certificate(b"x"), b"x")

    def test_none_is_a_classified_failure(self):
        with self.assertRaises(probe.ProbeError) as caught:
            probe.require_certificate(None)
        self.assertEqual(caught.exception.status, probe.STATUS_NO_CERTIFICATE)


class TestNormaliseExpectedFingerprint(unittest.TestCase):
    CANONICAL = "ed47d1c3744afa9ffa86d80f3dfbe7a2be67c34e4b171e5fe5a61fec5ed5ef41"

    def assertUsageError(self, text):
        with self.assertRaises(probe.ProbeError) as caught:
            probe.normalise_expected_fingerprint(text)
        self.assertEqual(caught.exception.status, probe.STATUS_USAGE)

    def test_already_canonical(self):
        self.assertEqual(
            probe.normalise_expected_fingerprint(self.CANONICAL), self.CANONICAL
        )

    def test_accepts_what_openssl_prints(self):
        colon_separated = ":".join(
            self.CANONICAL[i:i + 2].upper() for i in range(0, 64, 2)
        )
        self.assertEqual(
            probe.normalise_expected_fingerprint(colon_separated), self.CANONICAL
        )

    def test_accepts_surrounding_whitespace(self):
        self.assertEqual(
            probe.normalise_expected_fingerprint(f"  {self.CANONICAL}\n"),
            self.CANONICAL,
        )

    def test_rejects_one_character_short(self):
        self.assertUsageError(self.CANONICAL[:-1])

    def test_rejects_one_character_long(self):
        self.assertUsageError(self.CANONICAL + "0")

    def test_rejects_non_hex(self):
        self.assertUsageError("g" * 64)


class TestPermissiveTlsContext(unittest.TestCase):
    """The probe is a gate, not the guard. A probe stricter than the client it
    precedes stops a healthy terminal for ever, which D-020 names as the
    expensive direction to be wrong in. These assertions are the only thing
    stopping a future reader's instinct to harden it."""

    def test_hostname_checking_is_off(self):
        self.assertIs(probe.permissive_tls_context().check_hostname, False)

    def test_the_certificate_is_not_verified(self):
        self.assertIs(
            probe.permissive_tls_context().verify_mode, ssl.CERT_NONE
        )

    def test_the_tls_floor_is_tls_one(self):
        self.assertIs(
            probe.permissive_tls_context().minimum_version,
            ssl.TLSVersion.TLSv1,
        )

    def test_each_call_returns_its_own_context(self):
        self.assertIsNot(
            probe.permissive_tls_context(), probe.permissive_tls_context()
        )

    def test_it_says_nothing_to_the_administrator(self):
        # Asking for a TLS 1.0 floor is deprecated, and we mean it. The
        # deprecation notice is addressed to us, not to the person reading the
        # journal at 2am -- and one line of noise above every successful probe
        # is how a reader learns to stop reading stderr.
        with warnings.catch_warnings(record=True) as raised:
            warnings.simplefilter("always")
            probe.permissive_tls_context()
        self.assertEqual(
            [str(w.message) for w in raised],
            [],
            "building the context must not print anything",
        )

    def test_it_does_not_leave_the_warning_filters_changed(self):
        """The suppression must be scoped to the one assignment. A filter left
        behind is process-global and would silently swallow deprecations from
        anywhere else in this program or this test run.

        Measured against an empty baseline, on a module executed here, because
        anything weaker has no teeth in a suite: comparing a snapshot taken in
        this test would pass a module-level `simplefilter` -- that filter is
        already in the list before the snapshot, put there when the module was
        imported, and an earlier test has already made the same call. The
        snapshot sees nothing change, and the leak reads as clean. So: reset
        the filters (restored on the way out by catch_warnings), execute the
        file, call it, and require that nothing at all was added -- neither at
        import nor at call.
        """
        with warnings.catch_warnings():
            warnings.resetwarnings()
            fresh = load_probe()
            fresh.permissive_tls_context()
            self.assertEqual(
                warnings.filters, [],
                "encore-probe.py added a process-global warning filter. Every "
                "suppression in it must be scoped with catch_warnings().",
            )

    def test_the_security_level_is_actually_lowered(self):
        # The independent proof that the lowering happened. SECLEVEL governs
        # cipher suites, signature algorithms and DH sizes during the
        # handshake -- the half of the envelope that verify_mode=CERT_NONE
        # does not already cover, and the half that bites against an old xrdp.
        self.assertEqual(probe.permissive_tls_context().security_level, 0)

    def test_it_refuses_nothing_the_real_client_would_offer(self):
        base = {
            cipher["name"]
            for cipher in ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT).get_ciphers()
        }
        permissive = {
            cipher["name"]
            for cipher in probe.permissive_tls_context().get_ciphers()
        }
        self.assertGreaterEqual(
            permissive, base,
            "suites the real client would offer and the probe would refuse: "
            f"{sorted(base - permissive)}. A far end offering only one of "
            "these would be classified TLS_FAILED while the client connects "
            "fine -- the false 'configuration is broken' that D-020 names as "
            "the expensive direction.",
        )

    def test_it_offers_no_unauthenticated_suite(self):
        # ALL includes aNULL. With verify_mode=CERT_NONE, a far end selecting
        # an anonymous suite would complete a handshake and present no
        # certificate -- and the real client never offers these, so we would be
        # accepting a handshake it would never have made.
        anonymous = sorted(
            cipher["name"]
            for cipher in probe.permissive_tls_context().get_ciphers()
            if cipher["auth"] == "auth-null"
        )
        self.assertEqual(
            anonymous, [],
            "the probe would accept an unauthenticated handshake and report "
            "NO_CERTIFICATE for a healthy target",
        )


class FakeRdpServer:
    """A scripted far end on 127.0.0.1, so every branch of the probe is
    reachable without a network and without a real RDP host.

    It accepts repeatedly, so a test can probe the same server twice.
    """

    def __init__(self, reply=CAPTURED_RESPONSE, certificate=None,
                 silent=False, close_before_reply=False):
        self.reply = reply
        self.certificate = certificate
        self.silent = silent
        self.close_before_reply = close_before_reply
        # Built here, on the calling thread, rather than per connection:
        # warnings.catch_warnings mutates process-global state and is not
        # thread-safe, and the accept loop runs in a thread.
        self.tls = None
        if certificate is not None:
            self.tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            with warnings.catch_warnings():
                # This fake far end is as old-fashioned as the probe tolerates,
                # so it trips the same deprecation. Silenced here so the tests
                # that assert on the probe's stderr are measuring the probe and
                # not this helper.
                warnings.simplefilter("ignore", DeprecationWarning)
                self.tls.minimum_version = ssl.TLSVersion.TLSv1
            self.tls.set_ciphers("DEFAULT@SECLEVEL=0")
            self.tls.load_cert_chain(certificate.pem, certificate.key)
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(8)
        self.port = self.listener.getsockname()[1]
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def _serve(self):
        while True:
            try:
                connection, _ = self.listener.accept()
            except OSError:
                return  # the listener was closed by stop(); that is the exit
            threading.Thread(
                target=self._handle, args=(connection,), daemon=True
            ).start()

    def _handle(self, connection):
        with connection:
            try:
                if self.silent:
                    time.sleep(5.0)
                    return
                self._read_exactly(connection, len(probe.NEGOTIATION_REQUEST))
                if self.close_before_reply:
                    return
                connection.sendall(self.reply)
                if self.tls is None:
                    return
                with self.tls.wrap_socket(connection, server_side=True) as tls:
                    tls.recv(1)
            except (OSError, ssl.SSLError):
                # The probe closes the socket the moment it has the certificate,
                # so a reset here is the expected end of a successful test, not
                # a fault. Nothing in this thread can report it anyway; what the
                # probe saw is what the test asserts on.
                pass

    @staticmethod
    def _read_exactly(connection, count):
        data = b""
        while len(data) < count:
            chunk = connection.recv(count - len(data))
            if not chunk:
                return data
            data += chunk
        return data

    def stop(self):
        self.listener.close()


class TestFetchPeerCertificate(unittest.TestCase):
    def fetch(self, server, timeout=5.0):
        return probe.fetch_peer_certificate("127.0.0.1", server.port, timeout)

    def assertProbeError(self, status, host, port, timeout=5.0):
        with self.assertRaises(probe.ProbeError) as caught:
            probe.fetch_peer_certificate(host, port, timeout)
        self.assertEqual(
            caught.exception.status, status, caught.exception.message
        )
        return caught.exception

    def test_happy_path_returns_the_hosts_certificate(self):
        openssl_or_skip(self)
        with tempfile.TemporaryDirectory() as directory:
            certificate = Certificate(directory)
            server = FakeRdpServer(certificate=certificate)
            self.addCleanup(server.stop)
            der = self.fetch(server)
            self.assertEqual(
                probe.fingerprint_sha256(der), certificate.fingerprint
            )

    def assertWeakCertificateAccepted(self, description, keyspec, digest):
        """The probe is a gate, not the guard. Being stricter than the client it
        precedes would stop a healthy terminal for ever, and self-signed
        certificates with small keys and old signatures are the normal case for
        xrdp and gnome-remote-desktop.

        **What this proves, exactly:** that `verify_mode` is `CERT_NONE`, so the
        probe accepts a certificate the client would question. It does NOT prove
        anything about `set_ciphers("DEFAULT@SECLEVEL=0")` -- `CERT_NONE` already
        bypasses the peer-certificate checks the security level governs, and
        these cases pass at SECLEVEL=2 as well. The cipher half of the envelope
        is asserted in TestPermissiveTlsContext, not here.

        Split by weakness on purpose: an openssl too new to *generate* one of
        them must not take the other check down with it.
        """
        openssl_or_skip(self)
        with tempfile.TemporaryDirectory() as directory:
            try:
                certificate = Certificate(directory, keyspec, digest)
            except subprocess.CalledProcessError as failure:
                self.skipTest(
                    f"openssl on this machine refuses to generate {description},"
                    " so the check that the probe accepts that kind of weak "
                    "certificate was NOT made: "
                    + failure.stderr.decode(errors="replace").strip()[-200:]
                )
            server = FakeRdpServer(certificate=certificate)
            self.addCleanup(server.stop)
            der = self.fetch(server)
            self.assertEqual(
                probe.fingerprint_sha256(der),
                certificate.fingerprint,
                f"the probe refused {description}, which the real client would "
                "have accepted -- it is now stricter than the guard it "
                "precedes, and it will stop a healthy terminal",
            )

    def test_a_small_key_is_still_accepted(self):
        self.assertWeakCertificateAccepted(
            "a 1024-bit key", "rsa:1024", None
        )

    def test_an_old_signature_is_still_accepted(self):
        self.assertWeakCertificateAccepted(
            "a SHA-1 signature", "rsa:2048", "-sha1"
        )

    def test_negotiation_failure_is_reported_as_no_tls_offered(self):
        server = FakeRdpServer(reply=negotiation_failure(5))
        self.addCleanup(server.stop)
        error = self.assertProbeError(
            probe.STATUS_NO_TLS_OFFERED, "127.0.0.1", server.port
        )
        self.assertIn("5", error.message)

    def test_a_host_that_closes_immediately_is_not_rdp(self):
        server = FakeRdpServer(close_before_reply=True)
        self.addCleanup(server.stop)
        self.assertProbeError(probe.STATUS_NOT_RDP, "127.0.0.1", server.port)

    def test_a_host_that_negotiates_then_will_not_handshake(self):
        server = FakeRdpServer(certificate=None)
        self.addCleanup(server.stop)
        self.assertProbeError(probe.STATUS_TLS_FAILED, "127.0.0.1", server.port)

    def test_a_host_that_never_answers_times_out(self):
        server = FakeRdpServer(silent=True)
        self.addCleanup(server.stop)
        self.assertProbeError(
            probe.STATUS_TIMEOUT, "127.0.0.1", server.port, timeout=0.5
        )

    def test_nothing_listening_is_unreachable(self):
        closed = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        closed.bind(("127.0.0.1", 0))
        port = closed.getsockname()[1]
        closed.close()
        self.assertProbeError(probe.STATUS_UNREACHABLE, "127.0.0.1", port)

    def test_a_name_that_cannot_resolve(self):
        # .invalid is reserved by RFC 2606 and must never resolve, so this
        # needs no network.
        host = "encore-probe-test.invalid"
        with self.assertRaises(probe.ProbeError) as caught:
            probe.fetch_peer_certificate(host, 3389, 2.0)
        self.assertEqual(
            caught.exception.status,
            probe.STATUS_DNS,
            "a reserved .invalid name did not come back as a DNS failure. If "
            "this says UNREACHABLE (4), this machine's resolver is hijacking "
            "NXDOMAIN and answering for names that do not exist -- that is a "
            "broken resolver, not a broken probe. The probe reported: "
            + caught.exception.message,
        )
        self.assertIn(host, caught.exception.message)

    def test_a_host_that_cannot_be_encoded_is_a_usage_error(self):
        """getaddrinfo raises UnicodeError -- a ValueError, NOT an OSError --
        for a name it cannot IDNA-encode, so it escapes the whole OSError
        taxonomy above. A doubled dot is a routine administrator typo.

        USAGE and not DNS: a structurally invalid address can never become
        valid by looking it up again, and a stored host that retries for ever
        against a name that cannot exist is exactly what D-028 is for.
        """
        for host, why in (
            ("..invalid", "an empty label"),
            ("a" * 64 + ".invalid", "a label over 63 characters"),
        ):
            with self.subTest(why=why):
                error = self.assertProbeError(
                    probe.STATUS_USAGE, host, 3389, timeout=1.0
                )
                self.assertIn(host, error.message)

    def test_a_bare_unicode_error_is_classified_and_not_a_crash(self):
        """The handler that stops a crash must not be able to cause one.

        `UnicodeError` has no `.reason`; only its subclasses do. CPython's IDNA
        codec raises a *bare* `UnicodeError` below 3.14 and a
        `UnicodeEncodeError` from 3.14 on, so which one arrives depends on the
        interpreter in front of whoever is running this. Raised directly here
        rather than through a hostname, so this test asks the same question on
        every version instead of only on the ones that happen to expose it.
        """
        def raise_bare_unicode_error(*_args, **_kwargs):
            raise UnicodeError("label empty or too long")

        original = socket.create_connection
        socket.create_connection = raise_bare_unicode_error
        self.addCleanup(setattr, socket, "create_connection", original)

        error = self.assertProbeError(
            probe.STATUS_USAGE, "..invalid", 3389, timeout=1.0
        )
        self.assertIn("..invalid", error.message)
        self.assertIn("label empty or too long", error.message)

    def test_a_timeout_too_large_for_a_socket_is_a_usage_error(self):
        """`inf` and 1e30 pass a `> 0` check and then raise OverflowError from
        settimeout -- the same hole as above, a non-OSError escaping the
        taxonomy. Operator-supplied, so it cannot strand a terminal, but it
        must still be a classified status and not a traceback."""
        for timeout in (float("inf"), 1e30):
            with self.subTest(timeout=timeout):
                self.assertProbeError(
                    probe.STATUS_USAGE, "127.0.0.1", 3389, timeout=timeout
                )


class TestMain(unittest.TestCase):
    """The output discipline is the whole safety of the command-line seam:
    stdout carries the fingerprint and nothing else, and is empty on every
    non-zero exit, so

        FP=$(encore-probe.py --expect "$PIN" "$HOST")

    written by a caller who forgets to check $? cannot come back holding an
    unverified fingerprint. It comes back empty.
    """

    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = probe.main(list(argv))
        return status, out.getvalue(), err.getvalue()

    def serving(self, **kwargs):
        server = FakeRdpServer(**kwargs)
        self.addCleanup(server.stop)
        return server

    def certificate_server(self):
        openssl_or_skip(self)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        certificate = Certificate(directory.name)
        return self.serving(certificate=certificate), certificate

    def assertSaysExactlyWhatHappened(self, err):
        """Two assertions, not one, because they fail for different reasons.

        The first catches the defect this codebase keeps producing: saying
        nothing at all. The second catches noise -- including a Python
        deprecation notice, which is addressed to us and not to the
        administrator reading the journal.
        """
        lines = [line for line in err.splitlines() if line.strip()]
        spoken = [
            line for line in lines
            if line.startswith("ok: ") or line.startswith("error: ")
        ]
        self.assertEqual(
            len(spoken), 1,
            "every path must report exactly once, as 'ok: ' or 'error: '. "
            f"Got {len(spoken)} such line(s) in {err!r}",
        )
        self.assertEqual(
            [line for line in lines if line not in spoken], [],
            "stderr carried something besides the one report. If this names a "
            "DeprecationWarning, come back to permissive_tls_context() rather "
            f"than hunting the parser. stderr was:\n{err}",
        )

    def assertStatusAndSilentStdout(self, status, *argv):
        got, out, err = self.run_main(*argv)
        self.assertEqual(got, status, err)
        self.assertEqual(out, "", "stdout must be empty on a non-zero exit")
        return err

    def test_success_prints_the_fingerprint_and_nothing_else(self):
        server, certificate = self.certificate_server()
        status, out, err = self.run_main("--port", str(server.port), "127.0.0.1")
        self.assertEqual(status, 0, err)
        self.assertEqual(out, certificate.fingerprint + "\n")
        self.assertSaysExactlyWhatHappened(err)
        self.assertIn(certificate.fingerprint, err)

    def test_expect_accepts_what_openssl_prints(self):
        server, certificate = self.certificate_server()
        pasted = ":".join(
            certificate.fingerprint[i:i + 2].upper() for i in range(0, 64, 2)
        )
        status, out, err = self.run_main(
            "--port", str(server.port), "--expect", pasted, "127.0.0.1"
        )
        self.assertEqual(status, 0, err)
        self.assertEqual(out, certificate.fingerprint + "\n")
        self.assertSaysExactlyWhatHappened(err)

    def test_a_mismatch_prints_no_fingerprint_at_all(self):
        server, certificate = self.certificate_server()
        wrong = "0" * 64
        err = self.assertStatusAndSilentStdout(
            probe.STATUS_MISMATCH,
            "--port", str(server.port), "--expect", wrong, "127.0.0.1",
        )
        self.assertIn(wrong, err)
        self.assertIn(certificate.fingerprint, err)

    def test_a_malformed_expect_is_a_usage_error(self):
        self.assertStatusAndSilentStdout(
            probe.STATUS_USAGE, "--expect", "deadbeef", "127.0.0.1"
        )

    def test_a_malformed_expect_is_reported_before_any_connection(self):
        # A typo in the pin must not cost a TCP connection and a timeout first.
        server = self.serving(silent=True)
        before = time.monotonic()
        self.assertStatusAndSilentStdout(
            probe.STATUS_USAGE,
            "--port", str(server.port), "--timeout", "30",
            "--expect", "deadbeef", "127.0.0.1",
        )
        self.assertLess(time.monotonic() - before, 5.0)

    def test_port_below_range_is_a_usage_error(self):
        self.assertStatusAndSilentStdout(
            probe.STATUS_USAGE, "--port", "0", "127.0.0.1"
        )

    def test_port_above_range_is_a_usage_error(self):
        self.assertStatusAndSilentStdout(
            probe.STATUS_USAGE, "--port", "70000", "127.0.0.1"
        )

    def test_timeout_of_zero_is_a_usage_error(self):
        self.assertStatusAndSilentStdout(
            probe.STATUS_USAGE, "--timeout", "0", "127.0.0.1"
        )

    def test_a_missing_host_is_a_usage_error(self):
        self.assertStatusAndSilentStdout(probe.STATUS_USAGE)

    def test_a_host_beginning_with_a_dash_is_a_host(self):
        # After --, argparse must not read it as an option. It cannot resolve,
        # so reaching DNS is the proof it was treated as a host.
        self.assertStatusAndSilentStdout(
            probe.STATUS_DNS, "--timeout", "2", "--", "-encore.invalid"
        )

    def test_a_structurally_invalid_host_is_a_usage_error_not_a_crash(self):
        """The exit status is the whole point here. An unhandled exception
        exits 1, and 1 is deliberately unassigned so that a crash can never be
        read as a classification -- so a doubled dot arriving as 1, with a
        traceback on stderr and nothing a human can act on, breaks both that
        rule and the "every path reports exactly once" rule at the same time.
        """
        for host, why in (
            ("..invalid", "an empty label"),
            ("a" * 64 + ".invalid", "a label over 63 characters"),
        ):
            with self.subTest(why=why):
                err = self.assertStatusAndSilentStdout(
                    probe.STATUS_USAGE, "--timeout", "1", "--", host
                )
                self.assertSaysExactlyWhatHappened(err)
                self.assertIn("error: ", err)

    def test_a_timeout_too_large_for_a_socket_is_a_usage_error(self):
        for timeout in ("inf", "1e30"):
            with self.subTest(timeout=timeout):
                err = self.assertStatusAndSilentStdout(
                    probe.STATUS_USAGE, "--timeout", timeout, "127.0.0.1"
                )
                self.assertSaysExactlyWhatHappened(err)
                self.assertIn("error: ", err)

    def test_every_probe_error_status_reaches_the_caller_unchanged(self):
        no_tls = self.serving(reply=negotiation_failure(5))
        not_rdp = self.serving(close_before_reply=True)
        tls_failed = self.serving(certificate=None)
        silent = self.serving(silent=True)
        closed = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        closed.bind(("127.0.0.1", 0))
        unreachable_port = closed.getsockname()[1]
        closed.close()

        cases = [
            (probe.STATUS_NO_TLS_OFFERED, ["--port", str(no_tls.port), "127.0.0.1"]),
            (probe.STATUS_NOT_RDP, ["--port", str(not_rdp.port), "127.0.0.1"]),
            (probe.STATUS_TLS_FAILED, ["--port", str(tls_failed.port), "127.0.0.1"]),
            (probe.STATUS_TIMEOUT,
             ["--port", str(silent.port), "--timeout", "0.5", "127.0.0.1"]),
            (probe.STATUS_UNREACHABLE,
             ["--port", str(unreachable_port), "127.0.0.1"]),
            (probe.STATUS_DNS,
             ["--timeout", "2", "encore-probe-test.invalid"]),
        ]
        for status, argv in cases:
            with self.subTest(status=status):
                err = self.assertStatusAndSilentStdout(status, *argv)
                self.assertSaysExactlyWhatHappened(err)
                self.assertIn("error: ", err)

    def test_two_runs_against_the_same_host_agree(self):
        server, _ = self.certificate_server()
        first = self.run_main("--port", str(server.port), "127.0.0.1")
        second = self.run_main("--port", str(server.port), "127.0.0.1")
        self.assertEqual(first[0], 0, first[2])
        self.assertEqual(first[1], second[1])

    def test_help_is_the_only_thing_besides_a_fingerprint_on_stdout(self):
        status, out, err = self.run_main("--help")
        self.assertEqual(status, 0)
        self.assertIn("NO_TLS_OFFERED", out)
        self.assertIn("deliberately unassigned", out)
        self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main()
