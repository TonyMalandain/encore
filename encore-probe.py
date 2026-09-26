#!/usr/bin/python3
"""Report the certificate a host presents for RDP, or say why it could not.

RDP does not begin with TLS. Before any handshake, MS-RDPBCGR requires a
TPKT-framed X.224 Connection Request carrying an RDP_NEG_REQ, and a Connection
Confirm carrying an RDP_NEG_RSP. That is why `openssl s_client` cannot reach
the certificate, and it is the whole of what this program implements
(ADR-0008).

Usage:

    encore-probe.py [--port PORT] [--timeout SECONDS] [--expect FINGERPRINT] HOST

On success the SHA-256 fingerprint of the host's certificate is printed to
stdout as 64 lower-case hex characters and a newline. That is the exact form
FreeRDP's certificate-db compares with. stdout carries the fingerprint and
nothing else: on every non-zero exit it is empty, so a caller who forgets to
check the exit status cannot come back holding an unverified value. Every exit
path, success included, writes exactly one line to stderr.

No credentials are involved. The certificate arrives during TLS, before NLA,
so this program never reads a password, a profile, a file, an environment
variable or stdin, and never spawns a process.

Exit statuses:

    0   OK               fingerprint on stdout; --expect, if given, matched
    2   USAGE            the arguments are wrong -- including a HOST that is
                         not a usable address at all (an empty label from a
                         doubled dot, a label over 63 characters) and a
                         --timeout too large for a socket. Those are wrong
                         input, not a lookup that failed today, so retrying
                         them can never help
    3   DNS              the name does not resolve
    4   UNREACHABLE      nothing listening there, or the host cannot be reached
    5   TIMEOUT          the host did not answer in time
    6   NO_TLS_OFFERED   the host refused the security mode, or chose plain
                         RDP -- there is no certificate to see
    7   NOT_RDP          something answered, but it did not speak RDP
    8   TLS_FAILED       negotiation succeeded, the TLS handshake did not
    9   NO_CERTIFICATE   TLS completed and the host presented no certificate
    10  MISMATCH         a fingerprint was seen, and it is not the --expect one

Status 1 is deliberately unassigned. An unhandled Python exception exits 1, so
by giving 1 no meaning a crash can never be mistaken for a classification.
Status 78 is never used here; it belongs to the runner (ADR-0007). This
program reports, and the caller decides what an outcome means.
"""

import argparse
import hashlib
import socket
import ssl
import sys
import warnings

STATUS_OK = 0
STATUS_USAGE = 2
STATUS_DNS = 3
STATUS_UNREACHABLE = 4
STATUS_TIMEOUT = 5
STATUS_NO_TLS_OFFERED = 6
STATUS_NOT_RDP = 7
STATUS_TLS_FAILED = 8
STATUS_NO_CERTIFICATE = 9
STATUS_MISMATCH = 10

# TPKT version 3, reserved, length 0x0013 = 19
# X.224 Connection Request, LI 14
# RDP_NEG_REQ, flags 0, length 8, requestedProtocols = 0x00000003 (SSL|HYBRID)
#
# The 0x03 is load-bearing. ADR-0008 records that 0x01, 0x00, 0x08 and an
# absent RDP_NEG_REQ all drew RDP_NEG_FAILURE 0x05 HYBRID_REQUIRED_BY_SERVER
# from the one observed target, with no TLS at all. Do not simplify it.
NEGOTIATION_REQUEST = (
    b"\x03\x00\x00\x13"
    b"\x0e\xe0\x00\x00\x00\x00\x00"
    b"\x01\x00\x08\x00\x03\x00\x00\x00"
)


class ProbeError(Exception):
    """A classified failure. Carries its own exit status and its own wording.

    The status and the message travel together so there is no second table
    mapping wording to codes that could drift apart from the one in the module
    docstring. Deliberately not an OSError, so the OSError taxonomy in
    fetch_peer_certificate cannot swallow it.
    """

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


