# Plan — the certificate probe (`BACKLOG.md` item 7, first slice; ADR-0008)

**Sensitive:** this is identity machinery. It decides what fingerprint the
administrator confirms (D-029) and what the runner compares against the pin
(D-028). It is **credential-free by construction** — the certificate arrives
during TLS, before NLA, so the probe never holds, reads or logs a password.
Keep it that way: no password argument, no reading of the profile, no stdin.

**Status:** design only. Nothing here is built. The consuming tickets (the
installer's capture-and-confirm step, and the runner's pre-flight) are **out of
scope** — see *Out of scope*.

---

## What changes, and for whom

Nothing a person at a terminal can see. One new standalone script appears in the
repository: given a host, it prints the SHA-256 fingerprint of the certificate
that host presents for RDP, or exits with a distinct documented status saying
why it could not. It is the artifact ADR-0008 decided on, and it is the thing
two later tickets call.

The audience is the terminal administrator, indirectly at setup and at launch,
and directly when debugging over SSH with no graphical session.

---

## The component

- **Responsible for:** answering one question — *what certificate is this host
  presenting for RDP, and if not, why not* — and nothing else.
- **Has drifted by:** no drift. The file does not exist yet.
- **This change belongs here because:** there is no existing home for it and the
  two candidate homes are both wrong. `encore-install.sh` owns what differs
  between terminals (boundary 5) and `encore-kiosk.sh` owns launching the client
  (boundary 4); neither owns speaking a protocol, and putting the exchange in
  either would make it uncallable by the other. ADR-0008 already decided that
  **one piece of our own code does both jobs**, so the new part is the
  architect's decision, taken; its shape is this plan's.

**Boundary note for the record:** this adds a seventh part to
`docs/architecture/boundaries.md` — *the certificate probe*. It owns speaking the
RDP preamble and reporting a fingerprint. It **must not know** about profiles,
credentials, units, consoles, compositors, pin files or `/etc/FreeRDP`. It is a
gate, not the guard (ADR-0008); enforcement stays in
`/etc/FreeRDP/certificates.json`. Recording that boundary in the architecture
record is the architect's edit, not this ticket's — flagged, not done.

---

## The file

| | |
|---|---|
| Path in the repository | `encore-probe.py` at the root, beside the other shipped artifacts |
| Mode | `755` |
| Shebang | `#!/usr/bin/python3` — **not** `/usr/bin/env python3`; the runner will call it from a systemd unit where `PATH` is not ours to assume |
| Language | Python 3, **standard library only** (D-030). Permitted imports: `argparse`, `hashlib`, `socket`, `ssl`, `sys`. Nothing else. No `subprocess`, ever — there is no shell in this program and therefore no injection surface from the host argument |
| Tests | `encore-probe-test.py` at the root, `unittest` from the standard library, run by hand: `python3 encore-probe-test.py` |

**Why a `.py` suffix when the other scripts are `.sh`:** the suffix is how this
repository already says what language a file is (`encore-kiosk.sh`,
`encore-kiosk.target`). Keep it.

**Neither file is added to `encore-install.sh` or `encore-uninstall.sh` in this
ticket.** Installing the probe to `/usr/local/bin` and removing it again is part
of the consuming tickets, because until something calls it, an installed copy is
a file the uninstaller can forget (C-3).

**`encore-probe.py` IS added to `encore-push.sh`'s `FILES` list** — one line. The
ticket requires that a human can run it by hand on a terminal to debug, and
`encore-push.sh` is the only way anything reaches a terminal. `encore-probe-test.py`
is **not** pushed.

---

## Seams

### The outer seam — the command line

This is the seam the two later tickets consume. It is a shell-level contract, so
it must be as hard to misuse as a function signature.

```
encore-probe.py [--port PORT] [--timeout SECONDS] [--expect FINGERPRINT] HOST
```

