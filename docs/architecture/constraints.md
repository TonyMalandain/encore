# Constraints — the numbers and the hard edges

Most of this project's constraints are not performance numbers. They are
**absolutes**: things that must be true one hundred percent of the time,
because the user is a child and the failure mode is an unmanaged computer in a
bedroom. Absolutes are harder than percentages, and they are what the design
must be judged against.

---

## C-1 — Environment (from D-003, R-1, R-2)

| Constraint | Value |
|---|---|
| Package manager | apt family only |
| Display server | Wayland only |
| Init | systemd only |
| Hardware | none assumed — 32-bit and ARM must be considered in scope |
| Host distribution | out of scope; the author's own host is a distribution we do not support |

**Consequence nobody has priced yet:** "no hardware assumed" plus "Wayland
only" is a real tension on old machines. A 2009 iMac or an old PC with an
ancient GPU may have no working Wayland path at all. `BACKLOG.md` already asks
whether those two machines qualify. Until someone runs it, R-2 is a claim.

---

## C-2 — The kiosk absolute (D-004, D-005, R-6, R-8)

**There must be no reachable state in which the person at the terminal sees
anything other than the remote machine's login screen or session.** Not a
desktop, not a settings panel, not an error dialog, not a terminal prompt, not
the remote client's own user interface.

This is one hundred percent, not "almost always". The current design has at
least two ways to fall short of it — see `debt.md`, items D-A1 and D-A4.

---

## C-3 — Reversibility absolute (D-007, R-11)

**Deactivation must require no repair by hand.** Anything that rewrites a
system file in place, rather than adding a file beside it, breaks this. The
current design is well-behaved here: it adds units, adds a user, adds a script,
and flips one symlink.

---

## C-4 — Privilege ceiling (D-012, R-15, R-16)

The running capability may reach:

- the screen, the keyboard, the mouse, the audio devices
- the one host named in its profile

and nothing else. In particular: no root, no other hosts on the LAN, no other
users' data, no package management, no storage beyond its own home.

**Measured against the code:** `NoNewPrivileges=true`, `ProtectSystem=yes`,
`ProtectHome=true` and `User=kiosk` are present
(`remmina-kiosk.service:7,26-28`). They cover the privilege half. **The network
half is entirely unbuilt** — there is no `IPAddressDeny=`, so the process can
reach every host the machine can reach. `ProtectSystem=yes` is also the weakest
of the three settings; it leaves `/etc` writable.

---

## C-5 — Audio absolute (D-009, D-014, R-12)

Sound out through the terminal's speakers and, where a microphone exists, in
through the terminal's microphone — **as the default, with nobody choosing a
device from a list**, and a terminal with no microphone must still work fully.

**Measured against the code:** the shipped profile sets `sound=off` and leaves
`microphone=` empty (`group_rdp_server_server.remmina:104,92`). Audio is not
merely unbuilt; the current configuration switches it off.

---

## C-7 — Fleet size: two or three terminals, one household

**The number this design is built for is 2–3.** Not a dozen, not a site.

This is the smallest-looking constraint in the file and one of the most
load-bearing. It is the whole reason for ADR-0005 (assemble from parts rather
than adopt a thin-client platform), and it is why the absence of central
configuration management is a reasonable position rather than a glaring hole.

**What it licenses:** configuring each terminal individually; no fleet view; no
push of changes; no inventory; no rollout mechanism.

**When it stops holding:** watch for the symptom, not the count — the first
time a change has to be applied to every terminal by hand and one of them gets
missed. Around a dozen machines, or terminals in more than one household, the
platforms that were rejected start being cheaper than the assembly.

**Source:** the author, 2026-09-13.

---

## C-6 — No clock, but one real timing number

`RestartSec=3` and `sleep 2` are the only numbers in the system
(`remmina-kiosk.service:14`, `remmina-kiosk.sh:15`). Neither has a stated
reason and neither has been tuned against anything. There is **no stated
requirement for how quickly a terminal must return to a login screen** after a
drop. If one matters, it belongs in the product record, not here.

---

## The conflict this record must not hide

**R-6 (nothing but the remote session) and R-10 (the administrator can reach
the machine without the screen) are served by the same mechanism, in opposite
directions.**

The design leaves consoles 1–6 as text logins so the administrator can get in.
The person at the terminal can press `Ctrl+Alt+F2` and land on one of them. A
child without credentials cannot log in, so nothing is *granted* — but the
screen has stopped being the remote session, which is what C-2 says must never
happen, and a blank console with a cursor is exactly the kind of thing a child
calls an adult about.

Both reasons still hold. This is a genuine **Conflict**, not drift, and the
architect does not get to pick. It is put to the author in `NOTES.md` as
question Q-1, and to the author by the product manager as Q-P1.

The trade-off: disabling VT switching hardens R-6 and makes R-10 depend
entirely on the network being up, which risks locking a household out of its
own hardware.

**Correction, 2026-09-13, from the product manager, and it is right.** My first
framing of this called that "the exact cost D-006 already accepted". It is not.
D-006 accepted the lock-out risk *while a text console still existed as a way
in*. Closing that console does not re-accept the same cost — it accepts a
strictly larger one, with the last local route removed. Pointing the author at
D-006 as precedent would have understated what they were agreeing to. The
question must be put as a new cost, not a settled one.