# MS-RDPBCGR failureCode values, so the message says what a human can act on
# rather than only a number. An unlisted code is still reported, as a number.
NEGOTIATION_FAILURES = {
    0x01: "SSL_REQUIRED_BY_SERVER",
    0x02: "SSL_NOT_ALLOWED_BY_SERVER",
    0x03: "SSL_CERT_NOT_ON_SERVER",
    0x04: "INCONSISTENT_FLAGS",
    0x05: "HYBRID_REQUIRED_BY_SERVER",
    0x06: "SSL_WITH_USER_AUTH_REQUIRED_BY_SERVER",
}

_TPKT_VERSION = 0x03
_X224_CONNECTION_CONFIRM = 0xD0
_TYPE_RDP_NEG_RSP = 0x02
_TYPE_RDP_NEG_FAILURE = 0x03
_PROTOCOL_SSL = 0x01
_PROTOCOL_HYBRID = 0x02


def parse_negotiation_response(data: bytes) -> int:
    """Return the selected protocol (0x01 or 0x02). Raise ProbeError otherwise.

    `data` is one whole TPKT frame, header included. Parsed structurally and
    never compared against a literal: ADR-0008's diagram and the raw capture in
    docs/architecture/NOTES.md disagree by one byte, so a byte-for-byte
    comparison against either could reject every real response.
    """
    if len(data) < 4 or data[0] != _TPKT_VERSION:
        raise ProbeError(
            STATUS_NOT_RDP,
            "the host answered, but not with an RDP TPKT frame "
            f"(got {len(data)} bytes: {data[:8].hex() or 'nothing'})",
        )

    declared = int.from_bytes(data[2:4], "big")
    if not 7 <= declared <= 1024:
        raise ProbeError(
            STATUS_NOT_RDP,
            "the host answered with an RDP frame declaring an impossible "
            f"length of {declared} bytes",
        )
    if len(data) != declared:
        raise ProbeError(
            STATUS_NOT_RDP,
            f"the host announced a {declared}-byte RDP frame but sent "
            f"{len(data)} bytes -- it closed the connection mid-answer",
        )

    if data[5] != _X224_CONNECTION_CONFIRM:
        raise ProbeError(
            STATUS_NOT_RDP,
            "the host answered with X.224 code "
            f"{data[5]:#04x}, not a Connection Confirm "
            f"({_X224_CONNECTION_CONFIRM:#04x})",
        )

    if declared == 11:
        raise ProbeError(
            STATUS_NO_TLS_OFFERED,
            "the host accepted the connection with no negotiation structure, "
            "which means plain RDP security -- there is no certificate to see",
        )

    if declared < 19:
        raise ProbeError(
            STATUS_NOT_RDP,
            f"the host answered with a {declared}-byte frame: too long to be "
            "a bare Connection Confirm, too short to hold a negotiation "
            "structure",
        )

    negotiation_type = data[11]
    value = int.from_bytes(data[15:19], "little")

    if negotiation_type == _TYPE_RDP_NEG_FAILURE:
        name = NEGOTIATION_FAILURES.get(value)
        named = f" {name}" if name else ""
        raise ProbeError(
            STATUS_NO_TLS_OFFERED,
            "the host refused the security mode with RDP_NEG_FAILURE code "
            f"{value} ({value:#04x}){named} -- no TLS is started, so there is "
            "no certificate to see",
        )

    if negotiation_type != _TYPE_RDP_NEG_RSP:
        raise ProbeError(
            STATUS_NOT_RDP,
            f"the host answered with negotiation type {negotiation_type:#04x}, "
            "which is neither RDP_NEG_RSP nor RDP_NEG_FAILURE",
        )

    if value not in (_PROTOCOL_SSL, _PROTOCOL_HYBRID):
        raise ProbeError(
            STATUS_NO_TLS_OFFERED,
            f"the host selected protocol {value:#010x}, which does not start "
            "TLS -- there is no certificate to see",
        )

    return value