| Argument | Rule |
|---|---|
| `HOST` | required, positional, exactly one. Passed to `socket.create_connection` verbatim and to `server_hostname=` verbatim. A hostname or an address literal, both permitted (R-5). It is **never** split on `:` — an IPv6 literal makes that ambiguous, and the port has its own option |
| `--port` | integer, default `3389`, must be `1..65535` |
| `--timeout` | float seconds, default `10.0`, must be `> 0`. Applied as the socket timeout, so it covers the connect, each preamble read, and the TLS handshake separately — **not** a total deadline. Say so in `--help` |
| `--expect` | optional. A SHA-256 fingerprint the caller requires. Normalised before comparison: whitespace and `:` removed, lower-cased. Must then be exactly 64 hex characters, or it is a usage error. This exists so an administrator can paste `openssl x509 -fingerprint -sha256` output (upper case, colon-separated) and have it work |

**Output discipline — this is the part that makes the seam safe.**

- **stdout carries the fingerprint and nothing else, ever**: 64 lower-case hex
  characters and a newline, on exit 0 only. The single exception is `--help`.
- **On every non-zero exit, stdout is empty.** In particular, `--expect` given
  and not matched prints **nothing** on stdout. The observed fingerprint appears
  in the stderr message, named alongside the expected one, which is what
  ADR-0008's runner row asks for.
- **The misuse this makes impossible:** `FP=$(encore-probe.py --expect "$PIN" "$HOST")`
  written by a caller who forgets to check `$?` cannot come back holding an
  unverified fingerprint. It comes back empty.
- **stderr carries exactly one line on every path, success included.** Silent
  failure is this codebase's recurring defect; a silent success is the same
  defect wearing better clothes. Success: `ok: <host>:<port> presented a
  certificate, sha256 <fp>` (and, with `--expect`, that it matched). Failure:
  `error: <plain language>`, matching the `die()` wording style already used by
  `encore-install.sh:15`.
- **Nothing is read from stdin. No file is created, read or written. No
  environment variable is read. No process is spawned. Nothing is drawn.**

### Exit statuses

Exactly one table, in the module docstring, which is also what `--help` prints.

| Status | Name | Means | Reachable when |
|---|---|---|---|
| `0` | `OK` | fingerprint on stdout; if `--expect` was given, it matched | |
| `2` | `USAGE` | the arguments are wrong | argparse's own default; keep it |
| `3` | `DNS` | the name does not resolve | `socket.gaierror` |
| `4` | `UNREACHABLE` | nothing is listening there, or the host cannot be reached | `ConnectionRefusedError`, `EHOSTUNREACH`, `ENETUNREACH`, other `OSError` at connect |
| `5` | `TIMEOUT` | the host did not answer in time | `TimeoutError` at any phase |
| `6` | `NO_TLS_OFFERED` | the host refused the security mode, or chose plain RDP — there is no certificate to see | `RDP_NEG_FAILURE`, selected protocol `0x00`, a Connection Confirm carrying no negotiation structure at all, or a selected protocol that is neither `0x01` nor `0x02` |
| `7` | `NOT_RDP` | something answered, but it did not speak the RDP preamble | bad TPKT version or length, wrong X.224 code, short read, connection closed mid-preamble |
| `8` | `TLS_FAILED` | the negotiation succeeded but the TLS handshake did not | `ssl.SSLError`, or the connection dropping during the handshake |
| `9` | `NO_CERTIFICATE` | TLS completed and the host presented no certificate | `getpeercert(binary_form=True)` returned `None` |
| `10` | `MISMATCH` | a fingerprint was seen, and it is not the one `--expect` named | |

Two rules about this table that are decisions, not taste:

1. **`1` is deliberately unassigned.** An unhandled Python exception exits 1. By
   never giving 1 a meaning, a crash can never be mistaken for a classification.
   This is the same asymmetry ADR-0008 used to reject the `ctypes` route: our
   failure mode must be legible, not a wrong branch.
2. **`78` is never used by this script.** It belongs to the runner
   (`RestartPreventExitStatus=78`, ADR-0007). The probe reports; the caller
   decides which of D-020's branches an outcome belongs to.

### The inner seams — exact signatures

