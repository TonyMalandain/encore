# NOTES — append-only working log

Never rewrite past entries. One fact per entry. Restructure when this passes
150 lines or 25 entries, or when asked.

Entries are removed only by a fold into a formal document. What is left here is
what is not yet settled.

**Folded 2026-09-13.** The sixteen findings that stood above this line were
folded into `debt.md`, `data.md`, `interfaces.md`, `overview.md`, `00-index.md`
and ADR-0006, and removed from here. Where two of them disagreed, both sides
were written into the "Open contradictions" section of `00-index.md` rather
than resolved. The open questions below were **not** folded — they are
unanswered and stay here verbatim.

---

# Open questions — a human must answer these

## 2026-09-13 — Q-1: does R-6 win over R-10 at the virtual consoles?
- **Kind:** question
- **Fact:** Consoles 1–6 remain text logins while the kiosk holds tty7, so the person at the terminal can press `Ctrl+Alt+F2` and leave the remote session; the same mechanism is how the administrator gets in without a screen.
- **Why:** Both reasons still hold, so this is a genuine Conflict and the architect must not pick. Disabling VT switching hardens R-6 and makes R-10 depend wholly on the network, which is the lock-out cost D-006 already accepted — accepting it twice is a different weight.
- **Source:** `remmina-kiosk.service:19-20`; D-006, R-6, R-10
- **Touches:** constraints.md, and a future ADR

## 2026-09-13 — Q-2: what is R-14 actually promising, given no store can deliver it?
- **Kind:** question
- **Fact:** On an unattended headless terminal there is nobody to unlock a keyring at boot, so libsecret moves the secret rather than protecting it; full-disk encryption pushes the cost to the adopter and sits badly with "no particular hardware".
- **Why:** The likely honest answer is to narrow what the credential can reach on the far host and say plainly what it does not protect against — but that changes what R-14 promises a reader, which is the product manager's call, not the architect's.
- **Source:** the analysis in `data.md`
- **Touches:** a future ADR; possibly `docs/product/solution.md` R-14

