# ADR-0008 — We speak the RDP preamble ourselves, to capture and to classify

- **Date:** 2026-09-23
- **Kind:** one-way door (we now own protocol code; see *Consequences*)

## Context

D-030 rules out installing a second remote desktop client to capture the
target's certificate at setup. D-029 requires setup to show the administrator a
fingerprint. D-028 requires the terminal to *stop* on a certificate mismatch,
with the reason readable over `journalctl`, and D-026 makes anything the
terminal cannot classify retry for ever — so classification is not optional.

The previous plan for both jobs was `xfreerdp3` from `freerdp3-x11`: for
capture at setup, and as a runtime pre-flight whose exit code told a refused
certificate (143) from an unreachable machine (139/140/141). D-030 removes that
binary, and with it the only channel the runner had. Remmina's own exit carries
no failure taxonomy (ADR-0007, consequence 5); the alternative left was matching
a libfreerdp log string, which D-024 makes a moving target and which the
"HOST IDENTIFICATION HAS CHANGED" banner printed on a *successful* first accept
makes actively dangerous.

RDP does not begin with TLS. MS-RDPBCGR requires a TPKT-framed X.224 Connection
Request carrying an `RDP_NEG_REQ`, and a Connection Confirm carrying an
`RDP_NEG_RSP`, before the TLS handshake starts. That is why `openssl s_client`
cannot reach the certificate, and it is the whole of what we have to implement.

## Options

**A — Our own probe, in Python 3 from the base system.** Nineteen bytes out,
nineteen bytes in, then hand the same socket to `ssl`. Forever cost: we own a
piece of wire protocol and every bug in it; nothing warns us when a far end
stops behaving as tested; we own a second TLS client whose acceptance envelope
must be kept no stricter than the one the real client uses.

**B — `freerdp3-x11` for both jobs.** Forever cost: an X11 client permanently
on a Wayland-only machine, a package the uninstaller must remove, an exit-code
contract with an upstream project, and a dependency on the component most
likely to be replaced. Rejected by the author as D-030.

**C — Capture ours, classify from the client's log text.** Forever cost: a
string contract with libfreerdp, re-verified on every upgrade, with a known
trap (the banner above) that produces exactly the wrong answer. Rejected: it is
strictly worse than A on the job A already does.

## Decision

**One piece of our own code does both jobs: at setup it captures, and at every
launch the runner runs it as a pre-flight and classifies on its result.**

The choice was decided by a single fact: classification has to be *ours*. Every
borrowed channel — an exit code, a log line — belongs to a component this
project has already decided it may replace, and D-028 cannot rest on that. Once
we own the probe for capture, classification is the same code called twice.

The exchange, verified end to end (see *Source* in `NOTES.md`):

```
-> TPKT 03 00 00 13 | X.224 CR 0e e0 00 00 00 00 00
   | RDP_NEG_REQ 01 00 08 00  03 00 00 00      requestedProtocols = SSL|HYBRID
<- TPKT 03 00 00 13 | X.224 CC 0e d0 00 00 00 00 00
   | RDP_NEG_RSP 02 0b 08 00  02 00 00 00      selectedProtocol  = HYBRID
then: TLS ClientHello on the same socket.
```

**Corrected 2026-09-23.** The Connection Confirm line above read
`0e d0 00 00 00 00 02` when this ADR was written. That was a transcription
slip and it has been fixed in place. The seventh X.224 byte is the class
option, `00`; the `02` is the first byte of the `RDP_NEG_RSP` — its type. The
capture in `NOTES.md` (2026-09-23) reads
`03 00 00 13 | 0e d0 00 00 00 00 00 | 02 0b 08 00 02 00 00 00`, and the
specification agrees: an X.224 CC header is LI, code `0xD0`, DST-REF, SRC-REF,
class option — seven bytes, the last of which is `00` for class 0. The
Connection Request line one line above was always right and has the same shape.
Anyone comparing a real response against the old line byte-for-byte would have
rejected every real response; parse the frame structurally, never as a literal.

Requesting `SSL|HYBRID` is load-bearing. Requesting `SSL` alone against the one
observed target returns `RDP_NEG_FAILURE` `0x05 HYBRID_REQUIRED_BY_SERVER` and
no TLS ever starts. Both `0x01` and `0x02` selections mean TLS next; only
`0x00` (plain RDP security) means there is no certificate to see.

No credentials are needed: the certificate is on the wire before CredSSP runs.

**Pinning is still enforced by FreeRDP, not by the probe.** The probe decides
*what to say*; `/etc/FreeRDP/certificates.json` (`certificate-db` +
`deny-userconfig`) decides *what is allowed*. Two connections are involved, so
the probe is a gate and not the guard — keeping the guard where no client can
opt out of it is what stops the probe becoming security theatre.