```python
STATUS_OK               = 0
STATUS_USAGE            = 2
STATUS_DNS              = 3
STATUS_UNREACHABLE      = 4
STATUS_TIMEOUT          = 5
STATUS_NO_TLS_OFFERED   = 6
STATUS_NOT_RDP          = 7
STATUS_TLS_FAILED       = 8
STATUS_NO_CERTIFICATE   = 9
STATUS_MISMATCH         = 10

NEGOTIATION_REQUEST: bytes   # the 19 bytes below, a module constant

class ProbeError(Exception):
    """A classified failure. Carries its own exit status and its own wording."""
    def __init__(self, status: int, message: str) -> None: ...

def parse_negotiation_response(data: bytes) -> int:
    """Return the selected protocol (0x01 or 0x02). Raise ProbeError otherwise."""

def permissive_tls_context() -> ssl.SSLContext: ...

def require_certificate(der: bytes | None) -> bytes:
    """Return the DER. Raise ProbeError(STATUS_NO_CERTIFICATE) if there is none."""

def fetch_peer_certificate(host: str, port: int, timeout: float) -> bytes:
    """Connect, negotiate, handshake, return the peer's leaf certificate as DER.
    Raises ProbeError for every failure. Closes everything it opened."""

def fingerprint_sha256(der: bytes) -> str: ...

def normalise_expected_fingerprint(text: str) -> str:
    """Strip whitespace and colons, lower-case, require 64 hex. Raise ProbeError."""

def main(argv: list[str]) -> int: ...
```

**The misuses these make impossible:**

- `ProbeError` carries the status **and** the wording together, so there is no
  second table mapping messages to codes that could drift apart from the first.
  Every exit path is one `raise` with both halves in it.
- `fetch_peer_certificate` is one call that opens, negotiates, wraps and closes.
  There is no `connect()` you must call before `read()`, no context to prepare,
  no module-level socket, no `init()`. Nothing in this file holds state between
  calls, so there is no order to get wrong.
- `permissive_tls_context()` returns a finished context. It is never mutated by
  a caller, so the permissive envelope cannot be tightened by accident from
  somewhere else in the file.
- `require_certificate` exists only so that the `None` branch — which no test
  can reach through a real handshake — is reachable by a test. That is its whole
  justification; write it in the docstring so nobody inlines it later.
- **Only `main` touches `sys.stdout`, `sys.stderr` and the exit status.**
  Everything else takes values and returns values or raises. That is what keeps
  the tests three lines long.

---

## The bytes, and how to read them

**Send** (19 bytes, exactly; `NEGOTIATION_REQUEST`):

```
03 00 00 13   TPKT version 3, reserved, length 0x0013 = 19
0e e0 00 00 00 00 00   X.224 Connection Request, LI 14
01 00 08 00 03 00 00 00   RDP_NEG_REQ, flags 0, length 8,
                          requestedProtocols = 0x00000003 (SSL|HYBRID)
```

`0x03` is load-bearing. ADR-0008 records that `0x01`, `0x00`, `0x08` and an
absent `RDP_NEG_REQ` all drew `RDP_NEG_FAILURE 0x05 HYBRID_REQUIRED_BY_SERVER`
from the one observed target, with no TLS at all. Do not "simplify" it.

**Read, by framing, not by length:**

1. Read exactly 4 bytes. Fewer, or a first byte that is not `0x03` →
   `STATUS_NOT_RDP`.
2. Take the declared length from bytes 2–3, big-endian. It must be `7..1024`, or
   `STATUS_NOT_RDP`.
3. Read exactly `length - 4` more bytes. Short read or closed connection →
   `STATUS_NOT_RDP`.
4. Byte 5 is the X.224 LI, byte 6 must be `0xD0` (Connection Confirm), or
   `STATUS_NOT_RDP`.
5. If the frame is 11 bytes — a bare Connection Confirm with no negotiation
   structure — that is plain RDP security and there is no certificate:
   `STATUS_NO_TLS_OFFERED`.
6. Otherwise byte 12 is the negotiation type. `0x03` is `RDP_NEG_FAILURE`; read
   the 4-byte little-endian failure code at bytes 16–19 and name it in the
   message → `STATUS_NO_TLS_OFFERED`. `0x02` is `RDP_NEG_RSP`; read the 4-byte
   little-endian selected protocol at bytes 16–19. Anything else →
   `STATUS_NOT_RDP`.
7. Selected `0x01` or `0x02` → return it, TLS starts next. Anything else,
   including `0x00` → `STATUS_NO_TLS_OFFERED`.

