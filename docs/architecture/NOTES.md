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