**Runner contract**, on top of ADR-0007's exit 78:

| Probe outcome | Runner |
|---|---|
| DNS failure, refused, unreachable, timeout | exit non-78 — systemd retries (D-026) |
| `RDP_NEG_FAILURE`, or selected protocol `0x00` | journal line, exit 78 — stop |
| TLS reached, fingerprint ≠ pin | journal line naming both, exit 78 — stop |
| TLS reached, fingerprint = pin | launch the client as today |

**This table was incomplete. Two rows were added by the first addendum of
2026-09-23 below, along with the rule that decides which side any future
outcome falls on, and the remaining four by the second. The three tables
together are the contract; this one alone is not.**

The fingerprint is `sha256` over the DER certificate, lower-case hex, no
colons — the exact form `certificate-db` compares with `_stricmp`.

## Consequences

Easier: D-028 is satisfied without any contract with an upstream project;
the wording of the journal line is ours; setup can show the fingerprint for
D-029 from the same code; a pinned terminal that a probe cannot even reach
stops before the client draws anything, so C-2 is not exercised on this path.

Harder: we own protocol code. The probe is a second TLS client on the machine,
and if its acceptance envelope is *stricter* than the real client's — OpenSSL
security level, minimum TLS version, SNI — it will stop a terminal that would
have connected fine. That is a false "configuration is broken", which D-020
names as the more expensive direction to get wrong.

No longer possible: classifying on a FreeRDP exit code, since no FreeRDP client
binary is on the terminal.

## Addendum, 2026-09-23 — option D was examined and rejected: bind to the installed libfreerdp

The author asked whether the library already on every terminal could be driven
directly instead, since that adds no package. It was investigated against the
Ubuntu archive and the FreeRDP headers, not reasoned from the source tree. The
decision above is unchanged; the reasoning is now on file.

**What is there.** `remmina-plugin-rdp` installs one plugin object and pulls
`libfreerdp3-3`, `libfreerdp-client3-3`, `libwinpr3-3`. That is
`libfreerdp3.so.3` and nothing else — no headers (`freerdp3-dev` is a separate
package), no `.so` symlink, no executable.

**No headless way in exists.** Of 24 binary packages built from `freerdp3`,
three carry a client: `freerdp-x11`, `freerdp-sdl`, and `freerdp-wayland`
(`wlfreerdp`, which still needs a running compositor). `winpr-utils` is
`winpr-hash` and `winpr-makecert`; the rest are servers and libraries. So the
only routes are a graphical client package — which D-030 rules out — or the
library itself.

**D — drive `libfreerdp3.so.3` from Python `ctypes`.** Feasible and nameable:
`freerdp_new`, `freerdp_context_new`, `instance->VerifyCertificateEx`,
`freerdp_settings_set_string(… FreeRDP_ServerHostname …)`, `freerdp_connect`,
`freerdp_get_last_error`. The certificate reaches the callback during TLS,
before NLA, so no credentials are needed. The API is genuinely public and
ABI-held: `struct rdp_freerdp` uses `ALIGN64` numbered slots with reserved
padding, and FreeRDP 3 made settings opaque behind accessors for exactly this.

Rejected on three counts.

1. **It is not reuse of an implementation; it is a hand-written binding to a C
   ABI.** With no headers on the terminal and no compiler in the path, every
   struct slot, settings enum id, error code and callback prototype becomes a
   hardcoded constant in our file. That is more undocumented magic than the
   nineteen bytes, and it is magic about a private ABI rather than a published
   wire format.
2. **Its failure mode is a segfault, and a segfault takes the wrong branch.**
   A wrong constant under `ctypes` is a wild pointer, not an exception. In the
   runner's pre-flight that exits non-78, which ADR-0007 turns into indefinite
   retry — the precise outcome D-028 exists to prevent. The probe's failure
   mode is bytes that do not parse, and we choose what that means.
3. **The borrowed side is the one that moves.** MS-RDPBCGR's preamble is frozen
   by specification. `libfreerdp3.so.3` is not: a FreeRDP 4 is a new soname with
   slots and enum ids free to move, and D-024 gives us no compatibility handling
   and no warning. The usual argument for reusing an implementation — it absorbs
   change for you — is inverted in this particular case.

**Its one real advantage is conceded, and bought elsewhere.** Binding would give
the probe the client's own TLS acceptance envelope, removing the *Consequences*
risk above that a stricter probe stops a healthy terminal. That risk is closed
in our own code — `check_hostname=False`, `verify_mode=CERT_NONE`, a cipher
string meeting the property below, and an explicit low `minimum_version` — and
doing so is correct on its own terms, because the probe is a gate and
`deny-userconfig` is the guard. The probe has no business judging TLS strength;
it only needs to see the certificate. **Treat the permissive envelope as part of
this decision, not as an option.**