**Parse structurally; do not compare the response against a literal.** ADR-0008's
diagram writes the Connection Confirm header as `0e d0 00 00 00 00 02`, while the
raw capture in `docs/architecture/NOTES.md` for the same exchange is
`03 00 00 13 0e d0 00 00 00 00 00 02 0b 08 00 02 00 00 00` — where that seventh
X.224 byte is `00` and the `02` is the first byte of the `RDP_NEG_RSP`. One of
the two is a transcription slip. A byte-for-byte comparison against the ADR would
reject every real response; structural parsing is immune to which of them is
right. Raised under *For the architect* below.

---

## The TLS envelope — deliberately permissive, and it is a decision

ADR-0008: *"Treat the permissive envelope as part of this decision, not as an
option."* `permissive_tls_context()` does exactly this and nothing else:

```python
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.check_hostname = False              # MUST be set before verify_mode
ctx.verify_mode = ssl.CERT_NONE
ctx.minimum_version = ssl.TLSVersion.TLSv1
ctx.set_ciphers("DEFAULT@SECLEVEL=0")
```

- **The order is not cosmetic.** `PROTOCOL_TLS_CLIENT` starts with
  `check_hostname = True`, and Python raises `ValueError` if you set
  `verify_mode = CERT_NONE` while hostname checking is on. Setting them the other
  way round is a crash on every run.
- **`minimum_version` is `TLSv1`, stated as a number** rather than ADR-0008's
  "an explicit low `minimum_version`". Ubuntu's `/etc/ssl/openssl.cnf` sets a
  TLS 1.2 floor for anything that does not say otherwise; saying otherwise is the
  whole point. `maximum_version` is left alone.
- **`set_ciphers("DEFAULT@SECLEVEL=0")`** is what lets a small key or an old
  signature through — the normal case for `xrdp` and `gnome-remote-desktop`
  self-signed certificates.
- **`server_hostname=HOST` is passed unchanged**, so a far end that selects a
  certificate by SNI shows the probe what it will show the client. Python
  suppresses the extension for an address literal rather than raising
  (`NOTES.md`, 2026-09-23).

Why all of this is right and not laziness: the probe is a **gate**, not the
guard. `deny-userconfig` in `/etc/FreeRDP/certificates.json` is what refuses a
certificate. A probe stricter than the client stops a healthy terminal for ever,
which D-020 names as the expensive direction to be wrong in. **Write that reason
into the function's docstring**, because this is the one place in the codebase
where a future reader's instinct to "harden" it would do real damage.

---

## Steps

No repair steps. The file does not exist, so there is nothing to restore first.
Every step is test-first: write the test, watch it fail for the stated reason,
then write the code.

### Step 1 — the test file and the request bytes  [feature]
- **Test first:** `encore-probe-test.py` with one case asserting
  `NEGOTIATION_REQUEST` is exactly the 19 bytes above, as a `bytes` literal
  written out independently in the test. Fails with `ImportError` — which proves
  the test is running the file we mean and not a stale copy.
- **Then:** create `encore-probe.py` with the module docstring (purpose, usage,
  the full exit-status table), the status constants, `ProbeError`, and
  `NEGOTIATION_REQUEST`.
- **Why here:** the constant is the published wire format; it is the one thing in
  the file that is copied from a specification rather than reasoned out, so it
  gets its own test.
- **Behaviour change:** new file, nothing calls it.

### Step 2 — `parse_negotiation_response`  [feature]
- **Test first:** one case per branch, all as `bytes` literals, no sockets:
  the real captured response → `2`; the same with selected `0x01` → `1`;
  selected `0x00` → `ProbeError` with `STATUS_NO_TLS_OFFERED`; an
  `RDP_NEG_FAILURE` carrying `0x05` → `STATUS_NO_TLS_OFFERED` **and** the
  message contains `5`; an 11-byte bare Connection Confirm →
  `STATUS_NO_TLS_OFFERED`; truncated to 10 bytes → `STATUS_NOT_RDP`; first byte
  `0x16` (someone answering TLS directly) → `STATUS_NOT_RDP`; X.224 code not
  `0xD0` → `STATUS_NOT_RDP`; empty `b""` → `STATUS_NOT_RDP`.
- **Then:** the parser, following the seven numbered rules above.
- **Why here:** it is the whole of the protocol knowledge this project owns, and
  it is pure, so it must be provable without a network.
- **Behaviour change:** none observable.

