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