def permissive_tls_context() -> ssl.SSLContext:
    """A TLS client context that accepts anything, on purpose.

    **This is a decision, not laziness, and it must not be hardened.** The probe
    is a gate, not the guard: `deny-userconfig` in /etc/FreeRDP/certificates.json
    is what refuses a certificate, and the probe only needs to *see* one. A probe
    whose acceptance envelope is stricter than the real client's would stop a
    healthy terminal for ever -- a false "the configuration is broken", which
    D-020 names as the more expensive direction to be wrong in. Self-signed
    certificates from xrdp and gnome-remote-desktop, with small keys and old
    signatures, are the normal case here. ADR-0008: "Treat the permissive
    envelope as part of this decision, not as an option."

    A fresh context every call, so nothing can tighten a shared one.
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # Order matters: PROTOCOL_TLS_CLIENT starts with check_hostname True, and
    # Python raises ValueError if verify_mode is set to CERT_NONE while it is.
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    # Stated as a number because Ubuntu's /etc/ssl/openssl.cnf sets a TLS 1.2
    # floor for anything that does not say otherwise. Saying otherwise is the
    # point. maximum_version is left alone.
    #
    # TLSv1 is deprecated and we mean it -- see above. The warning is addressed
    # to us, not to the administrator reading the journal, and one line of
    # noise above every successful probe is how a reader learns to stop reading
    # stderr. Scoped to this one assignment: warnings.filters is process-global,
    # so a module-level filter would silently swallow deprecations from
    # anywhere else.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        context.minimum_version = ssl.TLSVersion.TLSv1
    # `ALL` rather than `DEFAULT`, because Python's own default list for
    # PROTOCOL_TLS_CLIENT is NOT OpenSSL's `DEFAULT`: naming `DEFAULT` lowers
    # the security level as intended and silently drops suites the untouched
    # context offers -- on OpenSSL 3.5 all the AES-CCM ones. That is the probe
    # becoming stricter than the client in a corner nobody looked at.
    #
    # `!aNULL` because `ALL` admits anonymous suites. With verify_mode
    # CERT_NONE, a far end selecting one would complete a handshake and present
    # no certificate, and the probe would report NO_CERTIFICATE for a healthy
    # target -- a handshake the real client would never have offered.
    #
    # `@SECLEVEL=0` is the only way to reach security level 0 from Python:
    # SSLContext.security_level is read-only, and "@SECLEVEL=0" alone selects
    # no ciphers at all. It governs the half of the envelope that CERT_NONE
    # does not: suites, signature algorithms and DH sizes during the handshake.
    #
    # ADR-0008 records the string as "DEFAULT@SECLEVEL=0". The property it
    # asserts is what matters and is unchanged: no suite the untouched client
    # context offers may be absent, and no unauthenticated suite may be
    # present. Both are asserted in encore-probe-test.py.
    context.set_ciphers("ALL:!aNULL@SECLEVEL=0")
    return context


def require_certificate(der: bytes | None) -> bytes:
    """Return the DER. Raise ProbeError(STATUS_NO_CERTIFICATE) if there is none.

    This exists as a separate function only so that the None branch -- which no
    test can reach through a real handshake -- is reachable by a test. That is
    its whole justification. Do not inline it.
    """
    if der is None:
        raise ProbeError(
            STATUS_NO_CERTIFICATE,
            "TLS completed but the host presented no certificate, so there is "
            "nothing to fingerprint",
        )
    return der


def fingerprint_sha256(der: bytes) -> str:
    """SHA-256 over the DER certificate, lower-case hex, no colons -- the exact
    form FreeRDP's certificate-db compares with."""
    return hashlib.sha256(der).hexdigest()


def _read_exactly(sock: socket.socket, count: int) -> bytes:
    """Read exactly `count` bytes, or raise ProbeError(STATUS_NOT_RDP)."""
    data = b""
    while len(data) < count:
        chunk = sock.recv(count - len(data))
        if not chunk:
            raise ProbeError(
                STATUS_NOT_RDP,
                f"the host closed the connection after {len(data)} of the "
                f"{count} bytes expected -- it is not speaking RDP",
            )
        data += chunk
    return data


def _read_negotiation_frame(sock: socket.socket) -> bytes:
    """Read one whole TPKT frame, by its declared length rather than by a
    fixed size, so a longer-than-expected answer is still parsed."""
    header = _read_exactly(sock, 4)
    if header[0] != _TPKT_VERSION:
        raise ProbeError(
            STATUS_NOT_RDP,
            "the host answered, but not with an RDP TPKT frame "
            f"(first bytes {header.hex()})",
        )
    declared = int.from_bytes(header[2:4], "big")
    if not 7 <= declared <= 1024:
        raise ProbeError(
            STATUS_NOT_RDP,
            "the host answered with an RDP frame declaring an impossible "
            f"length of {declared} bytes",
        )
    return header + _read_exactly(sock, declared - 4)