### Step 3 — `fingerprint_sha256`, `require_certificate`, `normalise_expected_fingerprint`  [feature]
- **Test first:**
  - `fingerprint_sha256(b"")` equals the known SHA-256 of the empty string, and
    the result is 64 characters, lower case, `[0-9a-f]` only.
  - a test that generates a throwaway self-signed certificate with
    `openssl req -x509 -newkey rsa:2048 -nodes -subj /CN=probe-test` into a
    `tempfile.TemporaryDirectory`, then asserts `fingerprint_sha256(der)` equals
    what `openssl x509 -noout -fingerprint -sha256` reports for the same file
    after stripping colons and lower-casing. This is the cross-check against the
    tool ADR-0008's fingerprint was originally produced with. Skip the test with
    a clear message if `openssl` is absent.
  - `require_certificate(None)` raises `STATUS_NO_CERTIFICATE`;
    `require_certificate(b"x")` returns `b"x"`.
  - `normalise_expected_fingerprint` accepts upper case, accepts colons, accepts
    surrounding whitespace, and rejects 63 characters, 65 characters and `g`×64
    with `STATUS_USAGE`.
- **Then:** the three functions.
- **Why here:** these are the pure value transforms; the fingerprint form is the
  detail that silently produces a pin that never matches.
- **Behaviour change:** none observable.

### Step 4 — `permissive_tls_context`  [feature]
- **Test first:** assert the returned context has `check_hostname is False`,
  `verify_mode is ssl.CERT_NONE`, `minimum_version is ssl.TLSVersion.TLSv1`, and
  that two calls return two different objects (no shared module-level context).
- **Then:** the function, in the exact order given above, with the "gate, not the
  guard" reason in its docstring.
- **Why here:** it is the one setting whose wrongness is invisible until a real
  terminal stops for ever.
- **Behaviour change:** none observable.

### Step 5 — `fetch_peer_certificate`, against a fake server  [feature]
- **Test first:** a test helper in `encore-probe-test.py` that starts a fake RDP
  server on `127.0.0.1` port `0` in a daemon thread: accept, read 19 bytes, write
  a scripted reply, then optionally `ssl`-wrap the server side with a certificate
  generated for the test. Then:
  - **happy path** — replies with the real captured `RDP_NEG_RSP`, wraps with a
    generated 2048-bit certificate → `fetch_peer_certificate` returns DER whose
    fingerprint equals `openssl`'s for that certificate.
  - **the expensive direction, and this is the most valuable test in the file** —
    the same, with a deliberately weak certificate (`rsa:1024`, `-sha1`) →
    **still succeeds**. If `openssl` on the machine refuses to generate it, skip
    with a message saying which check was not made rather than passing quietly.
  - `RDP_NEG_FAILURE 0x05` → `STATUS_NO_TLS_OFFERED`.
  - accept then close immediately → `STATUS_NOT_RDP`.
  - accept, reply correctly, then close instead of handshaking →
    `STATUS_TLS_FAILED`.
  - accept and never reply, `timeout=0.5` → `STATUS_TIMEOUT`.
  - a port bound and then closed → `STATUS_UNREACHABLE`.
  - host `encore-probe-test.invalid` (the reserved `.invalid` TLD, so no network
    is needed) → `STATUS_DNS`. If the machine's resolver hijacks NXDOMAIN the
    test will report `STATUS_UNREACHABLE`; say so in the failure message so it is
    read as a broken resolver and not a broken probe.
- **Then:** the function. `socket.create_connection((host, port), timeout=timeout)`
  inside a `with`, `sock.settimeout(timeout)`, send, read by framing, parse,
  `permissive_tls_context().wrap_socket(sock, server_hostname=host)`,
  `require_certificate(tls.getpeercert(binary_form=True))`.
- **The exception ordering is a decision, not an implementation detail.**
  `socket.gaierror` and `ConnectionRefusedError` and `TimeoutError` are all
  subclasses of `OSError`; a single `except OSError` collapses the whole taxonomy
  into one status. Catch in this order: `socket.gaierror` → `DNS`;
  `TimeoutError` → `TIMEOUT`; `ssl.SSLError` → `TLS_FAILED`; then `OSError`,
  splitting `ConnectionRefusedError`/`EHOSTUNREACH`/`ENETUNREACH` and everything
  else at connect time to `UNREACHABLE`, and anything during the handshake to
  `TLS_FAILED`. **`ProbeError` must not be caught by any of these** — it is not
  an `OSError`, which is why it is a plain `Exception`.