## 2026-09-13 — Q-3: why not Remmina's own kiosk edition? — CLOSED same day
- **Kind:** question
- **Fact:** Remmina ships `remmina-gnome`, a kiosk session integrated with a display manager, which is close to what the unit file and script reimplement by hand. The record does not say whether it was considered.
- **Why:** "No code" beats "boring code". If it does the job, most of `remmina-kiosk.service` and all of `remmina-kiosk.sh` are unnecessary — and every one of items D-A2, D-A4 and D-A6 in `debt.md` goes away with them. If it does not, the reason belongs in ADR-0001 so it is never asked again.
- **Source:** [Remmina Kiosk Edition](https://remmina.org/remmina-kiosk-edition/)
- **Touches:** stack.md, ADR-0001
- **CLOSED 2026-09-13:** ruled out on a hard constraint. `remmina-gnome` is an X11 session (`remmina-gnome-xsession.desktop`, launching `gnome-session`) and D-003 fixes the display server as Wayland. Liveness turned out to be the wrong question — it is stagnant but not removed, and the X11 dependency decides it either way. Folded into `stack.md`.

## 2026-09-13 — Q-5: if a terminal is silently failing, is anyone owed a signal?
- **Kind:** question
- **Fact:** Raised by the product manager as Q-P3, drawn out of item D-A2. The product record is silent on whether an administrator should learn that a terminal has stopped working, and silence is not an answer either way.
- **Why:** It decides the shape of the D-A2 fix. If nobody is owed a signal, letting systemd mark the unit failed is enough and the work is small. If the administrator is owed one, something must reach them on a machine with no screen, which is a notification path this product does not have and which brushes against "not a manager of the terminal". The product answer must come first; I should not build a notifier nobody asked for, nor quietly assume a failed unit counts as telling someone.
- **Source:** product manager report, 2026-09-13; D-015, D-012
- **Touches:** debt.md D-A2, BACKLOG.md

## 2026-09-13 — Q-4: is `kiosk.target` too generic a name to publish?
- **Kind:** question
- **Fact:** The target name becomes public the moment a stranger reads an instruction containing it, and it is generic enough to collide with another package on the same machine.
- **Why:** Namespacing it costs nothing today and is impossible after publication. This is the cheapest one-way door on the list.
- **Source:** `kiosk.target`; ADR-0003
- **Touches:** ADR-0003, interfaces.md I-1

---

# 2026-09-14 — recovery and restart

## 2026-09-14 — systemd can do increasing backoff, since v254
- **Kind:** stack
- **Fact:** `RestartSec=` + `RestartSteps=` + `RestartMaxDelaySec=` give a geometric (exponential) restart delay natively; both of the latter two were added in systemd 254. There is no jitter, no per-failure-kind curve, and no way to reset the delay from inside the service except `RESTART_RESET=1` over `sd_notify` (v257+).
- **Why:** The author's question was whether systemd can do this at all. It can, and knowing the version it arrived in turns it from a capability into a declared prerequisite under D-024.
- **Source:** `systemd.service(5)`, systemd 259, read 2026-09-14
- **Touches:** constraints.md C-1, stack.md, ADR-0007

## 2026-09-14 — systemd's restart backoff never decays on its own
- **Kind:** constraint
- **Fact:** The restart counter is flushed only when a start is not an auto-restart — a manual `start`/`restart`, a `reset-failed`, or a reboot. Time spent running successfully does not reset it, so a terminal that reconnects many times over months ends up waiting the full cap on every subsequent reconnect.
- **Why:** This is the whole argument for keeping `RestartMaxDelaySec=` small. A generous cap looks prudent and quietly becomes the steady-state wait a child sits through after every drop.
- **Source:** systemd `src/core/service.c:3623-3625` and `:6073`, read 2026-09-14
- **Touches:** ADR-0007, constraints.md C-6

## 2026-09-14 — cage returns its child's exit status as its own
- **Kind:** interface
- **Fact:** When the child exits, cage's `SIGCHLD` handler sets `return_app_code` and `main` returns the child's status, so an exit code written by the runner reaches systemd through the compositor unchanged.
- **Why:** It is the load-bearing fact under the whole exit-code scheme. Without it the compositor would swallow the distinction between "configuration is broken" and "machine is unreachable", and D-020 could not be expressed mechanically at all.
- **Source:** `cage.c:199-213`, `cage.c:722-726` (upstream master), read 2026-09-14
- **Touches:** interfaces.md, ADR-0007

## 2026-09-14 — `ExecStopPost=chvt 1` becomes a kiosk breach once the unit really restarts
- **Kind:** debt
- **Fact:** `encore-kiosk.service:18` flips the foreground console to tty1 on every stop; today the loop means it never fires on a dropped connection, but under ADR-0007 every reconnect would show the person at the terminal a text login prompt for the length of the backoff delay.
- **Why:** It is a fault the fix would create, not one it would find — exactly the kind that gets blamed on the wrong change later. It has to move to the deactivation path in the same edit that removes the loop.
- **Source:** `encore-kiosk.service:18`; C-2
- **Touches:** debt.md D-A2, ADR-0007

## 2026-09-14 — Q-6: the author cites D-009 as the basis for retrying for ever, and the record does not support that
- **Kind:** for-product
- **Fact:** The author's framing is that retrying indefinitely was decided because the target machine is always on, attributed to D-009. In `docs/product/decisions.md`, D-009 is about audio belonging to the terminal, and no decision anywhere in the product record states that the target machine is always on. D-020 does require indefinite retry, but its stated reason is different: retrying fixes an unreachable machine and cannot fix a broken configuration.
- **Why:** If "the target is always on" is a real premise the product is relying on, it is load-bearing and unwritten — it decides whether an overnight outage is a fault or a normal Tuesday, and it is the difference between a backoff cap of thirty seconds and one of five minutes. If it is a misremembered ID, the record is fine and only the reference is wrong. Either way the architect must not settle it.
- **Source:** the author via the coordinator, 2026-09-14; `docs/product/decisions.md` D-009, D-020
- **Touches:** docs/product/decisions.md; ADR-0007's cap

## 2026-09-14 — Q-7: how long may a terminal show a black screen after a dropped connection?
- **Kind:** for-product
- **Fact:** C-6 already records that no such number exists. ADR-0007 has to pick one anyway — thirty seconds, chosen to be small rather than measured — and under ADR-0007 that delay is a black screen in front of the person at the terminal, because the compositor is restarted along with the client.
- **Why:** `docs/product/users.md` names a black screen as a reason the person at the terminal gives up, so the number is a product promise wearing a configuration directive's clothes. The architect can pick a defensible value; only the author can say what is acceptable to a child waiting for their screen to come back.
- **Source:** ADR-0007 consequence 1; constraints.md C-6; `docs/product/users.md`
- **Touches:** constraints.md C-6, docs/product/solution.md R-8

---

# 2026-09-23 — the record was rewritten to match the product that exists

The rename sweep (D-022, D-023), the D-027 packaging corrections, the three
factual errors in `constraints.md`, and the observations of 2026-09-14 and
2026-09-23 were folded directly into `overview.md`, `boundaries.md`,
`interfaces.md`, `constraints.md`, `data.md`, `stack.md`, `debt.md`,
`00-index.md` and ADR-0002, -0003, -0004, -0007 on this date, so they are not
repeated here. Every `file:line` in the record was re-checked against the file
rather than renamed. What is below is only what is **not** settled.

## 2026-09-23 — Q-6 is closed by D-026, and Q-1 is half dissolved
- **Kind:** decision
- **Fact:** D-026 (2026-09-21) states the machine being connected to is available about 99% of the time, which is the premise ADR-0007's cap rests on and which Q-6 found unwritten. Separately, R-10 was reworded on 2026-09-21 to promise only that an administrator can reach a terminal *from another machine*, so R-10 is no longer one of the two sides of Q-1.
- **Why:** Q-6 was a for-product finding and the product answered it; recording the closure here stops it being re-raised. Q-1 stays open but is now R-6 against D-017's own reason, not R-6 against R-10 — a smaller conflict, and the mechanism is one character (`cage -s`, `encore-kiosk.service:17`).
- **Source:** `docs/product/decisions.md` D-026; `docs/product/NOTES.md`, 2026-09-21
- **Touches:** ADR-0007 (addendum written), constraints.md, 00-index.md

## 2026-09-23 — Q-8: the console is wrong on `isolate` and untested on boot
- **Kind:** question
- **Fact:** `systemctl isolate encore-kiosk.target` on a machine already running a desktop did not bring the capability's console to the foreground. Whether a machine that boots straight into `encore-kiosk.target` has the same problem is untested — Test 7 in `docs/tests.md` has never been run.
- **Why:** The two branches lead to different designs and neither is established. If boot is affected too, `ExecStartPre=+/usr/bin/chvt 7` is insufficient and hardcoding tty7 is the wrong shape. If only `isolate` is affected, the lasting activation path is sound and the fault is in switching away from a live session — which is a debugging inconvenience, not a product defect. Recorded as untested with both branches named, because guessing which it is would decide an interface (I-2) on no evidence.
- **Source:** the author, observed; `encore-kiosk.service:16,27-28`; `docs/tests.md` Test 7
- **Touches:** interfaces.md I-2, ADR-0003, docs/tests.md

## 2026-09-23 — the setup password can reach the journal
- **Kind:** for-product
- **Fact:** `encore-install.sh:137-142` passes the connection password on a command line inside a transient unit, so it can be logged; `:173-176` detects this and tells the administrator to rotate the password or clear the journal. Recorded as `debt.md` item D-A12.
- **Why:** R-14 covers the credential at rest on the terminal. Nothing covers the credential during setup, and this leaks it into a place that survives a reboot. The mechanism fix is mine and it is small — pass it on stdin instead of `argv`. What is not mine is whether the product wants to promise anything about the credential during setup at all, which is the same conversation as Q-P2.
- **Source:** `encore-install.sh:72-77,137-142,173-176`
- **Touches:** docs/product/solution.md R-14; debt.md D-A12

## 2026-09-23 — the configuration step shipped without the two decisions it was holding
- **Kind:** for-product
- **Fact:** `debt.md` items D-A5 (what the credential may reach on the far host) and D-A8 (certificate pinning) were both deferred on 2026-09-13 on the stated grounds that they belonged "inside the configuration design". The configuration step is now built (`encore-install.sh`) and neither was decided in it.
- **Why:** The conversation those two were waiting for has already happened. They are not blocked on anything any more and the reason recorded for deferring them is no longer true, so leaving the deferral in place would be filing them behind an event that has passed. Both need the author — D-A5 is what R-14 can honestly promise, D-A8 is what R-16 means — and neither is the architect's to settle.
- **Source:** `debt.md` D-A5, D-A7, D-A8; `encore-install.sh`
- **Touches:** docs/product/solution.md R-14 and R-16; docs/product/NOTES.md Q-P2

---

# 2026-09-23 — certificate pinning: what the parts we ship can actually do

Investigation only. Nothing below is decided and nothing was changed in any
shipped artifact. Every claim is sourced to FreeRDP 3.31.0 source read from
upstream, to Remmina 1.4.43 source read from upstream, or to FreeRDP 3.30.0
installed on the development machine — each entry says which.

## 2026-09-23 — FreeRDP 3 has a system-wide pin that sits below the client
- **Kind:** stack
- **Fact:** `/etc/FreeRDP/certificates.json` is read by `tls_verify_certificate` in **libfreerdp core**, not in the client layer. Four keys, checked in this order: `deny` (hard fail), `ignore` (accept anything), `certificate-db` (an array of `{"type":"sha256","hash":"<hex, no colons>"}` — a match accepts, with no prompt), and `deny-userconfig` (hard fail, and the user is never asked). Any non-zero result sets `allowUserconfig = FALSE`, which skips the per-host store and the client's verify callback entirely.
- **Why:** This is the whole answer to D-A8. It pins a certificate *and* suppresses the dialog, it lives in a file only root can write, and no client that drives libfreerdp can opt out of it. `certificate-db` plus `deny-userconfig: true` is exactly "accept this one certificate, abort on anything else, ask nobody". Note the order: `deny` is evaluated *before* `certificate-db`, so `deny` must not be set.
- **Source:** FreeRDP 3.31.0 `libfreerdp/crypto/tls.c:1642-1745` (`tls_config_check_allowed_hashed`, `tls_config_check_certificate`) and `:1888-1895` (the `allowUserconfig` gate); path construction in `libfreerdp/utils/helpers.c:253-308`; `xfreerdp(1)` "GLOBAL CONFIGURATION (client common)" on FreeRDP 3.30.0 installed locally.
- **Touches:** debt.md D-A8, interfaces.md (a new contract), stack.md, ADR-0001

## 2026-09-23 — the hash the pin wants is a bare hex SHA-256, case-insensitive
- **Kind:** data
- **Fact:** the `hash` string is compared with `_stricmp` against `freerdp_certificate_get_fingerprint_by_hash_ex(cert, type, FALSE)` — separator `FALSE`, so hex with **no colons**. `openssl x509 -noout -fingerprint -sha256` prints it colon-separated and upper-case; both differences are ours to strip, the case is not.
- **Why:** it is the one detail that silently produces a pin that never matches, and a pin that never matches is a terminal that never connects.
- **Source:** FreeRDP 3.31.0 `libfreerdp/crypto/tls.c:1686-1700`
- **Touches:** debt.md D-A8

## 2026-09-23 — Remmina's profile format cannot carry a pinned identity, and does not need to
- **Kind:** interface
- **Fact:** of the 103 keys in the shipped template, three touch certificates and none pins one. `cert_ignore` sets `FreeRDP_IgnoreCertificate` (`rdp_plugin.c:1951`); `tls-seclevel` sets `FreeRDP_TlsSecLevel`, an OpenSSL cipher-strength level, not a trust decision (`:2106-2110`); `authentication level` sets `FreeRDP_AuthenticationLevel`, where **0 disables the check entirely** (`:1947-1948`, not present in our template). `FreeRDP_CertificateAcceptedFingerprints` — the setting behind `xfreerdp /cert:fingerprint:` — is never set by Remmina.
- **Why:** this is the exact question ADR-0001's live trigger asks. The literal answer is "no, the profile cannot carry it". The trigger does **not** fire, because the pin does not have to live in the profile: `/etc/FreeRDP/certificates.json` is read with `system=TRUE` and is independent of anything Remmina sets. Remmina is a carrier here, not a blocker.
- **Source:** Remmina 1.4.43 `plugins/rdp/rdp_plugin.c:1947-1951,2106-2110`; FreeRDP 3.31.0 `libfreerdp/crypto/tls.c:1798`
- **Touches:** ADR-0001, interfaces.md I-3 and I-6, debt.md D-A8

## 2026-09-23 — `cert_ignore=1` short-circuits above the pin, so it must go for pinning to work
- **Kind:** constraint
- **Fact:** `FreeRDP_IgnoreCertificate` is tested at `tls.c:1831` and returns success immediately — before the store, before the global configuration file, before any callback. While `cert_ignore=1` is in the profile, no pin anywhere on the machine has any effect.
- **Why:** D-A8 warns that `cert_ignore=1` is load-bearing and says "pin first, then remove the ignore". The mechanism says the two cannot be sequenced that way: the pin does nothing until the ignore is gone, so they are one change, not two. What makes that safe is that `deny-userconfig` replaces the dialog the ignore was suppressing.
- **Source:** FreeRDP 3.31.0 `libfreerdp/crypto/tls.c:1831-1839`; `encore-kiosk.remmina.template:46`
- **Touches:** debt.md D-A8, constraints.md C-2

## 2026-09-23 — the per-host trust store is PEM files, not `known_hosts2`, and Remmina moves it
- **Kind:** data
- **Fact:** FreeRDP 3 stores an accepted certificate as `<ConfigPath>/server/<hostname>_<port>.pem`, lower-cased, matched by comparing the stored certificate's fingerprint against the presented one for the same host and port. `known_hosts2` is the FreeRDP 2 file and 3.31 neither reads nor writes it. **Remmina overrides `ConfigPath`** to `<remmina user datadir>/RDP` — so on a terminal it is `/var/lib/encore/.local/share/remmina/RDP/server/` — but only if that directory already exists and is writable, otherwise FreeRDP's default `$HOME/.config/freerdp` is used.
- **Why:** two traps in one fact. The path a pre-seeded PEM must go to depends on a directory existing first, so the location is not deterministic unless the installer creates it. And the store is the mechanism that cannot deliver safe failure: a *match* connects silently, but a *mismatch* calls `VerifyChangedCertificateEx`, which in Remmina is a blocking GTK dialog. The store alone gives pinning and keeps the C-2 breach; combining it with `deny-userconfig` disables the store. They do not compose.
- **Source:** FreeRDP 3.31.0 `libfreerdp/crypto/certificate_store.c:100-206`, `certificate_data.c:86-91,275-296`, `include/freerdp/crypto/certificate_store.h:36-41`; Remmina 1.4.43 `plugins/rdp/rdp_plugin.c:1664-1676,1170-1188,2774-2775`; observed on FreeRDP 3.30.0 locally, where `~/.config/freerdp/server/*.pem` are current and `known_hosts2` was last written under FreeRDP 2.
- **Touches:** data.md, interfaces.md, debt.md D-A8

## 2026-09-23 — the pin overrides the name check rather than adding to it
- **Kind:** constraint
- **Fact:** the global configuration file is consulted only when OpenSSL verification fails *or* the hostname does not match the certificate. A `certificate-db` match then accepts regardless of the name mismatch. Conversely, a certificate that validates against a public CA *and* matches the hostname succeeds before the pin is ever read.
- **Why:** R-16 says "that machine and not something answering to its name". A fingerprint pin delivers that, and it does so by replacing the name test, not by strengthening it. Recorded so nobody later reads the pin as a name check that got stricter. The second half is a floor, not a ceiling: the pin cannot reject a certificate the public trust path already accepted.
- **Source:** FreeRDP 3.31.0 `libfreerdp/crypto/tls.c:1843-1894`
- **Touches:** constraints.md C-4, docs/product/solution.md R-16

## 2026-09-23 — nothing we install can fetch the certificate, and OpenSSL cannot either
- **Kind:** stack
- **Fact:** `remmina-plugin-rdp` brings libfreerdp only; there is no FreeRDP command-line binary on a terminal built by `encore-install.sh:83`. `openssl s_client` has no RDP `-starttls` mode (verified against OpenSSL 3.5.7: the accepted values are smtp, pop3, imap, ftp, xmpp, xmpp-server, telnet, irc, mysql, postgres, lmtp, nntp, sieve, ldap). RDP requires an X.224 connection request and negotiation response before the TLS handshake starts, so a bare TLS client cannot reach the certificate.
- **Why:** capture at install time therefore costs one of: an extra apt package (`freerdp3-x11` ships `/usr/bin/xfreerdp3` on Ubuntu, which gives `/cert:` and a way to print the fingerprint), or roughly thirty lines of our own that speak the X.224 exchange and then hand off to a TLS library. Both are real; neither is free; the choice is a design decision nobody has taken.
- **Source:** `encore-install.sh:83`; the author's observation of 2026-09-23; `openssl s_client -starttls` on the development machine; packages.ubuntu.com for `xfreerdp3`
- **Touches:** stack.md, debt.md D-A8

## 2026-09-23 — Q-9: capturing at install time is trust on first use unless a person checks the fingerprint
- **Kind:** question
- **Fact:** whatever answers on the configured name during the install is what gets pinned. If an impostor is already in position at that moment, the administrator pins the impostor and every check afterwards passes. The only thing that turns this into identity rather than first-use trust is the administrator reading the fingerprint off the target machine itself, out of band, and comparing it.
- **Why:** pinning is worth doing either way — it closes every *later* impostor, which is the risk that recurs on every one of thousands of connections, and it is the one an unattended terminal cannot notice. But the difference between "trust on first use, moved earlier" and "verified identity" is entirely a manual step, and asking for that step sits against R-4's promise that a machine becomes a terminal in minutes. Whether the install demands the comparison, offers it, or says nothing is a product call about what R-16 is worth, not an architecture one.
- **Source:** FreeRDP 3.31.0 `libfreerdp/crypto/tls.c`; D-002 (the target machine is out of scope — reading a thumbprint on it is an instruction, not a change); R-4, R-16
- **Touches:** docs/product/solution.md R-4 and R-16; debt.md D-A8

## 2026-09-23 — Q-10: what a pinned mismatch puts on the terminal's screen has not been seen
- **Kind:** question
- **Fact:** with `deny-userconfig` set, `tls_verify_certificate` returns -1 and the connection fails without any callback being invoked, so the certificate dialog observed on 2026-09-23 cannot appear. What Remmina then draws — a connection-error dialog, a message in its own window, or nothing — is **not established**, under `-c <profile> --enable-fullscreen --disable-toolbar --enable-extra-hardening` inside `cage`.
- **Why:** this is the only part of the mechanism that decides whether pinning fixes C-2 or moves the breach. It is a test, not a reading, and the one time this product's screen was watched it disagreed with every other channel (`00-index.md`, open contradiction 3). Guessing it would be deciding C-2 on no evidence.
- **Source:** FreeRDP 3.31.0 `libfreerdp/crypto/tls.c:1743-1745`; `encore-kiosk.sh:10`; `docs/tests.md`
- **Touches:** constraints.md C-2, debt.md D-A1 and D-A8, docs/tests.md

## 2026-09-23 — telling a pin mismatch from an unreachable machine is cheap at install and dear at runtime
- **Kind:** for-product
- **Fact:** D-020 splits failures into "invalid configuration — stop and say so" and "unreachable machine — retry for ever". A pin mismatch is deterministic, repeatable and unfixable by retrying, and libfreerdp emits a unique line for it (`"[certificates.json] configuration denies user to accept certificates"`) which reaches the journal at the template's `freerdp_log_level=INFO`. But the runner sees only Remmina's exit, which carries no failure taxonomy — so classifying a mismatch at runtime means matching a log string from an upstream project, which D-024 makes a moving target.
- **Why:** the author asked whether the mechanism makes one side of D-020 easier. It does, unevenly: *deciding* that a mismatch is a configuration fault costs nothing, because the pin is part of the configuration by construction. *Detecting* it at runtime, well enough to choose R-17 over R-18, is a fragile string contract we would own. Worth saying which way the cost falls: D-026 makes anything unclassifiable retry for ever, and a pin mismatch retried for ever is a terminal showing nothing indefinitely over a fault a person could repair in two minutes — exactly the harm D-020 exists to prevent.
- **Source:** FreeRDP 3.31.0 `libfreerdp/crypto/tls.c:1743`; `encore-kiosk.remmina.template:113`; D-020, D-024, D-026; R-17, R-18
- **Touches:** docs/product/decisions.md D-020; debt.md D-A2

## 2026-09-23 — pinning makes D-A5's promise smaller and D-A13's harm smaller
- **Kind:** debt
- **Fact:** a pin does not make the stored credential harder to recover, but it removes the remote route that made the local weakness cheap to exploit — after pinning, D-A5's residual exposure is someone holding the machine, and nothing else. Separately, D-A13 allows a second profile to retarget a terminal silently; with a pin and `deny-userconfig`, such a terminal fails to connect instead of sending the credential to the new host.
- **Why:** the record says D-A5, D-A7 and D-A8 are one conversation. D-A5 genuinely is, and pinning is the half of it that can actually be delivered. D-A7 is not, any more — it is largely repaid, and its remainder is D-A13, which pinning mitigates rather than depends on. Worth correcting so the author is not asked to settle three things when two of them are one.
- **Source:** debt.md D-A5, D-A7, D-A8, D-A13; FreeRDP 3.31.0 `libfreerdp/crypto/tls.c:1743-1745`
- **Touches:** debt.md D-A5, D-A8, D-A13

## 2026-09-23 — a pin is a third place the installer guarantees something once
- **Kind:** debt
- **Fact:** `/etc/FreeRDP/certificates.json` sits outside `/var/lib/encore` and outside the profile. It is written once at install, root-owned, and nothing re-checks it — the same shape as D-A13 (installer and runner disagree) and I-7 (the install record). It must also be removed by `encore-uninstall.sh`, or C-3's promise of a clean undo is broken by a file that changes how every RDP client on that machine behaves.
- **Why:** the file is global to the machine, not to the `encore` identity. That is what makes it work — no client can opt out — and it is also what makes leaving it behind a real fault rather than untidiness.
- **Source:** FreeRDP 3.31.0 `libfreerdp/utils/helpers.c:253-296`; `encore-uninstall.sh`; constraints.md C-3; interfaces.md I-7
- **Touches:** constraints.md C-3, interfaces.md, debt.md

## 2026-09-23 — the global configuration path depends on a build flag nobody has checked on a terminal
- **Kind:** question
- **Fact:** `/etc/FreeRDP/certificates.json` is the path only when `freerdp_areApplicationDetailsCustomized()` is false and `FREERDP_USE_VENDOR_PRODUCT_CONFIG_DIR` was not set at build time; otherwise it becomes `/etc/<vendor>/<product>[<version>]/certificates.json`. Verified as `/etc/FreeRDP` on FreeRDP 3.30.0 as Fedora builds it. **Not verified on Ubuntu 26.04**, which is the only distribution a terminal has ever been built on.
- **Why:** if the path differs, a pin written to the wrong file is silently inert and the terminal connects to anything — the failure is invisible and in the unsafe direction. The check is one line of that machine's own `xfreerdp(1)`, or the absence of the expected log line in the journal, and it must be done before anything is written.
- **Source:** FreeRDP 3.31.0 `libfreerdp/utils/helpers.c:220-296`; `xfreerdp(1)` on FreeRDP 3.30.0, development machine
- **Touches:** stack.md, debt.md D-A8, docs/tests.md

## 2026-09-23 — second reading of the same source agreed, and corrected one hedge
- **Kind:** stack
- **Fact:** an independent read of the FreeRDP 3.31.0 and Remmina 1.4.43 trees reached the same conclusions on the order of checks in `tls_verify_certificate`, on `cert_ignore` being nothing but `/cert:ignore`, on the absence of any fingerprint key in the profile format, and on the store being PEM files rather than `known_hosts2`. It corrected one hedge: **nothing in Remmina ever creates `<datadir>/RDP`**, so the `access(..., W_OK)` test at `rdp_plugin.c:1673` always fails on a normal install and `ConfigPath` stays at FreeRDP's default. In practice the store is `$HOME/.config/freerdp/server/` — `/var/lib/encore/.config/freerdp/server/` on a terminal — and it stays there unless somebody creates that `RDP` directory, at which point the whole store silently moves and anything seeded is ignored.
- **Why:** the earlier entry left the path conditional, which would have sent an installer looking in two places. It is one place, with a trip-wire beside it.
- **Source:** FreeRDP 3.31.0 `libfreerdp/crypto/tls.c`, `certificate_store.c`, `certificate_data.c`, `utils/helpers.c`; Remmina 1.4.43 `plugins/rdp/rdp_plugin.c:1663-1676`, `src/remmina_file_manager.c:60-142`; store layout observed on two live Remmina installations
- **Touches:** data.md, debt.md D-A8

## 2026-09-23 — `trust_all` is a second blanket bypass, and it lives in a file we generate
- **Kind:** debt
- **Fact:** `remmina.pref` carries a global boolean `trust_all` (`src/remmina_pref.c:359-362`, `:958`), checked in `remmina_protocol_widget_panel_new_certificate` and `..._changed_certificate` (`src/remmina_protocol_widget.c:1857-1868`, `:1895`). When true, every certificate is accepted **including a changed one**, so it is weaker than FreeRDP's own trust-on-first-use. Its default is false. `/var/lib/encore/.config/remmina/remmina.pref` is generated on the terminal by `encore-install.sh:137-142` and nothing in our record has ever looked at what it contains beyond `secret=`.
- **Why:** we ship a file we do not read. A pin defeated by a preference in a file the installer created and never inspected is the same failure as the template silently losing `cert_ignore`, and it would be just as invisible. Whatever pinning is built has to assert this key, not assume it.
- **Source:** Remmina 1.4.43 `src/remmina_pref.c:359-362,958`, `src/remmina_protocol_widget.c:1857-1868,1895`; `encore-install.sh:137-149`
- **Touches:** debt.md, data.md, interfaces.md

## 2026-09-23 — a non-default RDP port changes the store filename twice over
- **Kind:** data
- **Fact:** Remmina sets `FreeRDP_CertificateName` to the bare host when the port is 3389 and to `host:port` otherwise (`rdp_plugin.c:431-443`); `tls.c` then uses `CertificateName` as the store key, and `ensure_valid_charset` maps `:` to `.` — so a terminal pointed at port 3390 looks for `host.3390_3390.pem`. Derived from source, **not observed**; no non-3389 example exists on any machine checked.
- **Why:** R-5 lets an adopter name any machine, and nothing stops them naming a port. Recorded as inference so that if pre-seeding the store is ever chosen, the non-default-port case is tested rather than assumed. The system-wide fingerprint pin has no filename and is not affected.
- **Source:** Remmina 1.4.43 `plugins/rdp/rdp_plugin.c:431-443`; FreeRDP 3.31.0 `libfreerdp/crypto/certificate_data.c:64-91`
- **Touches:** data.md, debt.md D-A8

## 2026-09-23 — FreeRDP's trust-on-first-use path exists, is fully non-interactive, and needs no display
- **Kind:** stack
- **Fact:** `/cert:tofu` sets `FreeRDP_AutoAcceptCertificate` (`client/common/cmdline.c:3530-3532`). In `tls_verify_certificate`, when no stored entry matches, `if (settings->AutoAcceptCertificate)` accepts at `tls.c:1941-1944` **before** `instance->VerifyCertificateEx` is ever reached (`:1976`), and `accept_certificate == 1` writes the store entry at `:2084-2090`. No stdin is read and no callback fires, so no GTK dialog and no terminal prompt is possible on this path. `+auth-only` makes the X11 client skip the display entirely — observed log line `[xf_pre_connect]: Authentication only. Don't connect to X.` with `DISPLAY` and `WAYLAND_DISPLAY` unset.
- **Why:** this is the answer to "can we drive it". It can be driven by a shell script over SSH with no session of any kind, which is exactly the shape setup has.
- **Source:** FreeRDP 3.31.0 `client/common/cmdline.c:3515-3532`, `libfreerdp/crypto/tls.c:1896-1949,2084-2090`; run against a live RDP host on FreeRDP 3.30.0 locally, `xfreerdp /v:<host> /cert:tofu /u:x /p:x +auth-only` with a scratch `HOME`, repeated three times, PEM written every time
- **Touches:** stack.md, interfaces.md, debt.md D-A8

## 2026-09-23 — capture needs no valid credentials, because TLS precedes NLA
- **Kind:** interface
- **Fact:** the certificate is verified and stored during the TLS handshake, before NLA authentication runs. A capture run with deliberately wrong credentials writes the PEM and then fails authentication: observed `XF_EXIT_LOGON_FAILURE` (134) with `/u:x /p:x`, PEM present on disk.
- **Why:** it means the capture step does not have to hold the RDP password, so it can run before the credential is collected and cannot leak it. It also means the capture cannot be confused by a wrong password — the two failures are separate exit codes.
- **Source:** observed, FreeRDP 3.30.0, three repetitions; `client/X11/xfreerdp.h:339-390` for the code names
- **Touches:** interfaces.md, data.md

## 2026-09-23 — the stored PEM yields the pin's hash with stock `openssl`, exactly
- **Kind:** data
- **Fact:** the store file is a single plain `-----BEGIN CERTIFICATE-----` block. `openssl x509 -in <pem> -noout -fingerprint -sha256 | sed 's/.*=//; s/://g' | tr 'A-Z' 'a-z'` produced `ed47d1c3…ef41`, byte-identical to the fingerprint FreeRDP itself printed for the same certificate. `openssl` is in the Ubuntu base system; nothing new is needed to read it back.
- **Why:** closes the "colon-free hex" trap recorded on 2026-09-23 with a verified command rather than an inference.
- **Source:** observed locally against the PEM written by `/cert:tofu`; hash form required by `libfreerdp/crypto/tls.c:1642-1700`
- **Touches:** data.md, interfaces.md

## 2026-09-23 — no client binary on a terminal can drive the first-use path, so capture costs one package
- **Kind:** stack
- **Fact:** the first-use path lives in libfreerdp but only a *client* can turn it on. On a terminal the only client is Remmina, whose verify callback is a GTK dialog and which cannot run without a graphical session; `trust_all` in `remmina.pref` bypasses the dialog but is weaker still and remains a display-bound path. The headless driver is a FreeRDP command-line client, which on Ubuntu is `/usr/bin/xfreerdp3` from **`freerdp3-x11`** (package page present for the 26.04 suite). The binary is ~0.8 MB; its shared-library dependencies are libfreerdp/libwinpr, already installed by `remmina-plugin-rdp`, plus X11 client libraries, most of which Remmina's GTK stack already pulls (`assumed` for the exact Ubuntu dependency delta).
- **Why:** the author's hypothesis — drive Remmina's own first-use path — does not survive the no-display requirement. The mechanism is right, the driver is not on the machine. One extra apt package is the whole cost, and `encore-install.sh:83` already runs `apt-get install`.
- **Source:** FreeRDP 3.31.0 `libfreerdp/crypto/tls.c:1976` (client callback), Remmina 1.4.43 `src/remmina_protocol_widget.c:1857-1895`; `packages.ubuntu.com` contents search, `xfreerdp3` → `freerdp3-x11`; local binary size on Fedora
- **Touches:** stack.md, debt.md D-A8

## 2026-09-23 — FreeRDP exit codes classify a certificate refusal without matching any log string
- **Kind:** interface
- **Fact:** `client/X11/xfreerdp.h:339-390` is a named public enum. Observed against a live host with a scratch store: certificate refused (`/cert:deny`) → **143** `XF_EXIT_TLS_CONNECT_FAILED`; host reachable but nothing listening → **141** `XF_EXIT_CONNECT_FAILED`; certificate accepted, credentials wrong → **134** `XF_EXIT_LOGON_FAILURE`. DNS failures are 139/140.
- **Why:** this replaces the fragile contract recorded earlier the same day — classifying a pin mismatch by grepping libfreerdp's `"[certificates.json] configuration denies user to accept certificates"` line. A numeric enum in a public header is a far cheaper promise to hold across upgrades than a log sentence, and it maps straight onto D-020's two branches. Two cautions: 143 covers any TLS failure, not only a refused pin; and 143 is also `128+SIGTERM`, so anything that kills the client with `SIGTERM` (including a `timeout` wrapper) forges it.
- **Source:** FreeRDP 3.31.0 `client/X11/xfreerdp.h:339-390`; observed on FreeRDP 3.30.0 locally
- **Touches:** interfaces.md, constraints.md, debt.md

## 2026-09-23 — the hard-deny exit code is inferred from the auto-deny path, not observed
- **Kind:** question
- **Fact:** exit 143 was observed for `/cert:deny` (`AutoDenyCertificate`), not for `deny-userconfig` in `/etc/FreeRDP/certificates.json`, which needs root to place. Both set `verification_status = -1` and leave `tls_verify_certificate` by the same route (`tls.c:1745` and `:2013` both fall through to the same failure), so the same 143 is expected — but it is `assumed`.
- **Why:** if the two differ, a runner that classifies on 143 would misread a real pin mismatch as something else and D-026 would send it back to retrying for ever, which is the exact harm D-028 exists to stop. One test on a terminal settles it.
- **Source:** `libfreerdp/crypto/tls.c:1707-1754,2003-2100`; `assumed`
- **Touches:** debt.md, `docs/tests.md`

## 2026-09-23 — FreeRDP shouts "HOST IDENTIFICATION HAS CHANGED" on a *successful* first accept
- **Kind:** debt
- **Fact:** `tls_print_new_certificate_warn` is called at `tls.c:1930`, inside the branch where **no** stored entry was found, and prints the full SSH-style banner including `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!`, `The host key for <host> has changed` and `Host key verification failed.` — and then the code accepts and stores the certificate. Observed on every one of three clean first-use runs, exit 134 with the PEM written.
- **Why:** anyone classifying a certificate fault by log text would reach for exactly those phrases and would misclassify a healthy first connection as a mismatch. Recorded as a trap, and as the second reason to classify on exit code rather than text. Cosmetic upstream defect, present in 3.31 source and 3.30 behaviour; not ours to fix.
- **Source:** FreeRDP 3.31.0 `libfreerdp/crypto/tls.c:1909-1935`; observed on FreeRDP 3.30.0
- **Touches:** debt.md, `docs/troubleshooting.md`

## 2026-09-23 — a credential-free pre-flight is the cheapest thing that can satisfy D-028
- **Kind:** decision
- **Fact:** D-028 requires the terminal to *stop* on a certificate mismatch and say why. Remmina's exit carries no taxonomy, so the runner cannot get that from Remmina. If `freerdp3-x11` is installed for capture anyway, the same binary gives the runner a pre-flight — `xfreerdp3 /v:<host> /u:- /p:- +auth-only` with no real credentials — whose exit code classifies the fault before Remmina is launched: 143 stop and report, 134 certificate is good and proceed, 139/140/141 unreachable and retry per D-026.
- **Why:** it converts D-028 from a log-string contract with an upstream project into a numeric one, it needs no credentials, it needs no display, and it adds no package beyond the one capture already costs. What it does cost is a second TLS connection on every restart and a runner that now has a branch in it. Size: S for the capture step, M once the runner classifies and the unit must be told which exit codes are terminal.
- **Source:** `client/X11/xfreerdp.h:339-390`; observed exit codes, this session; D-028, D-020, D-026 in `docs/product/decisions.md`
- **Touches:** interfaces.md, stack.md, boundaries.md, a future ADR

## 2026-09-23 — for-product: the pin makes the terminal depend on a package the product never chose
- **Kind:** for-product
- **Fact:** every workable capture route puts a FreeRDP command-line client on the terminal permanently, or writes protocol code of our own (~30 lines of X.224 plus a TLS handshake, and a second implementation of a thing FreeRDP already does correctly). The package is the cheaper of the two by a wide margin, and it must be removed by `encore-uninstall.sh` or C-3's clean undo is broken.
- **Why:** it is a visible change to what "converting a machine" installs, and D-002 forbids touching the target machine but says nothing about the terminal's own footprint. Not a work item — a consequence of D-028 and D-029 the author should see before pinning is built.
- **Source:** this session
- **Touches:** debt.md, `docs/product/decisions.md`

---

# 2026-09-23 — capture without a borrowed client (D-030), verified on the wire

## 2026-09-23 — the whole RDP preamble is nineteen bytes each way, and Python's stdlib finishes the job
- **Kind:** interface
- **Fact:** sending TPKT+X.224 CR with an `RDP_NEG_REQ` of `requestedProtocols = 0x00000003` (SSL|HYBRID) returned `03 00 00 13 0e d0 00 00 00 00 00 02 0b 08 00 02 00 00 00` — `RDP_NEG_RSP`, selected `0x02` HYBRID — after which `ssl.SSLContext(PROTOCOL_TLS_CLIENT)` with `check_hostname=False`, `verify_mode=CERT_NONE` wrapped the *same* socket, completed TLSv1.3, and `getpeercert(binary_form=True)` returned 1670 bytes of DER. `hashlib.sha256(der).hexdigest()` gave `ed47d1c3744afa9ffa86d80f3dfbe7a2be67c34e4b171e5fe5a61fec5ed5ef41`.
- **Why:** that hex is byte-identical to the fingerprint FreeRDP wrote for the same host on 2026-09-23, and it is already in the pin's required form — lower-case, no colons — with no `openssl` and no `sed` in between. D-030's route is not a plan, it is a thing that ran.
- **Source:** run this session against the same live RDP host, Python 3.14.7 / OpenSSL 3.5.7 on the development machine; hash form required by FreeRDP 3.31.0 `libfreerdp/crypto/tls.c:1642-1700`
- **Touches:** ADR-0008, interfaces.md, data.md

## 2026-09-23 — requesting SSL alone gets no certificate at all from an NLA server
- **Kind:** constraint
- **Fact:** with `requestedProtocols = 0x01` (SSL only), `0x00` (RDP only), `0x08` (HYBRID_EX only), or with no `RDP_NEG_REQ` at all, the same host answered `RDP_NEG_FAILURE` with `0x00000005 HYBRID_REQUIRED_BY_SERVER` and never started TLS. `0x03` and `0x0b` both selected `0x02` HYBRID and proceeded.
- **Why:** it is the one byte that decides whether the capture step works at all, and the failure is silent in the sense that it looks like a protocol error rather than a policy answer. Ask for SSL|HYBRID, accept a selection of `0x01` or `0x02`, and treat `0x00` as "this server offers no certificate".
- **Source:** six variants run against the live host, this session
- **Touches:** ADR-0008

## 2026-09-23 — Python 3 with `ssl` is in Ubuntu 26.04's minimal install, not merely available
- **Kind:** stack
- **Fact:** `ubuntu-minimal` in the `resolute` (26.04 LTS) suite depends on `python3`, and `_ssl.cpython-*.so` ships in `libpython3.14-minimal` — so even the cut-down interpreter has TLS. The version there is 3.14, the same minor as the 3.14.7 the exchange above was verified on.
- **Why:** D-030 says "only what the terminal already has", and that had to be established rather than assumed. It also means `encore-install.sh:83` needs no new package for capture — the `apt-get install` line is unchanged.
- **Source:** packages.ubuntu.com, `resolute/ubuntu-minimal` dependency list and contents search for `_ssl.cpython`, read 2026-09-23
- **Touches:** stack.md, constraints.md C-1

## 2026-09-23 — the probe's TLS envelope must be no stricter than the client's, and by default it is stricter
- **Kind:** debt
- **Fact:** Python's default context inherits Ubuntu's OpenSSL security level (SECLEVEL=2) and a TLS 1.2 floor, while the shipped profile sets `tls-seclevel` explicitly for the real client (`encore-kiosk.remmina.template`, and Remmina 1.4.43 `rdp_plugin.c:2106-2110`). A self-signed certificate with a small key or an old signature — the normal case for xrdp and for `gnome-remote-desktop` — could be refused by the probe and accepted by the client. `ctx.set_ciphers(...)` and an explicit `minimum_version` are available and were confirmed to apply. **Corrected 2026-09-23:** this entry said `ctx.set_ciphers("DEFAULT@SECLEVEL=0")`. That string is wrong — measured on Python 3.14.7 / OpenSSL 3.5.7 it lowers the security level *and* drops ten suites the untouched client context offers, the AES-CCM family among them, so it narrows the envelope it was chosen to widen. The shipped string is `ALL:!aNULL@SECLEVEL=0` (129 suites against 61, a strict superset, at level 0); `!aNULL` is load-bearing because `ALL` admits anonymous suites and, with `verify_mode=CERT_NONE`, an anonymous handshake presents no certificate and would be reported as "no certificate" for a healthy target. The requirement is a property, not a literal — see ADR-0008.
- **Why:** this is the probe's one dangerous failure mode. A probe stricter than the client turns a healthy terminal into a permanent stop, which D-020 names as the more expensive direction to be wrong in. It must be set deliberately, not left to the interpreter's defaults.
- **Source:** verified on the development machine this session; D-020
- **Touches:** debt.md, ADR-0008

## 2026-09-23 — SNI is safe to send and safe to omit for an address
- **Kind:** interface
- **Fact:** `wrap_socket(server_hostname=...)` with `check_hostname=False` completed against the live host for the name, for its IP literal, and for `None`. Python suppresses the SNI extension for an address rather than raising.
- **Why:** R-5 lets an adopter name a machine or an address, and a far end that selects a certificate by SNI would otherwise show the probe something different from what the client sees. Passing the configured name through unchanged makes the probe see what the client will see, and costs nothing when the name is an address.
- **Source:** three handshakes this session, Python 3.14.7
- **Touches:** ADR-0008, interfaces.md I-6

## 2026-09-23 — the runner can classify D-028 without any contract with an upstream project
- **Kind:** decision
- **Fact:** the same probe, run by the runner before it launches the client, classifies from things we own: a socket error (DNS, refused, unreachable, timeout) is D-026's retry; an `RDP_NEG_FAILURE`, a selected protocol of `0x00`, or a fingerprint that is not the pin is exit 78, which ADR-0007's `RestartPreventExitStatus=78` already turns into a permanent stop with our own journal line beside it. Enforcement stays in `/etc/FreeRDP/certificates.json`; the probe decides what to say, not what is allowed.
- **Why:** it replaces both fragile options at once — the FreeRDP exit-code contract (gone with the package under D-030) and the log-string contract (gone with D-024, and poisoned by the "HOST IDENTIFICATION HAS CHANGED" banner printed on a *successful* first accept). It also survives replacing Remmina, which is the same reasoning D-030 was decided on. Cost: one extra TCP+TLS connection per launch, and a branch in the runner.
- **Source:** ADR-0008; ADR-0007 `RestartPreventExitStatus=78`; D-020, D-026, D-028, D-030
- **Touches:** ADR-0008, interfaces.md, boundaries.md, debt.md D-A2

## 2026-09-23 — the probe is a gate, not the guard, and two connections is why
- **Kind:** constraint
- **Fact:** the probe's TLS session and the client's are different connections, so a far end could in principle present one certificate to each. The pin file is what actually refuses; the probe only decides which of D-020's two branches the runner takes.
- **Why:** recorded so nobody later removes `deny-userconfig` on the grounds that "the runner already checks". That would turn a real guarantee into a check with a window in it.
- **Source:** ADR-0008; FreeRDP 3.31.0 `libfreerdp/crypto/tls.c:1642-1745`
- **Touches:** ADR-0008, constraints.md C-4

## 2026-09-23 — Q-11: only one kind of far end has ever been spoken to
- **Kind:** question
- **Fact:** every observation of the preamble, in this session and in the FreeRDP session before it, is against the one host the author runs. `xrdp` and `gnome-remote-desktop` have never been probed. The exchange is MS-RDPBCGR and is the same shape everywhere; what varies is the answer — an `xrdp` configured with `security_layer=rdp` selects `0x00` and offers no certificate at all, and neither implementation's default certificate strength has been seen.
- **Why:** the two failures it produces are opposite in cost. Selected protocol `0x00` is a correct, permanent stop on a server that genuinely cannot be pinned. A handshake the probe refuses on strength is a *wrong* permanent stop. Naming which is which needs one probe against each, and neither exists here to probe.
- **Source:** this session; `assumed` for both implementations
- **Touches:** docs/tests.md, ADR-0008

## 2026-09-23 — for-product: pinning as a whole is L, and the capture step is the small part of it
- **Kind:** for-product
- **Fact:** the probe and the fingerprint it produces are **S** — one small artifact, no new package, verified on the wire. What the author is actually buying with D-028/D-029/D-030 is **L**: the installer must show and record the confirmation, write and remove `/etc/FreeRDP/certificates.json`, drop `cert_ignore=1` from the template in the same change (until it goes, no pin anywhere has any effect), assert `trust_all=false` in the `remmina.pref` we generate and never read, and the runner must grow a pre-flight and a second terminal exit path.
- **Why:** the capture question was asked on its own and answers cheaply, and the cheap answer could easily be mistaken for the size of the feature. The expensive parts are the ones that make the pin load-bearing rather than decorative; a pin shipped without them is a file that changes nothing.
- **Source:** ADR-0008; NOTES 2026-09-23 on `cert_ignore` and `trust_all`; `encore-install.sh:83,137-149`; `encore-uninstall.sh`
- **Touches:** docs/product/decisions.md; debt.md D-A8

## 2026-09-23 — what `remmina-plugin-rdp` actually puts on a terminal: three runtime libraries, no header, no binary
- **Kind:** stack
- **Fact:** on Ubuntu 26.04 (`resolute`), `remmina-plugin-rdp` 1.4.43+dfsg-0ubuntu0.26.04.2 installs exactly one object of its own, `/usr/lib/x86_64-linux-gnu/remmina/plugins/remmina-plugin-rdp.so`, and pulls `libfreerdp3-3`, `libfreerdp-client3-3` and `libwinpr3-3` (plus GTK/cairo/cups). `libfreerdp3-3` ships only `libfreerdp3.so.3` → `libfreerdp3.so.3.24.2`; the archive's `freerdp3` source is 3.24.2 in the release pocket and 3.31.0 in `resolute-updates`. **No development headers** (those are `freerdp3-dev`, not installed) and **no executable of any kind**.
- **Why:** it settles what "the library is already there" means. There is a loadable `.so` under a versioned soname and nothing else — no `.so` symlink, no header, no tool. Anything that drives it must hardcode the soname and every constant it needs.
- **Source:** packages.ubuntu.com, `resolute/amd64/remmina-plugin-rdp` dependency list and file list, and `resolute/amd64/libfreerdp3-3` file list, read 2026-09-23
- **Touches:** stack.md, ADR-0008

## 2026-09-23 — there is no headless FreeRDP client in the Ubuntu archive; the only non-X11 one still needs a compositor
- **Kind:** stack
- **Fact:** the `freerdp3` source in `resolute` builds 24 binary packages. Only three contain a client: `freerdp-x11` (`xfreerdp`), `freerdp-sdl` (`sdl-freerdp`), and `freerdp-wayland` (`/usr/bin/wlfreerdp`, depending on `libwayland-client0`, `libwayland-cursor0`, `libxkbcommon0`). `winpr-utils` contains only `winpr-hash` and `winpr-makecert` — neither connects to anything. `freerdp-proxy` and `freerdp-shadow-x11` are servers. There is **no CLI, helper or utility that connects to an RDP server without a display**.
- **Why:** it closes the "is there another way in" question properly, from the archive rather than from the source tree. `freerdp-wayland` is the near miss — it is not X11 and not SDL, so D-030's *stated* objection does not bite it — but it is still a second remote desktop client installed as a package, used once per terminal, and it needs a running compositor, which setup does not have. D-030's deciding reason (a dependency on a client's packaging buys nothing when the client is expected to be dropped) applies to it unchanged.
- **Source:** packages.ubuntu.com, `source/resolute/freerdp3` binary package list; file lists for `freerdp-wayland` and `winpr-utils`, read 2026-09-23
- **Touches:** stack.md, ADR-0008

## 2026-09-23 — driving libfreerdp from ctypes is a binding to a C ABI, not a reuse of an implementation
- **Kind:** stack
- **Fact:** the route exists and the calls are nameable: `freerdp_new()`, `freerdp_context_new()`, set `instance->VerifyCertificateEx`, `freerdp_settings_set_string(settings, FreeRDP_ServerHostname, …)` and the port/username equivalents, `freerdp_connect()`, then `freerdp_get_last_error(context)` / `freerdp_get_last_error_name()` for the failure taxonomy. The certificate arrives in the `VerifyCertificateEx` callback — host, port, common name, subject, issuer, **fingerprint string**, flags — during the TLS handshake, before NLA, so no credentials are needed (same point in the exchange our own probe reaches). The exported functions are public API and ABI-held: `struct rdp_freerdp` uses `ALIGN64` numbered slots with `paddingA`…`paddingE` reserved gaps precisely so fields can be added without moving existing ones, and FreeRDP 3 made `rdpSettings` opaque behind `freerdp_settings_get/set_*` for the same reason.
- **Why:** the honest reading is that the API is stable *and that does not help us as much as it sounds*. From Python there is no compiler and no header on the machine, so every one of `context` at slot 0, `VerifyCertificateEx` at slot 66, each `FreeRDP_*` settings enum integer, each `FREERDP_ERROR_*` code and each callback prototype becomes a hardcoded magic number in our own file, copied from headers we neither ship nor can check. We would own *more* undocumented constants than ADR-0008's nineteen bytes, not fewer, and they would be constants about a private ABI rather than about a published wire format.
- **Source:** FreeRDP `include/freerdp/freerdp.h` (master) struct layout and padding; soname `libfreerdp3.so.3`; `assumed` that slot numbers in 3.24/3.31 match master
- **Touches:** ADR-0008, stack.md

## 2026-09-23 — what a wrong constant does: a segfault, and in the runner a segfault means retry for ever
- **Kind:** constraint
- **Fact:** a mismatched struct offset or enum id under `ctypes` is not an exception — it is a wild pointer. The visible outcome is a crash or corrupted output, not a message. In the setup step that is a confusing failure a person is watching; in the runner's pre-flight it is a non-78 exit, which ADR-0007's `RestartPreventExitStatus=78` turns into **indefinite retry** (D-026) — exactly the outcome D-028 exists to prevent.
- **Why:** it is the decisive asymmetry between the two approaches. A wire-protocol probe that meets something unexpected returns bytes that do not parse, and we choose what that means. An ABI binding that meets something unexpected takes the process down before any classification happens, and the safe-looking default (retry) is the wrong branch.
- **Source:** `assumed` — reasoned from ctypes semantics and ADR-0007's exit contract; not executed
- **Touches:** ADR-0008, debt.md, constraints.md

## 2026-09-23 — the one genuine advantage of binding to the library, and why it is cheaper to buy without it
- **Kind:** decision
- **Fact:** binding to libfreerdp would give the probe **the client's own TLS acceptance envelope**, because it would be the same library, the same OpenSSL configuration and the same code path Remmina's plugin uses — which removes ADR-0008's recorded risk of a probe stricter than the client stopping a healthy terminal. That risk is already closable in our own code for three lines: `check_hostname=False`, `verify_mode=CERT_NONE`, a permissive `set_ciphers(...)` and an explicit low `minimum_version`, all confirmed to apply this session. **Corrected 2026-09-23:** this entry named `set_ciphers("DEFAULT@SECLEVEL=0")`, which was measured to drop ten suites the untouched client context offers (all AES-CCM) and so narrows the envelope rather than widening it. Shipped: `ALL:!aNULL@SECLEVEL=0`. The requirement is the property recorded in ADR-0008 — no stricter than the client it precedes, and never accepting a handshake that presents no certificate — because a cipher string is OpenSSL-build-dependent.
- **Why:** the probe is a gate, not the guard — `deny-userconfig` in `/etc/FreeRDP/certificates.json` is what actually refuses a certificate. So the probe has no business judging TLS strength at all; it only needs to *see* the certificate. Deliberately making our envelope as permissive as possible is therefore correct on its own terms, and it happens to buy the whole of the library's advantage. The residual direction — probe permissive, client strict — leaves a terminal retrying, which is the status quo today and not what D-028 is about.
- **Source:** NOTES 2026-09-23 "the probe's TLS envelope must be no stricter than the client's"; ADR-0008 *Consequences*
- **Touches:** ADR-0008, debt.md

## 2026-09-23 — the major version is where the two approaches diverge most
- **Kind:** stack
- **Fact:** the wire preamble is MS-RDPBCGR, a published Microsoft specification, frozen since RDP 5.2 era and identical on every server we could meet; nothing Ubuntu ships can change it. The ABI is versioned `libfreerdp3.so.3` and a FreeRDP 4 would land as a different soname with slots and enum ids free to move. D-024 commits us to the current release and no compatibility handling, so on that day the binding is a rewrite with no warning and the probe is untouched.
- **Why:** it answers the author's instinct directly. "Reuse an existing implementation" is normally right because the implementation absorbs change on your behalf. Here the thing that changes is the library, and the thing that does not change is the protocol — so the borrowed side is the moving one and the hand-written side is the frozen one. That is the inversion that makes this case unusual.
- **Source:** MS-RDPBCGR 2.2.1.1/2.2.1.2; Ubuntu soname `libfreerdp3.so.3`; D-024
- **Touches:** ADR-0008, stack.md

## 2026-09-23 — the Connection Confirm's seventh byte is `00`; ADR-0008's Decision block was wrong and is corrected
- **Kind:** decision
- **Fact:** an X.224 Connection Confirm header is LI, code `0xD0`, DST-REF (2), SRC-REF (2), class option (1) — seven bytes, last one `00` for class 0. The capture reads `03 00 00 13 | 0e d0 00 00 00 00 00 | 02 0b 08 00 02 00 00 00`; the `02` is the `RDP_NEG_RSP` type byte, not part of the header. ADR-0008 wrote the header as `0e d0 00 00 00 00 02` and has been corrected in place with a dated note.
- **Why:** the capture and the specification agree with each other, the ADR agreed with neither, and the ADR's own Connection *Request* line (`0e e0 00 00 00 00 00`) already had the right shape — so it was a transcription slip, not a disagreement about what was seen. Left alone it would have made anyone comparing a real response byte-for-byte reject every real response. The structural parser in `docs/plans/certificate-probe.md` is immune either way, and that is now the rule rather than a workaround.
- **Source:** NOTES 2026-09-23 capture; MS-RDPBCGR 2.2.1.2 / X.224 CC TPDU structure
- **Touches:** ADR-0008 (done)

## 2026-09-23 — the probe's TLS floor is TLS 1.0, and it is a decision
- **Kind:** decision
- **Fact:** `ssl.TLSVersion.TLSv1`. ADR-0008 said only "an explicit low `minimum_version`"; the number is now in the ADR's addendum.
- **Why:** Ubuntu's `/etc/ssl/openssl.cnf` imposes a TLS 1.2 floor on anything that does not say otherwise, and a probe stricter than the client stops a healthy terminal for ever — D-020's expensive direction. It is the same argument as `SECLEVEL=0` applied to the version, so it belongs to ADR-0008 rather than to a new decision, and it is not the implementer's preference.
- **Source:** `docs/plans/certificate-probe.md`; ADR-0008 addendum on the permissive envelope
- **Touches:** ADR-0008 (done)

## 2026-09-23 — "not RDP" stops, "TLS handshake failed" retries
- **Kind:** decision
- **Fact:** the runner contract in ADR-0008 had no row for either. It now has both, under one rule: stop when the evidence is about the target and retrying cannot change it; retry when the failure could be ours or transient. Answered-but-not-RDP is a wrong address — stop, exit 78. A failed handshake after a successful negotiation is a far end that has already proved it speaks RDP — retry.
- **Why:** anything left unclassified exits non-78 and retries for ever, which is exactly the harm D-028 exists to prevent, so silence here was itself the wrong decision. The asymmetry that decided each: a wrong address is repairable in two minutes by the person who typed it, while a failed handshake is the same status our own too-strict envelope would produce, and stopping healthy terminals on our own strictness is the direction D-020 names as worse.
- **Source:** ADR-0008 addendum 2026-09-23; D-020, D-026, D-028; ADR-0007's exit-78 contract
- **Touches:** ADR-0008 (done), debt.md D-A15

## 2026-09-23 — the pre-flight's address comes from the install record, not from the profile
- **Kind:** boundary
- **Fact:** ADR-0009. `encore-install.sh` splits the administrator's address once and writes `RDP_HOST=` and `RDP_PORT=` into `/var/lib/encore/encore-install.conf` (I-7); the runner reads those two keys and passes them to the probe. It still never opens the profile. Boundary 4's "must not know the host" is restated as "may know where, never who".
- **Why:** R-5 permits a port, the port lives inside `server=` in the profile, and the runner is the one part forbidden to read the profile. The split has to happen somewhere; the installer is the only place where a malformed address can be reported to a person who is standing there, and the only place that already holds host and port as separate facts. The alternative gives the runner a parser for a format we do not own and a `:` split that is ambiguous for IPv6, in the file that also holds the password. The boundary genuinely moves — recorded, not widened quietly.
- **Source:** `encore-kiosk.sh:6`; `encore-install.sh:105-112`, `:121`; `encore-kiosk.remmina.template:37`; I-7
- **Touches:** ADR-0009, boundaries.md part 4, interfaces.md I-7, debt.md D-A16

## 2026-09-23 — Q-11 now decides between two harms, not two unknowns
- **Kind:** question
- **Fact:** Q-11 stands, unchanged in substance, and has landed somewhere concrete. With the runner contract complete, "no TLS offered" stops the terminal for ever and "TLS handshake failed" retries for ever. Those are the two statuses an unprobed `xrdp` or `gnome-remote-desktop` could produce wrongly, and nothing testable locally tells a genuine instance of either from a mistake by us.
- **Why:** it is no longer an open question about the wire — it is a live cost in the runner's design, chosen on one data point. Whoever designs the pre-flight must be able to see that, which is why it is written into the ADR addendum and not only here.
- **Source:** NOTES 2026-09-23 "Q-11: only one kind of far end has ever been spoken to"; ADR-0008 addendum
- **Touches:** ADR-0008 (done), docs/tests.md Test 11 (**corrected 2026-09-23**: this said Test 10; 10 was already "does running setup again leave a working terminal?", so the probe's manual check shipped as Test 11)

## 2026-09-23 — the permissive envelope is a property; the literal cipher string was wrong and is corrected
- **Kind:** decision
- **Fact:** ADR-0008's option-D addendum named `set_ciphers("DEFAULT@SECLEVEL=0")`, and this log repeated it twice. Measured on Python 3.14.7 / OpenSSL 3.5.7: the untouched `PROTOCOL_TLS_CLIENT` context offers 61 suites at security level 2; `DEFAULT@SECLEVEL=0` offers 61 at level 0 but is **missing 10 of them**, the whole AES-CCM family among them; `ALL:!aNULL@SECLEVEL=0` offers 129 at level 0, missing none. The shipped probe uses the third. ADR-0008 and both log entries are corrected in place, dated, and the ADR now states the **property** rather than a literal: *no suite the untouched client context offers may be absent, and no unauthenticated suite may be present* — equivalently, never stricter than the client it precedes, and never accepting a handshake that presents no certificate.
- **Why:** the ADR's own string narrowed the envelope the addendum exists to widen — a far end offering only a CCM suite would be classified a TLS failure while the real client connects to it, which is the false "this configuration is broken" the addendum claims to buy off and the direction D-020 names as expensive. `!aNULL` is independently load-bearing: `ALL` admits anonymous suites, and with `verify_mode=CERT_NONE` a far end selecting one completes a handshake presenting no certificate, giving a false `NO_CERTIFICATE` — a permanent stop — for a healthy target. Recording a literal was the underlying mistake: a cipher string is OpenSSL-build-dependent and this one was already wrong on the first build it met. The property is checked against Python's own default client context as a proxy for the real client's offer list, which is the strongest thing testable without a terminal, and the ADR says so rather than implying the proxy is the client.
- **Source:** measurements reported by the implementer and reproduced by an independent reviewer, Python 3.14.7 / OpenSSL 3.5.7; ADR-0008 addendum "Its one real advantage is conceded, and bought elsewhere"
- **Touches:** ADR-0008 (done), NOTES 2026-09-23 entries on the TLS envelope (done)

## 2026-09-23 — a 12–18 byte declared frame length stops the terminal for ever, and nothing said so
- **Kind:** decision
- **Fact:** the probe classifies a TPKT frame declaring 12–18 bytes as "not RDP", which ADR-0008's runner table puts on the exit-78, permanent-stop side. No document specified that band; it was settled in an implementation gap. It is **ratified**, not re-opened: a frame that is TPKT-shaped but too short to contain an X.224 Connection Confirm with an `RDP_NEG_RSP` (7 + 8 bytes after the 4-byte header, so 19 in total) cannot be a valid answer to what we sent, and the evidence is about the target, which is exactly the rule the addendum states.
- **Why:** it belongs on file because it is a stop-for-ever decision and because the risk it carries is one ADR-0008 already accepted in the abstract — a bug in our own frame parser stops healthy terminals permanently. This is the first concrete instance of that risk, and the band rests on the specification rather than on any observation: no real far end has ever answered in it. If a target is ever seen answering with a short frame, this band and not the rule is what to revisit.
- **Source:** MS-RDPBCGR 2.2.1.2 / X.224 CC TPDU minimum length; ADR-0008 addendum runner table; reviewer finding, 2026-09-23
- **Touches:** ADR-0008 runner table

## 2026-09-23 — `permissive_tls_context()` mutates the process-global warnings filter
- **Kind:** debt
- **Fact:** it wraps the TLS-1.0 deprecation warning in `warnings.catch_warnings`, which swaps and restores the interpreter's global filter and is not thread-safe. Harmless in a standalone script; the installer ticket and the runner's pre-flight both call it from Python. Recorded as `debt.md` D-A17.
- **Why:** it is a property of the seam, not of the script — the second caller is what makes it real, and it is cheaper to decide who owns warning suppression before that caller exists than to diagnose a warnings filter that is intermittently not what someone set.
- **Source:** reviewer finding, 2026-09-23; `encore-probe.py` `permissive_tls_context()`
- **Touches:** debt.md D-A17

## 2026-09-23 — the one-line-stderr guarantee is not architecture, and is not recorded
- **Kind:** question
- **Fact:** a reviewer noted the probe's single-line stderr guarantee could break if an underlying error string contains a newline. Deliberately **not** recorded as debt or a constraint. Nothing consumes the probe's stderr as a contract: the runner classifies on the exit code (ADR-0008's table), and the journal accepts any number of lines.
- **Why:** written down so the decision not to record it is visible rather than looking like an oversight. If anything ever parses that stream — a future status file, a support script — it becomes an interface and the guarantee becomes load-bearing at that moment, not before.
- **Source:** reviewer finding, 2026-09-23; ADR-0008 runner table
- **Touches:** nothing yet; interfaces.md if a consumer appears

## 2026-09-23 — `DEFAULT@SECLEVEL=0` narrows the envelope it was chosen to widen [TAKEN 2026-09-23 — folded above and into ADR-0008; no longer waiting]
- **Kind:** for-architecture (taken)
- **Fact:** ADR-0008's addendum names `set_ciphers("DEFAULT@SECLEVEL=0")` as one of the three lines that close the stricter-probe risk. Measured while building the probe, on Fedora / Python 3.14.7 / OpenSSL 3.5.7, it does the opposite in part: Python's default cipher list for `PROTOCOL_TLS_CLIENT` is **not** OpenSSL's `DEFAULT`, so the call lowers the security level as intended *and* drops ten-plus suites the untouched context offers, all the AES-CCM ones among them. `encore-probe.py` therefore ships `set_ciphers("ALL:!aNULL@SECLEVEL=0")` — measured a strict superset of the untouched list (129 suites against 61) at security level 0, with anonymous suites excluded because `ALL` admits them and the probe, running `verify_mode=CERT_NONE`, would turn an anonymous handshake into a false `NO_CERTIFICATE` for a healthy target. **The ADR now records a string the code does not use.**
- **Why:** a far end offering only a CCM suite would be classified `TLS_FAILED` while Remmina connects fine — the false "configuration is broken" that ADR-0008's *Consequences* names and that this very addendum claims to have bought off, and which D-020 calls the more expensive direction. Worth more than correcting the string: the envelope's requirement is testable if stated as a property — *no suite the untouched client context offers may be absent, and no unauthenticated suite may be present* — where a literal cipher string is OpenSSL-build-dependent and was wrong on the first build it met. Both halves of that property are asserted in `encore-probe-test.py`.
- **Source:** measured against `ssl.SSLContext(PROTOCOL_TLS_CLIENT).get_ciphers()`; `encore-probe.py` `permissive_tls_context()`; ADR-0008 addendum "Its one real advantage is conceded, and bought elsewhere"
- **Touches:** ADR-0008 (addendum needs correcting), `docs/plans/certificate-probe.md`

## 2026-09-23 — the probe's manual test is Test 11, not Test 10 [TAKEN 2026-09-23 — the stale pointer above is corrected; no longer waiting]
- **Kind:** for-architecture (taken)
- **Fact:** `docs/plans/certificate-probe.md` step 7 and the Q-11 entry above both call the probe's manual check "Test 10". `docs/tests.md` Test 10 was already taken by "does running setup again leave a working terminal?", so it shipped as **Test 11 — does the probe agree with the target?**. Nothing else changed; the pass conditions are as the plan wrote them.
- **Why:** two documents pointing at the same ordinal for different tests is how a record stops being usable, and the ordinal is the only handle these documents have on each other.
- **Source:** `docs/tests.md`; `docs/plans/certificate-probe.md` step 7
- **Touches:** NOTES entry "Q-11 now decides between two harms", `docs/plans/certificate-probe.md`

## 2026-09-23 — four outcomes still had no row in ADR-0008's runner table
- **Kind:** decision
- **Fact:** the probe defines ten statuses; `2 USAGE`, `5 TIMEOUT` and `9 NO_CERTIFICATE` had no row, and exit `1` (a crash, which is not a status) had none either. A third addendum to ADR-0008 maps all four under the existing rule: `2` **stops**, `5` **retries**, `9` **stops**, `1` **retries**. Every status now has a side — `0` launches; `3`, `4`, `5`, `8`, `1` retry; `2`, `6`, `7`, `9`, `10` stop — and a new probe status is now a change to ADR-0008, not only to the probe. `5` was already named in prose in the original table ("timeout"); it is now tied to the number so nobody has to match wording to a code.
- **Why:** anything unmapped exits non-78 and retries for ever, which is the harm D-028 exists to prevent, so omission was a decision by accident. The two large costs are named rather than designed away: stopping on `2` means a bug in our own argument handling stops a healthy terminal for ever, offset by that path being decided before any packet leaves the machine and so provable without a network; stopping on `9` rests entirely on the probe never being the reason nothing was presented — `!aNULL` closes the one known way we could cause it, and Q-11 leaves the rest open, since `9` and `8` are the two opposite mistakes an unprobed `xrdp` or `gnome-remote-desktop` could produce and we have put one on each side with one data point.
- **Source:** `encore-probe.py` module docstring (statuses read from the file, not from memory); ADR-0008 runner tables; review finding, 2026-09-23
- **Touches:** ADR-0008 (done)

## 2026-09-23 — the Python floor is 3.14, and it is behavioural
- **CORRECTED the same day — the floor is 3.10, not 3.14.** This entry is kept
  as written because it was true when written. The defect it rests on was fixed
  concurrently: the probe no longer reads `.reason`, so the behavioural half of
  the floor is gone and only the syntactic 3.10 remains. See the entry "the
  Python floor dissolves to 3.10" at the end of this log, and `constraints.md`
  C-1, which now carries the whole story.
- **Kind:** constraint
- **Fact:** `constraints.md` C-1 now carries CPython ≥ 3.14 beside the systemd ≥ 254 floor, and `stack.md` has a CPython row (it had none — the probe's language was absent from the stack record entirely). Two things set it: **3.10** syntactically, because `bytes | None` and `list[str]` are evaluated at runtime in the probe's signatures; **3.14** behaviourally, and that is binding. Measured on `a..b:3389` on 2026-09-23: 3.10.21 and 3.11.16 raise a bare `UnicodeError` with **no `.reason`**; 3.14.7 raises `UnicodeEncodeError` with `reason='label empty'`. The probe reads `.reason` on that path, so below the floor it raises `AttributeError` inside an `except`, exits 1, and the malformed `RDP_HOST=` that ADR-0008 stops on is retried for ever instead.
- **Why:** the record said only "Python 3, standard library only", which is not a floor, and the difference is not cosmetic — it inverts a stop-or-retry decision. Stated at 3.14 because that is the highest version measured working and it costs nothing: Ubuntu 26.04 ships it and is the only distribution a terminal has ever been built on.
- **Source:** measured locally against `/usr/bin/python3.{10,11,14}`, 2026-09-23; CPython `Lib/encodings/idna.py` (bpo-25880, `UnicodeError` → `UnicodeEncodeError`); `encore-probe.py` `UnicodeError` handler. **3.12 and 3.13 were not measured** — no interpreter of either was to hand — so the exact boundary between 3.11 and 3.14 is `assumed`.
- **Touches:** constraints.md C-1 (done), stack.md (done), debt.md D-A18 (done)

## 2026-09-23 — nothing makes the Python floor visible on the machine
- **CORRECTED the same day: the floor is 3.10, not 3.14.** The item itself
  survives — nothing still checks anything — but it is much smaller than this
  entry describes, because 3.10 is four years old and the failure below it is
  now a `SyntaxError` at import rather than a silent misclassification.
- **Kind:** debt
- **Fact:** recorded as `debt.md` D-A18. `encore-probe.py` has a bare `#!/usr/bin/python3` and `encore-install.sh:79-83` checks no version, so an adopter on an older release gets behaviour the record does not describe with nothing detecting it. Exactly D-A14's shape, one component along.
- **Why:** D-024 accepts *excluding* older distributions; it does not accept the exclusion being undetectable. Under D-027 there is no resolver, so a check lives in the installer or nowhere.
- **Source:** `encore-probe.py:1`; `encore-install.sh:79-83`; D-A14, D-024, D-027
- **Touches:** debt.md D-A18 (done)

## 2026-09-23 — whether the installer should check version floors
- **Kind:** for-product
- **Fact:** there are now two undetected version floors, systemd ≥ 254 (D-A14) and CPython ≥ 3.14 (D-A18). Both bite silently and both would be closed by the same few lines in `encore-install.sh`. Whether that is worth doing is a scheduling question and is not settled in the architecture record.
- **Why:** the technical picture is complete — the checks are cheap, they live in the installer or nowhere under D-027, and the cost of not having them is a terminal that behaves differently from the record with no signal. What is not ours is whether excluding an adopter loudly is better than excluding them silently, which is a product promise.
- **Source:** D-A14, D-A18, D-027
- **Touches:** nothing here; it belongs in `BACKLOG.md` if the product manager takes it
- **AMENDED 2026-09-23:** the Python half of this is now much weaker — the
  floor is 3.10, not 3.14. The systemd ≥ 254 half is unchanged and is the
  stronger case of the two.

## 2026-09-23 — the Python floor dissolves to 3.10; it had been read off a defect
- **Kind:** constraint
- **Fact:** the floor is **CPython ≥ 3.10**, syntactic. `bytes | None` in a signature at `encore-probe.py:255` is a runtime-evaluated PEP 604 union with no `from __future__ import annotations` in either file, so below 3.10 the module does not import. Independently and at the same number, `socket.timeout` became an alias of `TimeoutError` in 3.10, and the probe separates `5 TIMEOUT` from `4 UNREACHABLE` by catching `TimeoutError` before `OSError` (`:345`, `:366`) — below 3.10 every socket timeout would be reported UNREACHABLE. **The 3.14 figure recorded earlier today is withdrawn**: it was behavioural, derived from the probe reading `UnicodeError.reason`, and the engineer fixed that defect concurrently — the handler now interpolates the exception itself (`:389-408`), which works on every version.
- **Why:** the number described what the code happened to do, not what the design needs. A constraint read off a defect dissolves when the defect does, and that is worth keeping visible in the record rather than overwriting — it is the clearest example this project has of the difference between a measurement and a requirement. The earlier entries are left in place with correction notes on top for exactly that reason.
- **Source:** read from `encore-probe.py` and `encore-probe-test.py`, not from the earlier reasoning; suite run on `/usr/bin/python3.{10,11,14}` — 61 tests OK on each — and `encore-probe.py "ex..ample.com"` exits 2 with one line and no traceback on all three; `socket.timeout is TimeoutError` confirmed True on 3.10.21; `docs/tests.md` Test 11 records the engineer's own three-interpreter run. **Nothing below 3.10 was run — none was to hand — so "3.9 fails" is `assumed`** from PEP 604 and the 3.10 changelog.
- **Touches:** constraints.md C-1 (done), stack.md (done), debt.md D-A18 (done), 00-index.md (done)

## 2026-10-04 — SELinux enforcing permits the arrangement, and nothing needs adding to the installer
- **Kind:** constraint
- **Fact:** on Fedora 44 with SELinux `Enforcing` and stock `selinux-policy-targeted-44.10-1.fc44`, the product's arrangement is allowed as it stands. `/var/lib/encore` and every directory beneath it label as `var_lib_t`, not `user_home_dir_t`, and both domains the session can land in — `unconfined_t` via `pam_selinux`, `unconfined_service_t` if it is not relabelled — are allowed full use of `var_lib_t` by the live kernel. `seusers` maps `__default__` to `unconfined_u`, so `encore` is unconfined; `--system` and `/usr/sbin/nologin` are invisible to SELinux, as no rule keys on a uid range or a shell. `get_default_context("unconfined_u","system_u:system_r:init_t:s0")` returns 0 — the call `session required pam_selinux.so open` makes, and the one that would otherwise refuse to start the unit. The policy explicitly allows `init_t init_t:process setexec`, `init_t login_userdomain:process transition` and `init_t login_userdomain:process2 nnp_transition`, the last of which is required because `encore-kiosk.service:48` sets `NoNewPrivileges=true`. Every directory the installer writes into already carries the type `matchpathcon` wants, including `/etc/systemd/system` as `systemd_unit_file_t`, so no `restorecon` and no `semanage fcontext` call belongs anywhere. **No policy module, so no Fedora-only component, so D-036's "one implementation" claim holds and no ADR is warranted.**
- **Why:** D-036 named SELinux as the specific untested risk of accepting dnf and said a policy module would weaken the decision. It would not be needed. The stronger half of the answer is not "unconfined lets it through" but that the labels are right by parent inheritance — which means the installer stays the same on both families rather than growing a conditional branch, and that is the difference between M and L on `BACKLOG.md` item 16. **The hazard is the opposite of the one expected:** `semanage fcontext -a -t user_home_dir_t "/var/lib/encore(/.*)?"` is the one change that could break a working terminal, because a home type under a `var_lib_t` parent is unreachable and a system identity does not belong in a user home type.
- **Source:** measured 2026-10-04 on the author's Fedora 44 machine, read-only: `getenforce`; `matchpathcon` on every installed path; `selinux_check_access` against the live kernel for `dir`/`file`/`sock_file`/`chr_file` on `var_lib_t`, `user_tmp_t`, `tty_device_t`, `dri_device_t`, `event_device_t`; `selinuxexeccon /usr/bin/chvt system_u:system_r:init_t:s0`; `/etc/selinux/targeted/seusers`; `/etc/pam.d/login`; `/etc/security/namespace.conf` (empty, so `pam_namespace` is a no-op); `libselinux-3.11` `get_default_context` called directly; `python3-setools` 4.6.0 against `/etc/selinux/targeted/policy/policy.35` for the attribute and allow-rule reads
- **Touches:** constraints.md C-1 (taken), interfaces.md I-5 (taken)

## 2026-10-04 — a clean AVC log is not evidence, and the discovery command that looks like it works does not
- **Kind:** question
- **Fact:** `dontaudit` rules suppress SELinux denials with no log line at all, and this policy carries 102 reaching `unconfined_service_t`, 164 reaching `unconfined_t` and 121 reaching `init_t`. So "`ausearch` found nothing" proves nothing. The canonical command also needs root: `/var/log/audit` is `0700 root:root`, so `ausearch -m AVC,USER_AVC,SELINUX_ERR,USER_SELINUX_ERR -ts boot` run without it tells you nothing about denials. **Correction, same day:** this entry first said the command "fails open" and **exits 0**, which would have made it indistinguishable from a healthy machine. That is wrong. Re-measured on Fedora 44 with `auditd` active: it prints `Error opening /var/log/audit/audit.log (Permission denied)` and **exits 1**. It fails loudly and will not fool a reader or a script. The claim was recorded before the exit code was read, which is the error `CONTRIBUTING.md` names as reasoning from configuration to runtime — committed here by the check written to catch that very habit. The `dontaudit` half of this entry stands and is the real trap: a clean log is still not evidence. The root-free command that does work is `journalctl -b -g 'avc: *denied'`, which returned real denials for an ordinary user here with `auditd` active. `journalctl -t setroubleshoot`, which Red Hat's own troubleshooting chapter recommends, produces nothing on a stock Fedora 44: `setroubleshoot-server` is not installed.
- **Why:** this is the project's documented recurring failure — things reporting healthy while not working — arriving in the diagnostic rather than the product. `getenforce` returning `Enforcing` tells an adopter nothing, and the obvious next command lies by exiting 0. The only check that cannot lie by omission is `setenforce 0`, reproduce, `setenforce 1`: if the behaviour changes it is SELinux and if it does not it is not. The escalation when a denial is suspected but absent from the log is `semodule -DB`, reproduce, `ausearch`, then `semodule -B` to restore.
- **Source:** measured 2026-10-04 on the author's Fedora 44 machine — `ausearch` exit status observed as non-root; `journalctl -b -g` observed returning denials; `rpm -q setroubleshoot-server`; `dontaudit` counts from `python3-setools` against `policy.35`. Red Hat SELinux troubleshooting chapter and a Fedora SELinux list thread on `unconfined_service_t` denials hidden by `dontaudit`, read
- **Touches:** docs/troubleshooting.md — **for the product manager to place; it is not the architect's file**

## 2026-10-04 — the unit's keyring suppression is Debian-shaped and misses on Fedora
- **Kind:** debt
- **INCOMPLETE — corrected the same day by the entry at the end of this file.** This entry names one site and says it "sits in the unit rather than the installer". That is wrong: the installer computes the same path at `encore-install.sh:42-48` and the consequence there is a failed install, not a degraded terminal. Left in place because this is a log; read the correction before acting on this.
- **Fact:** `encore-kiosk.service:27-29` hides Remmina's secret plugin by naming three Debian multiarch paths. Fedora puts the file at `/usr/lib64/remmina/plugins/remmina-plugin-secret.so`, so none of the three can match, and the leading `-` on each line makes systemd tolerate the miss without a word. Recorded as `debt.md` D-A19.
- **Why:** `BACKLOG.md` item 16 states the unit mentions no package manager and is therefore untouched. True of the package manager, false of the distribution — this is the one place in the product that reasoned from a distribution's filesystem layout rather than from a capability, and it sits in the unit rather than the installer. The consequence is the keyring prompt item 8 records as *observed* blocking an unattended terminal on 2026-09-14. It is one more line in one file, not a Fedora-only component, so item 16 stays M — but item 16's file list grew by one.
- **Source:** `dnf repoquery -l remmina-plugins-secret` on Fedora 44, 2026-10-04 (`remmina-plugins-secret-1.4.41-2.fc44`) — measured. That the suppression therefore fails to suppress is read, not watched.
- **Touches:** debt.md D-A19 (taken), overview.md (taken)

## 2026-10-04 — two package names differ, and the capture package is a third
- **Kind:** stack
- **Fact:** five of the seven packages `encore-install.sh:91-92` asks for are named identically on both families; `remmina-plugin-rdp` is `remmina-plugins-rdp` and `pipewire-pulse` is `pipewire-pulseaudio`. Item 7's capture tool is a third difference and is not in the installer yet: `freerdp3-x11` on Ubuntu, `freerdp` on Fedora — verified as `freerdp-2:3.31.1-1.fc44` providing `/usr/bin/xfreerdp` and `/usr/bin/wlfreerdp`, 2026-10-04.
- **Why:** the two installer names will be found by whoever edits those two lines. The capture name will not, because it will be written fresh against whichever family the author is sitting in front of, and a package added under one name only is also a package `encore-uninstall.sh` removes under one name only — which breaks C-3's clean undo on the other family and nowhere else, the hardest kind of defect to notice.
- **Source:** `dnf repoquery` on Fedora 44 and `BACKLOG.md` item 16, 2026-10-04
- **Touches:** stack.md (taken)

## 2026-10-04 — `/etc/FreeRDP` is now a two-platform question, not a gap
- **Kind:** question
- **Fact:** the 2026-09-23 entry above records `/etc/FreeRDP/certificates.json` as verified on Fedora's FreeRDP 3.30.0 and **not** on Ubuntu, and calls Ubuntu "the only distribution a terminal has ever been built on". D-036 inverts the shape of that gap: the verified side is now a claimed platform, so the question is no longer "we checked the wrong machine" but "we have checked one of our two platforms". The path depends on `FREERDP_USE_VENDOR_PRODUCT_CONFIG_DIR` at build time, which is a per-distribution build flag, so it must be confirmed **once per family** and the two answers may differ. Fedora 44 now ships FreeRDP 3.31.1 (2026-10-04), so even the Fedora answer was taken on 3.30.0 and not re-checked on what an adopter would install today.
- **Why:** item 7's pin written to the wrong path is silently inert and the terminal connects to anything — the failure is invisible and in the unsafe direction. Two families means two chances to write it to the wrong place, and a pin that works on the machine the author tests on is the worst possible outcome. The check is one line of that machine's own `xfreerdp(1)`, per family, before anything is written.
- **Source:** `NOTES.md:237` (2026-09-23); `rpm -q freerdp` on Fedora 44, 2026-10-04
- **Touches:** stack.md, debt.md D-A8, docs/tests.md

## 2026-10-04 — the keyring path defect has a second site, and that one blocks the conversion
- **Kind:** debt
- **Fact:** the entry above named only `encore-kiosk.service:28-30` (which it miscited as `:27-29`). **`encore-install.sh:42-48` constructs the same Debian multiarch path from `uname -m`** and passes it to `systemd-run -p "InaccessiblePaths=-$SECRET_PLUGIN"` at `:173`, which is the step that writes the RDP password into the profile. On Fedora the path does not exist, the leading `-` tolerates the miss, the plugin is not suppressed while the password is written, the password is not stored, and the installer's own guard at `:183-184` fires `die "no password stored in the profile"`. **So the two sites have different consequences: the unit site degrades a working terminal into asking for a keyring; the installer site means the conversion cannot complete at all.** Item 16 is undeliverable without it. Verified against the files, 2026-10-04.
- **Why:** this changes the severity reasoning, not the size. The item is no longer "a prompt comes back" but "the install fails", which makes it a blocker rather than a degradation — and it is still two files, no Fedora-only component and no package-manager conditional, so **item 16 stays M.** The one piece of luck is that site 2 fails loudly: the installer's own guard catches it, so this is the rare defect in this project that announces itself. **The lesson is about reading, not about Fedora:** the milder site was found first from the unit, and the blocking site sat eight lines into an installer the same reader had already opened, with the call that consumes it 125 lines further down. One grep for the plugin filename across the tree would have returned both on the first pass. Found by the senior engineer planning item 16, confirmed by the product manager.
- **Source:** `encore-kiosk.service:28-30`; `encore-install.sh:42-48`, `:173`, `:183-184` — read directly. The senior engineer's plan, `docs/plans/fedora-dnf-family.md`, is the authority on the repair. Fedora's path measured by `dnf repoquery` 2026-10-04. That the suppression fails on Fedora is read, not watched: no terminal has been booted there, so neither the failed install nor the keyring prompt has been seen.
- **Touches:** debt.md D-A19 (taken, rewritten), overview.md (taken)

## 2026-10-04 — hiding the `.so` is the only mechanism there is, so the path list is not a shortcut
- **Kind:** stack
- **Fact:** D-A19 previously asked whether Remmina could simply be configured not to load its secret plugin, which would have replaced a growing list of literal paths with one setting. **Closed negative.** No such preference exists; the maintainer said in 2019 that a hidden option could be added and it never was; upstream documents exactly two mechanisms — uninstall the package, or make the `.so` unreachable. Establishing this was the senior engineer's, with sources, while planning item 16.
- **Why:** uninstalling is closed by R-11 and D-007, which forbid the product changing software the machine already had — so hiding the file is not a shortcut this product chose, it is the only option on the table, and the path list is a consequence of that rather than a design preference. Worth recording as closed so nobody reopens it and spends the time again. What remains is not *whether* to name a path but *how to find* it, which is a discovery problem and has an answer.
- **Source:** senior engineer's investigation 2026-10-04, with upstream sources; R-11, D-007
- **Touches:** debt.md D-A19 (taken)

## 2026-10-04 — the architecture refusal in the installer was never a product limit
- **Kind:** constraint
- **OVERCLAIMED — corrected the same day by the entry at the end of this file.** The "stops claiming anything in either direction" clause below is wrong: the shipped code moves the refusal to the coverage check rather than ending it, so a machine whose plugin path the unit does not name is still turned away. The premise — that the refusal was an artefact and not a product limit — stands. Left in place because this is a log.
- **Fact:** `encore-install.sh:46` ends the architecture `case` with `die "unsupported architecture: $(uname -m)"`, refusing anything that is not `x86_64`, `aarch64` or `armv7l`. **R-2 claims no particular hardware is required and `constraints.md` C-1 puts 32-bit and ARM in scope; nothing in the product record ever restricted the instruction set.** The refusal exists only because a Debian triplet had to be constructed and the constructor knew three. Removing the triplet (D-A19's fix) removes the `case` and with it the `die`. **The product manager has ruled, 2026-10-04, that the refusal is not to be preserved, and that this is a deliberate behaviour change rather than a tidy-up.** Recorded as `debt.md` D-A20.
- **Why:** this is mechanism leaking out of a script and being enforced as policy on a reader — the product refuses a machine it claims to support, in a sentence no requirement authorises. D-036 made it visible rather than causing it: Fedora also builds for `ppc64le`, `s390x` and `riscv64`, on two of which that line would refuse a machine R-2 claims. It was equally wrong on apt and nobody noticed because nobody had an unusual machine. Replacing the computation with a discovery makes the product stop claiming anything about exotic architectures **in either direction** — neither promising nor refusing — which is what R-2 already implies. The accepted cost is that a machine refused early in one legible line may now fail later and less clearly; a late honest failure on a machine nobody has tried beats an early false one on a machine the record claims.
- **Source:** the product manager, 2026-10-04 (ruling); `encore-install.sh:42-48`; R-2; constraints.md C-1
- **Touches:** debt.md D-A20 (taken), constraints.md C-1 (taken)

## 2026-10-04 — open and unplanned: one discovery, or a drop-in the uninstaller has to remove
- **Kind:** question
- **Fact:** D-A19's fix replaces four constructed paths with one discovery. The further question is whether the *unit* should stop shipping literal paths at all, and the installer instead write a `encore-kiosk.service.d/` drop-in from what it discovered — one discovery feeding both the password step and the runtime suppression. **Deliberately not planned and not sized.**
- **Why:** it is not a ticket-sized question. A drop-in is a new installed artifact, so `encore-uninstall.sh` must remove it and C-3's clean-undo promise depends on that — a contract across three files, which makes it an architecture question rather than an implementation one. The pull against it is C-3: every artifact the product installs is a thing the undo can forget, and the record already carries two items of that exact shape (D-A8, I-7). **The plan's step 5 makes this non-urgent rather than closed, and that is the right trade:** it leaves the unit asserting paths but adds an install-time check that the assertion is true on this machine, which removes the *silence* — the actual harm — and leaves the *duplication*, which is only a cost. A question that was "the list grows with no way to notice a missing line" becomes "the list grows". Not decided here.
- **Source:** the senior engineer's plan for item 16, 2026-10-04; constraints.md C-3; debt.md D-A19
- **Touches:** debt.md D-A19, interfaces.md, constraints.md C-3

## 2026-10-04 — D-A20 overclaimed: the architecture refusal moved, it did not end
- **Kind:** debt
- **Fact:** D-A20 said the product "stops claiming anything about exotic architectures in either direction" and that an adopter on `riscv64` "gets whatever the packages and the compositor actually do". **Both are wrong.** On a Debian `riscv64` machine the plugin installs at `/usr/lib/riscv64-linux-gnu/remmina/plugins/remmina-plugin-secret.so`; the `find` at `encore-install.sh:249` locates it; the coverage check at `:282-285` greps `encore-kiosk.service`, whose list at `:35-38` does not name it; and the install dies. The fourth-triplet machine is **still turned away** — later, and with a far better message. Found by review of item 16 and confirmed by the product manager. D-A20 now carries the correction in place.
- **Why:** the refusal moved from an unconditional list of three processor names to a condition on the one thing that matters — whether this machine's plugin path is named in the unit. That is a real improvement: the old refusal was unconditional and keyed on a fact with no bearing on whether the product works, the new one is conditional and keyed on a fact that decides it, and the message names the exact line to add instead of saying "unsupported architecture", which R-2 authorises nobody to say. **R-2's cost is reduced, not eliminated.** The correction matters more than the facts: D-A20 is precisely the entry somebody opens in a year before deciding whether to restore or remove that refusal, and as first written it would have told them the problem was solved when it is relocated. The same overclaim is in `8827dd6`'s commit message — history stays, the record carries the correction, which is the discipline C-1 applies to the Python floor.
- **Source:** `encore-install.sh:249`, `:282-285`; `encore-kiosk.service:35-38` — read directly 2026-10-04. The `riscv64` path is read from Debian multiarch convention, not measured: no such machine exists here.
- **Touches:** debt.md D-A20 (taken), overview.md (taken). **For the product manager:** the `R-2` note in `solution.md` says the product "says nothing about unusual processors in either direction" and is too strong for the same reason — theirs to fix, and they asked for the mechanism wording first so the two halves agree.

## 2026-10-04 — the coverage check fails after the credential is stored, and it need not
- **Kind:** interface
- **Fact:** verified order in the shipped installer — packages `:144`, identity `:152`, profile `:192`, the `find` `:249`, **the password stored `:253`**, the unit copied `:271`, the coverage check `:282`. A machine whose layout the unit does not name is therefore converted most of the way and then refused, keeping an identity, a profile and a stored credential. **The check does not need to be there:** `install -m 644` at `:271` has just overwritten the installed unit with `$HERE/encore-kiosk.service`, so at `:282` the two are byte-identical by construction and the check is grepping a file whose content it dictated eleven lines earlier. It cannot see a hand-edit or a stale previous version, because `install` destroyed that evidence. Reading the installed copy rather than the source copy buys **no information**, and `$HERE` is set at `:19`. The earliest the block could run is immediately after the packages step at `:144`, find and check together.
- **Why:** the credential is the part that matters and it is not untidiness. D-A12 records the password reaching a `systemd-run` command line and possibly the journal; a conversion that fails after `:253` has paid D-A12's full cost for a terminal that will never exist. It does **not** save the person typing the password — that is prompted at `:117`, before the packages step, either way. **Two things stop this being a clear call.** Neither copy is complete: a grep of the unit file misses `InaccessiblePaths=` in a drop-in under `encore-kiosk.service.d/`, and the only exact check is the effective merged value (`systemctl show -p InaccessiblePaths`), which is *later* still — so the real fork is early-and-approximate against late-and-exact, and the shipped code is late *without* being exact, the one combination with nothing to recommend it. And an early source-copy check can refuse a machine that would have worked, if an administrator has already written a drop-in naming their layout — a false refusal, the same shape as the risk ADR-0008 tracks, narrow today only because `docs/troubleshooting.md` now tells people not to hand-edit the unit. **The equivalence is also a property of the sequence, not an invariant:** if the installer ever composes the unit instead of copying it — D-A19's open drop-in question — `$HERE` stops being the truth and a source-copy check becomes wrong. The two questions have to be answered together or the drop-in work silently invalidates the check.
- **Source:** `encore-install.sh:19`, `:117`, `:144`, `:152`, `:192`, `:249`, `:253`, `:271`, `:282-285` — read directly 2026-10-04. Ordering question raised by the product manager; the equivalence argument and the two counter-considerations are the architect's.
- **Touches:** debt.md D-A19 (taken), debt.md D-A12, ADR-0008

## 2026-10-05 — the two package lists now differ in length, not just in spelling
- **Kind:** stack
- **Fact:** `cb94d97` added `$H264_DECODER` to the single `PACKAGES=` line in the installer's family block — `openh264` on dnf, empty on apt. **So apt asks for seven packages and dnf asks for eight.** Until 2026-10-05 the two families asked for the same seven and differed only in two *names* (`remmina-plugin-rdp`/`remmina-plugins-rdp`, `pipewire-pulse`/`pipewire-pulseaudio`), which is the claim `stack.md`'s two-names table was built on. Verified on Fedora 44, 2026-10-05: `freerdp-libs-3.31.1-1.fc44` requires `libopenh264.so.8()(64bit)`; both `openh264-2.6.0-3.fc44` (repository `fedora-cisco-openh264`, enabled by default) and `noopenh264-2.6.0-4.fc44` (repository `fedora`) provide that soname; `openh264` carries `Obsoletes: noopenh264 < 1:0`.
- **Why:** the "same parts, two names each" framing was load-bearing in two directions and only one of them survives. It still holds that **no part is missing on either family** — the stub provides the library, so nothing is absent and nothing fails. It no longer holds that **the asymmetry is only nominal**: one family now needs a name the other must not be given, which is a different kind of difference and the kind that invites a second list or a branch further down. The installer resists that by keeping it as a variable in the one list; the record has to carry the same framing or the next reader restores the symmetry on the strength of a sentence in `stack.md`. The eighth package is also unwatched — it was added *after* the only dnf install ever observed (test 14b's install half, Fedora 44, 2026-10-05) — so the one name that differs in length is the one line of the install nothing has exercised.
- **Source:** `encore-install.sh` family block (`>>> family block` … `<<< family block`) and its packages step — read directly 2026-10-05. `rpm -q --requires freerdp-libs`, `rpm -q --obsoletes openh264`, `dnf repoquery --provides noopenh264` on the author's Fedora 44 machine, read-only under D-002. The unwatched-eighth-package point is the user's, confirmed against `docs/tests.md` test 14b.
- **Touches:** stack.md (taken, two-names section)

## 2026-10-05 — line numbers in stack.md have gone stale three times; the installer's own markers replace them
- **Kind:** stack
- **Fact:** `stack.md`'s two-names section cited `encore-install.sh:91-92` for the package list (now one line, `:87`) and `:83` for `kbd` (correct when written in September). The same section's later paragraph cited `:79-83` for the packages step (now the `case "$PKG_FAMILY"` block) and `:16`/`:18` for `chvt` (actually `encore-kiosk.service:39` and `:41` — and `:35` for `ProtectHome=` is `:58`). **Four stale references, none of them wrong when written.** All now point at named anchors instead: the installer's `>>> family block` / `<<< family block` markers, the `PACKAGES=` line, the `case "$PKG_FAMILY"` block, `ExecStartPre=`/`ExecStopPost=`. The old number is kept in brackets beside each, so the trail of what it used to say is readable.
- **Why:** this is a self-inflicted wound with a structural cause, not carelessness. `stack.md` exists **so that nobody has to re-derive the family difference from the installer** — and a line number is an instruction to go and read the installer, which is the exact behaviour the file was written to remove. Worse, a stale number is silently wrong: it still resolves to a line, so a reader is shown unrelated code rather than an error. The installer already carries durable anchors on purpose (the family-block markers exist to tell a maintainer where family-dependent names go), so pointing at them costs nothing and survives every edit above them. **The rule going forward: in `stack.md`, cite a named construct, never a line number.** This does not generalise to `NOTES.md`, which is a dated log and may cite whatever was true on the day.
- **Source:** the four references read against the files 2026-10-05; the observation that a second number had gone stale is the user's.
- **Touches:** stack.md (taken, throughout)

## 2026-10-05 — H-1: the hazard named, after six instances in three documents
- **Kind:** constraint
- **Fact:** named `constraints.md` H-1 — **a mechanism reports success without doing its job, because what it depends on is satisfiable without being satisfied.** Six instances already in the record under six different names: `systemctl status` reporting `active (running)` for ever (D-A2); `Wants=` succeeding when the terminal does not (D-A3, whose title is this hazard stated exactly); the installer's coverage loop passing over an empty `$SECRET_PLUGINS` (D-A19); a `systemd-analyze verify` check that passed against `./nope.service` because it looked for the *absence* of two strings (`docs/tests.md` test 14a check 2, since rewritten to require positive output); `noopenh264` providing `libopenh264.so.8()(64bit)` and decoding nothing (`stack.md`, D-037's withdrawal); and test 14b's install half passing before the `openh264` line existed. Three are guarded or repaired, three are open. H-1 carries the finding question — *if the thing this checks were absent or broken, would it report anything different?* — and the note that it must be asked when the check is **written**.
- **Why:** the pattern was found six times and connected never, which cost the project the fifth and sixth instances outright: `docs/tests.md` had already written down the general shape next to instance 4 and explicitly compared it to instance 3, and the packaging stub was then met as if it were new. **A hazard with no name cannot be transferred between layers** — finding it in a `for` loop over an empty list teaches nobody to look for it in a dependency resolver or a test record, because nothing links them. Instances 5 and 6 are the same defect one altitude apart, which is the argument for the name in one sentence. Deliberately **not** debt and **not** a constraint: it sets no number, forbids nothing and orders no work, and all six instances are recorded where they bite. It is a recognition aid for the seventh. Kept apart from `CONTRIBUTING.md`'s "do not reason from configuration to runtime", which is about how a *person* reads a machine; H-1 is about how a *mechanism* reports on itself.
- **Source:** the six instances read in place 2026-10-05 (`debt.md` D-A2, D-A3, D-A19; `docs/tests.md` test 14a check 2 and test 14b; `stack.md`). The observation that 5 and 6 are one hazard at two altitudes is the architect's, from this session; the coordinator asked for it to be named in the record rather than left in a log entry, and chose the hazard's permanence over its tidiness.
- **Touches:** constraints.md H-1 (taken), stack.md (cites it twice), 00-index.md (taken)

## 2026-10-05 — the decoder was missing from the parts table, the same omission `kbd` was
- **Kind:** stack
- **Fact:** added the H.264 decoder to `stack.md`'s main parts table: not pinned, **never observed on either family**, software decoding only, under D-036 and D-037's withdrawal. Also disambiguated the `—` in the "version seen working" column, which was carrying two meanings: for `kbd`, POSIX `sh` and PAM it means *present and working on the watched machine, no version worth recording*; for the decoder it means *no observation has ever established this part did any work*. The two families are unwatched for different reasons — on apt the real library was on the Ubuntu VM that produced a session, but nothing checked whether that session negotiated H.264 at all (the deciding profile settings are backlog item 13c's unexamined ones), and on dnf the name postdates the only watched install.
- **Why:** the file's own `kbd` precedent decides it — a part missing from that table means the record disagrees with a real machine, which is the one thing the table exists to prevent, and it read "five parts in this file and six on a real machine" for two weeks. The `—` disambiguation matters more than the row: without it the new row reads as one more part whose version nobody bothered to write down, which is the opposite of the point. **And the first draft of that paragraph overclaimed in the other direction** — it said the decoder had never been exercised on any machine, which is false for apt, where a session was watched with the real library installed. Corrected before it shipped. Claiming too little is still claiming wrongly, and this is H-1's neighbourhood: a working session is not evidence about the decoder, but it is not evidence against it either.
- **Source:** `stack.md`'s parts table and the `kbd` paragraph beneath it; the Ubuntu 26.04 observation of 2026-09-23; `docs/tests.md` test 14b. The parts-table row was the architect's recommendation and the coordinator's call.
- **Touches:** stack.md (taken), 00-index.md (taken)

## 2026-10-05 — folded in: the uninstaller is now a second shipped copy of the package names
- **Kind:** interface
- **Fact:** `stack.md` gained a paragraph from another session while this one was editing the same file, recording that `encore-uninstall.sh` carries its own copy of both families' package lists in a `>>> leftovers block` region, because it removes no packages (R-11) and prints them instead, and cannot read the installer's copy — the installer need not still be on the machine and `encore-install.conf` records nothing about the family. **Verified rather than assumed:** the leftovers block's dnf arm does include `openh264`, its apt arm lists seven names, and its no-package-manager arm names only the five identical ones and admits the rest under `LEFT_UNNAMED` instead of guessing. The two lists agree today and `docs/tests.md` 14a check 7 compares them as strings.
- **Why:** taken into the record as correct rather than queried, and worth logging for two reasons. It is the **first duplication of the family names outside the installer**, which makes "the installer is the authority, a disagreement is a defect in the uninstaller's copy" a contract rather than a preference — and that contract is exactly what the eighth package tests, since `openh264` had to be added in two files. It also follows the rule written in this same file hours earlier without having been told: it cites a named marker, not a line number. The string comparison in 14a check 7 is the right guard and is **not** an H-1 instance — it fails loudly on drift and cannot pass vacuously, because both sides must be non-empty to match.
- **Source:** `encore-uninstall.sh` leftovers block, read 2026-10-05 (read-only; the file is another session's and was not edited). `docs/tests.md` 14a check 7.
- **Touches:** stack.md (already written by the other session), interfaces.md (the two-copy contract may belong there as well — not taken)