def fetch_peer_certificate(host: str, port: int, timeout: float) -> bytes:
    """Connect, negotiate, handshake, return the peer's leaf certificate as DER.

    Raises ProbeError for every failure. Closes everything it opened. The
    timeout applies to the connect, to each read and to the handshake
    separately; it is not a total deadline.
    """
    try:
        # settimeout is what refuses an unusable timeout, and
        # create_connection calls it *after* it has made a socket, without
        # closing that socket when it raises. Try the value on one we own and
        # close, so the failure below costs no leaked file descriptor and no
        # ResourceWarning on stderr beside the one report.
        with socket.socket() as candidate:
            candidate.settimeout(timeout)
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.sendall(NEGOTIATION_REQUEST)
            parse_negotiation_response(_read_negotiation_frame(sock))
            # From here on the far end is speaking TLS on this same socket.
            try:
                with permissive_tls_context().wrap_socket(
                    sock, server_hostname=host
                ) as tls:
                    return require_certificate(
                        tls.getpeercert(binary_form=True)
                    )
            except ssl.SSLError as failure:
                raise ProbeError(
                    STATUS_TLS_FAILED,
                    f"the TLS handshake with {host}:{port} failed after RDP "
                    f"negotiation succeeded: {failure}",
                ) from failure
            except TimeoutError as failure:
                raise ProbeError(
                    STATUS_TIMEOUT,
                    f"{host}:{port} stopped answering during the TLS "
                    f"handshake, after {timeout} seconds",
                ) from failure
            except OSError as failure:
                raise ProbeError(
                    STATUS_TLS_FAILED,
                    f"{host}:{port} dropped the connection during the TLS "
                    f"handshake: {failure}",
                ) from failure
    # Order matters: gaierror, TimeoutError and ConnectionRefusedError are all
    # subclasses of OSError, so a single `except OSError` would collapse the
    # whole taxonomy into one status. ProbeError is not an OSError, so it
    # passes through every clause here untouched.
    except socket.gaierror as failure:
        raise ProbeError(
            STATUS_DNS,
            f"the name {host!r} does not resolve: {failure.strerror or failure}",
        ) from failure
    except TimeoutError as failure:
        raise ProbeError(
            STATUS_TIMEOUT,
            f"{host}:{port} did not answer within {timeout} seconds",
        ) from failure
    except ConnectionRefusedError as failure:
        raise ProbeError(
            STATUS_UNREACHABLE,
            f"nothing is listening on {host}:{port} -- the connection was "
            "refused",
        ) from failure
    except OSError as failure:
        # No route, network down, or anything else the connect could not do.
        # They are one status by design -- the caller's decision is the same --
        # so the operating system's own wording carries the difference.
        raise ProbeError(
            STATUS_UNREACHABLE,
            f"could not reach {host}:{port}: {failure.strerror or failure}",
        ) from failure
    # The two below are NOT OSErrors, so every clause above misses them and
    # they would leave main as a traceback and exit 1 -- the one status that
    # must stay unassigned, so that a crash can never be read as a
    # classification.
    except UnicodeError as failure:
        # getaddrinfo IDNA-encodes the name before it looks anything up, and
        # raises UnicodeError (a ValueError) for a name that cannot be
        # encoded at all: an empty label from a doubled dot, or a label over
        # 63 characters. USAGE and not DNS on purpose -- this address is
        # structurally invalid, so no later lookup can make it valid, and a
        # caller that read it as "the lookup failed today" would retry for
        # ever against a name that cannot exist.
        #
        # `{failure}` and not `{failure.reason}`: only UnicodeError's
        # subclasses carry `.reason`, and which one arrives depends on the
        # interpreter -- CPython's IDNA codec raises a bare UnicodeError below
        # 3.14 and a UnicodeEncodeError from 3.14 on. Reading an attribute that
        # may not be there is how this handler would raise AttributeError and
        # exit 1 with a traceback: the exact failure it exists to prevent.
        raise ProbeError(
            STATUS_USAGE,
            f"{host!r} is not a usable address: {failure}. No lookup "
            "was attempted -- fix the host and run it again",
        ) from failure
    except OverflowError as failure:
        # settimeout refuses a value the C clock cannot hold: `inf`, or
        # anything around 1e30. It passes the `> 0` check in main, so it can
        # only be caught here.
        raise ProbeError(
            STATUS_USAGE,
            f"--timeout {timeout} is too large for a socket timeout; give a "
            "number of seconds a machine can wait",
        ) from failure