- **Why here:** this is the only part that touches the network, and it is the
  outermost layer, exactly so the three steps before it needed no network at all.
- **Behaviour change:** none observable.

### Step 6 — `main`, and the output discipline  [feature]
- **Test first:** drive `main(argv)` with `contextlib.redirect_stdout` /
  `redirect_stderr` against the fake server:
  - no `--expect` → returns `0`, stdout is the fingerprint plus one newline and
    nothing else, stderr has exactly one line.
  - `--expect` with the right fingerprint, given upper case and colon-separated →
    returns `0`, stdout is the bare lower-case fingerprint.
  - `--expect` with a wrong-but-valid fingerprint → returns `10`, **stdout is
    empty**, stderr names both fingerprints.
  - `--expect deadbeef` → returns `2`, stdout empty.
  - `--port 0`, `--port 70000`, `--timeout 0` → return `2`.
  - every `ProbeError` status reaches the caller unchanged: the fake-server cases
    from step 5 run through `main` return `6`, `7`, `8`, `5`, `4`, `3`.
  - run twice against the same fake server → identical stdout. This is the
    ticket's repeatability check, and it is cheap here.
  - a host argument beginning with `-`, passed after `--`, is treated as a host.
- **Then:** `main`: argparse with the docstring as its description,
  `normalise_expected_fingerprint` before any network work is done, then
  `fetch_peer_certificate`, `fingerprint_sha256`, compare, print, return a
  status. One `except ProbeError` that writes `error: <message>` to stderr and
  returns `err.status`. Guard the entry point with
  `if __name__ == "__main__": sys.exit(main(sys.argv[1:]))`.
- **Validating `--expect` before connecting is deliberate:** a typo in the pin
  must not spend ten seconds and a TCP connection before being reported.
- **Why here:** `main` is the only place side effects live, so it is the last
  thing written and the only thing that knows about exit statuses.
- **Behaviour change:** the script now works.

### Step 7 — make it reachable and documented  [feature]
- **Test first:** none — these are documentation and a file list. Verify by
  running `./encore-probe.py --help` and reading the table, and by running
  `sh -n encore-push.sh`.
- **Then, three small edits:**
  1. `encore-push.sh`: add `encore-probe.py` to the `FILES` list. Not the test
     file.
  2. `docs/troubleshooting.md`: a new section `## Which certificate is the target
     presenting?` placed immediately before `## The shape of a good debugging
     session here`, giving the one command
     (`python3 ~/encore-probe.py <host>`), saying it needs no credentials, no
     graphical session and no root, and pointing at `--help` as the authority on
     the exit statuses rather than repeating the table.
  3. `docs/tests.md`: a new `Test 10 — does the probe agree with the target?`,
     added to the status table as `Never run`, whose pass condition is that
     against the host ADR-0008 records the probe prints
     `ed47d1c3744afa9ffa86d80f3dfbe7a2be67c34e4b171e5fe5a61fec5ed5ef41`, that a
     second run prints the same, and that `--expect` with that value exits 0
     while `--expect` with a value differing in one character exits 10.
- **Why here:** the ticket requires a human be able to run it and read what
  happened; a script nothing copies to a terminal cannot satisfy that.
- **Behaviour change:** the probe reaches a terminal when `encore-push.sh` runs.

---

## Callers to update

**None.** Nothing in the repository calls this today. The contracts this ticket
touches:

- `encore-push.sh`'s `FILES` list — one caller, itself, updated in step 7.
- `docs/tests.md` and `docs/troubleshooting.md` — read by humans; updated in
  step 7.
- The command-line seam above has **no callers yet**. It gets two in the
  consuming tickets, and it is a new contract, so nothing can break.

---

## Out of scope

The engineer must not touch any of these, however close they look:

- `encore-install.sh` — capturing and confirming the fingerprint (D-029) is a
  separate ticket.
- `encore-kiosk.sh` and `encore-kiosk.service` — the pre-flight and the exit-78
  path (D-028) are a separate ticket, and that one has an unsolved boundary
  problem (below).