> **Correction, 2026-09-23.** This paragraph named
> `set_ciphers("DEFAULT@SECLEVEL=0")`. That string is wrong and has been
> removed. Measured on Python 3.14.7 / OpenSSL 3.5.7, Python's default cipher
> list for `PROTOCOL_TLS_CLIENT` is *not* OpenSSL's `DEFAULT`, so the call
> lowers the security level as intended **and drops ten suites the untouched
> context offers**, the whole AES-CCM family among them — it narrows the
> envelope it was chosen to widen. A far end offering only a CCM suite would
> have been classified a TLS failure while the real client connects to it
> happily: the false "this configuration is broken" that this very addendum
> claims to buy off, and D-020's expensive direction. The shipped probe uses
> `ALL:!aNULL@SECLEVEL=0` — 129 suites against the untouched context's 61, a
> strict superset, at security level 0. `!aNULL` is independently load-bearing:
> `ALL` alone admits anonymous suites, and with `verify_mode=CERT_NONE` a far
> end selecting one completes a handshake presenting no certificate, which the
> probe would report as "no certificate" for a healthy target.

**The envelope is a property, not a literal.** A cipher string is
OpenSSL-build-dependent, and the one this ADR first recorded was already wrong
on the first build it met. What this decision requires is:

> **No suite the untouched client context offers may be absent, and no
> unauthenticated suite may be present.** Equivalently: never stricter than the
> client it precedes, and never accepting a handshake that presents no
> certificate.

Whichever string satisfies that on the build in hand is the right string.
The property is verified against Python's own default client context
(`ssl.SSLContext(PROTOCOL_TLS_CLIENT).get_ciphers()`) as a proxy for the real
client's offer list — the real client is Remmina's FreeRDP plugin, which cannot
be interrogated without a terminal, so this is the strongest check that can be
run locally, and it is a proxy rather than the thing itself.

**Classification (D-028) is unaffected.** Binding would offer
`freerdp_get_last_error` as a typed taxonomy, which is better than a log string
but is still a contract with the component this project expects to replace —
the same reason that decided against option C. The probe answers the same four
cases without one.

## Addendum, 2026-09-23 — the runner contract is completed, and the TLS floor is a number

Three gaps were found while the probe was being designed. All three are closed
here; the decision above is unchanged.

**1. `minimum_version` is TLS 1.0.** The text above says "an explicit low
`minimum_version`" without a number, which left it to whoever wrote the code.
It is `ssl.TLSVersion.TLSv1`. Ubuntu's `/etc/ssl/openssl.cnf` imposes a TLS 1.2
floor on anything that does not say otherwise, and saying otherwise is the
entire purpose of the permissive envelope: a probe stricter than the client
stops a healthy terminal for ever, which D-020 names as the expensive direction
to be wrong in. This is the same reasoning as `SECLEVEL=0`, applied to the
version rather than to the cipher, so it is part of the same decision and not a
separate one. `maximum_version` is deliberately left alone.

**2. Two reachable outcomes had no row.** The four-row table above covers
neither "something answered, but it did not speak the RDP preamble" nor "the
negotiation succeeded and the TLS handshake did not". Both are reachable, and
under ADR-0007 anything unclassified exits non-78 and retries for ever — the
harm D-028 exists to prevent — so leaving them out was itself a decision, and
the wrong one. The rule that settles them:

> **Stop when the evidence is about the target and retrying cannot change it.
> Retry when the failure could be ours, or transient.**

| Probe outcome | Runner | Why this side |
|---|---|---|
| answered, but not the RDP preamble | journal line, exit 78 — **stop** | The address names something that is not an RDP service. Wrong host, wrong port, or a middlebox in the way. No number of retries converts it, and it is repairable in two minutes by the person who typed the address — D-020's `invalid configuration` branch exactly. |
| negotiation succeeded, TLS handshake failed | exit non-78 — **retry** | The far end has already *proved* it speaks RDP, so this is not a wrong address. The plausible causes are our own envelope being too strict, or the target restarting mid-handshake. ADR-0008's own *Consequences* name the first as the expensive mistake; retrying is the cheap direction while only one far end has ever been spoken to (Q-11). |

The probe itself classifies but never decides: it returns distinct statuses and
uses 78 for nothing. Mapping them onto D-020's two branches is this ADR's job,
and the table above is the whole of it.