def normalise_expected_fingerprint(text: str) -> str:
    """Strip whitespace and colons, lower-case, require 64 hex. Raise ProbeError.

    An administrator pastes what `openssl x509 -fingerprint -sha256` prints:
    upper case, colon-separated. That must work.
    """
    candidate = "".join(text.split()).replace(":", "").lower()
    if len(candidate) != 64 or any(c not in "0123456789abcdef" for c in candidate):
        raise ProbeError(
            STATUS_USAGE,
            "--expect must be a SHA-256 fingerprint: 64 hex characters, with "
            "or without colons, in either case. Got "
            f"{len(candidate)} character(s): {text!r}",
        )
    return candidate


def main(argv: list[str]) -> int:
    """The only place in this file that touches stdout, stderr or the status."""
    parser = argparse.ArgumentParser(
        prog="encore-probe.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "host",
        metavar="HOST",
        help="the machine to ask: a hostname or an address literal. Never "
             "split on ':' -- an IPv6 literal would be ambiguous, so the port "
             "has its own option.",
    )
    parser.add_argument(
        "--port", type=int, default=3389,
        help="the RDP port, 1..65535 (default: %(default)s)",
    )
    parser.add_argument(
        "--timeout", type=float, default=10.0,
        help="seconds, greater than zero (default: %(default)s). Applied to "
             "the connect, to each read and to the TLS handshake separately -- "
             "it is NOT a total deadline.",
    )
    parser.add_argument(
        "--expect", metavar="FINGERPRINT",
        help="a SHA-256 fingerprint this host must present. Colons, upper "
             "case and surrounding whitespace are accepted, so the output of "
             "`openssl x509 -fingerprint -sha256` can be pasted as-is. On a "
             "mismatch nothing is printed to stdout and the exit status is 10.",
    )

    try:
        arguments = parser.parse_args(argv)
    except SystemExit as exit_request:
        # argparse has already said what was wrong, on stderr, and --help has
        # already printed to stdout. Return its status rather than letting it
        # propagate, so this function's only contract is its return value.
        return int(exit_request.code or 0)

    try:
        if not 1 <= arguments.port <= 65535:
            raise ProbeError(
                STATUS_USAGE,
                f"--port must be between 1 and 65535, not {arguments.port}",
            )
        if not arguments.timeout > 0:
            raise ProbeError(
                STATUS_USAGE,
                f"--timeout must be greater than zero, not {arguments.timeout}",
            )
        # Before any network work: a typo in the pin must not cost a TCP
        # connection and a timeout before being reported.
        expected = (
            normalise_expected_fingerprint(arguments.expect)
            if arguments.expect is not None
            else None
        )

        der = fetch_peer_certificate(
            arguments.host, arguments.port, arguments.timeout
        )
        fingerprint = fingerprint_sha256(der)

        where = f"{arguments.host}:{arguments.port}"
        if expected is not None and fingerprint != expected:
            raise ProbeError(
                STATUS_MISMATCH,
                f"{where} presented sha256 {fingerprint}, but {expected} was "
                "expected -- this is not the machine that was pinned, or its "
                "certificate has been replaced",
            )
    except ProbeError as failure:
        print(f"error: {failure.message}", file=sys.stderr)
        return failure.status

    confirmation = (
        " and it matched --expect" if expected is not None else ""
    )
    print(
        f"ok: {where} presented a certificate, sha256 {fingerprint}"
        f"{confirmation}",
        file=sys.stderr,
    )
    print(fingerprint)
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