- `encore-kiosk.remmina.template` — `cert_ignore=1` at line 46 and
  `ignore-tls-errors=1` at line 107 stay exactly as they are. Removing them
  without a pin in place breaks a working terminal.
- `/etc/FreeRDP/certificates.json` — nothing in this ticket writes, reads or
  mentions a pin file.
- `remmina.pref` and `trust_all` — a real problem, a different ticket.
- `encore-uninstall.sh` — nothing is installed by this ticket, so nothing is
  removed.
- The `while true` loop in `encore-kiosk.sh` — ADR-0007 says it goes; not here.
- No new package, no new import beyond the five named above, and no `subprocess`
  in `encore-probe.py`. `subprocess` in the **test** file, to drive `openssl`, is
  fine and expected.

---

## Stop and escalate if

- **`--expect` is wanted for more than one fingerprint.** Rotation of the target's
  certificate is a real thing and the argument above allows exactly one value.
  Widening it is a product decision about what D-028 promises.
- **The negotiation needs a cookie or routing token.** Some far ends want
  `Cookie: mstshash=...` in the Connection Request. None we have met does. If one
  does, it means the 19 bytes are not the whole exchange and ADR-0008 needs an
  addendum before any code is written.
- **`set_ciphers("DEFAULT@SECLEVEL=0")` raises on the machine you are on.** It
  means that OpenSSL build will not go that low, and the "probe stricter than the
  client" risk is live and unclosable in our own code. Stop; that is ADR-0008's
  *Revisit when* condition.
- **A live target selects `0x01` rather than `0x02`.** Not a fault — it is a
  supported branch — but it has never been observed, and it should be written
  into `docs/architecture/NOTES.md` when it first is.
- **Any test needs a real RDP host to pass.** Then the seam is in the wrong place.
  Every behaviour above is reachable with the fake server; if one is not, say so
  rather than marking the test as manual.

---

## For the architect — what in ADR-0008 is wrong or underspecified

Five things. None of them blocks this ticket; three block the consuming ones.

1. **The Connection Confirm bytes in the ADR disagree with the capture in
   `NOTES.md` by one byte.** The *Decision* block writes the X.224 CC header as
   `0e d0 00 00 00 00 02`; the raw capture is `... 0e d0 00 00 00 00 00 | 02 0b
   08 00 02 00 00 00`, so the seventh byte is `00` and the `02` belongs to the
   `RDP_NEG_RSP`. This plan sidesteps it by parsing structurally, but the ADR is
   the record and one of the two transcriptions is wrong. **Does not block.**
2. **The runner table has no row for two reachable outcomes.** "Answered, but not
   with RDP" (`7`) and "TLS handshake failed" (`8`) are both physically reachable
   and neither appears in ADR-0008's four-row contract. Which side of D-020 they
   fall on — retry, or stop and say so — is an architecture call, and a wrong
   default in either direction is expensive: retry-for-ever on a permanent fault
   is the harm D-028 exists to stop, and stop-for-ever on a transient one is the
   harm D-020 names as worse. This plan gives them distinct statuses so the
   decision stays open. **Blocks the runner ticket, not this one.**
3. **The port is absent from the whole design, and getting it to the probe
   breaches an existing boundary.** R-5 lets an adopter name a port, Remmina
   carries it inside `server=` in the profile, and `boundaries.md` part 4 says the
   runner **must not know** the host or anything in the profile — it finds a
   profile by glob and never reads it. A pre-flight that knows where to connect
   has to read the profile, which is a boundary change, not an implementation
   detail. **Blocks the runner ticket.**
4. **"An explicit low `minimum_version`" is not a number.** This plan picks
   `ssl.TLSVersion.TLSv1` and records why (Ubuntu's system-wide TLS 1.2 floor).
   Worth an addendum so it is a decision rather than one engineer's choice.
5. **Q-11 is unchanged and now has a concrete cost.** Only one far end has ever
   been spoken to. Statuses `6` and `8` are the two opposite mistakes it could
   produce against `xrdp` or `gnome-remote-desktop`, and Test 10 as written cannot
   tell them apart against a target nobody has. Noted, not solvable here.

**Also for the architect, not for this ticket:** `boundaries.md` gains a seventh
part and `interfaces.md` gains a contract (I-8, the probe's command line) once
this lands. Both are the architect's edits.