**3. What each side costs, recorded rather than assumed.** Stopping on "not
RDP" means a bug in our own frame parser would stop healthy terminals
permanently; that parser is pure and is the one part of the probe proved
without a network, which is what makes the risk acceptable. Retrying on a
failed handshake means a *permanently* broken far-end TLS configuration hides
behind an ordinary outage for ever — the one place this addendum knowingly
leaves D-028's harm in place. It is logged as debt rather than designed away,
because the alternative is stopping terminals on our own strictness.

**Q-11 lands directly on this table.** Every observation of the preamble is
against the one host the author runs; `xrdp` and `gnome-remote-desktop` have
never been probed. The two statuses an unseen target could produce wrongly are
opposite in cost: "no TLS offered" stops for ever and "TLS handshake failed"
retries for ever, and nothing testable locally tells a genuine instance of
either from a mistake by us. Anyone designing the runner's pre-flight is
choosing between those two harms with one data point, and should know it.

## Addendum, 2026-09-23 — the runner contract is completed against the probe's actual statuses

The two tables above were written before the probe existed. The shipped probe
defines ten statuses (`encore-probe.py` module docstring), and three of them —
`2 USAGE`, `5 TIMEOUT`, `9 NO_CERTIFICATE` — had no row on either side. A
fourth case, exit `1`, is not a probe status at all and had no row either.
Anything unmapped exits non-78 by default and retries for ever, which is the
harm D-028 exists to prevent, so the omission was a decision by accident. The
rule is unchanged and decides all four:

> **Stop when the evidence is about the target and retrying cannot change it.
> Retry when the failure could be ours, or transient.**

| Probe status | Runner | Why this side, and what it costs |
|---|---|---|
| `2 USAGE` | journal line, exit 78 — **stop** | The arguments are wrong, and the reachable cause in production is a malformed `RDP_HOST=` in the install record (ADR-0009, I-7): an empty label from a doubled dot, a label over 63 characters, a `--timeout` a socket cannot hold. The probe returns this precisely *because* no later lookup can make the address valid — it is a structural fact about the input, not a lookup that failed today. **Cost:** a bug in our own argument handling, or a Python that reports a malformed name differently from the one measured (see C-1's Python floor), stops a healthy terminal for ever. The offsetting fact is that this status is decided before any packet leaves the machine, so it is provable without a network — the same property that made "not RDP" acceptable to stop on. |
| `5 TIMEOUT` | exit non-78 — **retry** | The first table already said "timeout" in prose; this states it against the status number so nobody has to match wording to a code. The target did not answer in time, which is the textbook transient: a machine still booting, a saturated link, a firewall dropping rather than refusing. **Cost:** a target that is permanently silent — filtered by a firewall that will never be opened — is indistinguishable from one that is briefly slow, so it is retried for ever. That is accepted: the alternative stops a terminal whose server simply had not finished booting, which is D-020's expensive direction and the single most likely first-morning failure. |
| `9 NO_CERTIFICATE` | journal line, exit 78 — **stop** | TLS completed and the far end presented nothing. There is nothing to pin, so the pinned connection that follows cannot succeed either; retrying cannot produce a certificate that was not offered. **Cost, and it is the largest on this table:** this rests on the probe never itself being the reason nothing was presented. One known way to cause that is already closed — `!aNULL` in the cipher string, because an anonymous suite completes a handshake with no certificate and `verify_mode=CERT_NONE` would accept it (see the correction above). What is *not* closed is Q-11: this is one of the two opposite mistakes an unprobed `xrdp` or `gnome-remote-desktop` could produce, the other being `8 TLS_FAILED`, and nothing testable locally tells a genuine instance from a mistake of ours. We have put one on the stop side and one on the retry side with one data point, deliberately, and D-A15 records the retry half of that bet. |
| exit `1` — not a status | exit non-78 — **retry** | The probe leaves `1` unassigned so that a crash can never be read as a classification, which means the runner must decide what a crash means. It is evidence about *us*, not about the target, so the rule puts it on the retry side. **Cost:** a deterministic crash — a wrong assumption in our own code, met on every run — retries for ever and carries no classification with it. Accepted because the alternative permanently stops a terminal whose server is fine for a fault that may be transient (memory, file descriptors), and because the journal line plus the traceback on stderr is a louder signal than a silent stop. This is the same shape as D-A15 and is recorded with it. |

With these, every one of the probe's ten statuses has a side: `0` launches the
client; `3`, `4`, `5`, `8` and a crash retry; `2`, `6`, `7`, `9`, `10` stop.
Nothing falls through to the default any more. **A new probe status is
therefore a change to this ADR, not only to the probe.**

## Revisit when

A far end answers with `RDP_NEG_FAILURE` or selects protocol `0x00` on a
deployment we care about, or a probe refuses a handshake the real client
completes. Either means the probe's envelope, not the decision, is wrong.
