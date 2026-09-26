# Interfaces — the contracts, and how stable each is

There is no network API and no code-to-code API. Every contract here is a
**file, a path, or a filesystem convention**, which makes them easy to miss and
easy to break silently. They are listed so a change can name its callers.

**Names corrected 2026-09-23** to the ones D-022 and D-023 fixed on 2026-09-13
and the code shipped on 2026-09-14. Every `file:line` below was re-checked
against the file on 2026-09-23, not merely renamed.

---

## I-1 — `encore-kiosk.target` is the activation surface

**Contract:** an administrator activates a terminal with
`systemctl isolate encore-kiosk.target` (now) or
`systemctl set-default encore-kiosk.target` (across reboots), and deactivates
by setting the default back plus a reboot.

**Callers:** the administrator, by hand; `encore-install.sh:165-166`, which
prints both commands verbatim and is therefore the authority a stranger reads;
`encore-uninstall.sh:81-97`, which tests for this exact target name before
restoring the previous default; `README.md`; `docs/tests.md` Tests 4 and 7.

**Stability:** **stable and public.** This is the product's whole user
interface for R-4, R-9 and R-11. It appears in documentation a stranger reads.
Changing the target name after publication breaks every written instruction in
the wild — and now also breaks the uninstaller's string comparison silently,
which would leave a machine booting into a terminal that no longer exists.

**`set-default` is confirmed as the intended mechanism, 2026-09-23.** It was
marked `assumed` here; the installer and uninstaller both use it, and
`docs/product/NOTES.md` (2026-09-21 handoff) states that an activation which
does not outlast a restart does not satisfy R-8. `isolate` is the
until-reboot form and `set-default` is the lasting one; both are offered
deliberately.

**Unresolved, and it is the isolate half:** `systemctl isolate` on a machine
already running a desktop did **not** bring the capability's console to the
foreground. Whether a machine that *boots* straight into
`encore-kiosk.target` behaves the same way is **untested** — the reboot test
(Test 7) has never been run. Both branches matter: if boot is also affected,
`ExecStartPre=+/usr/bin/chvt 7` is not sufficient and the console choice is
wrong; if only `isolate` is affected, the fault is in switching away from a
live session and the lasting activation path is sound. Neither is established.

---

## I-2 — the service takes `/dev/tty7`

**Contract:** `encore-kiosk.service:27-28` claims `/dev/tty7` via `TTYPath=`
and registers `UtmpIdentifier=tty7`; `:16` brings that console to the
foreground before the compositor starts and `:18` returns it to tty1 on stop.
Consoles 1–6 remain ordinary text logins.

**Callers:** the person at the terminal, who can leave the session by switching
console (D-017); the administrator standing at the machine.
`encore-install.sh:54-56` tells the administrator this in writing.

**Which key, exactly.** `Ctrl+Alt+F1` through `Ctrl+Alt+F6` reach consoles 1–6;
**which of them gives a login prompt varies by machine**, and the kiosk holds
tty7. This file previously said `F1`, `constraints.md` said `F2` and `NOTES.md`
said `F2`; all three were wrong to name one key. Corrected 2026-09-23 from the
author.

**Stability:** **fragile, and observed to be fragile.** On many current
distributions `tty7` is where a display manager already sits. Worse, on
2026-09-14 the compositor claimed the console while its session was not the
active one, and then froze console switching and took 90 seconds to stop — the
contract was held by something that had not been granted it. `chvt 7` at
`:16` is the current answer and it is not established for the boot path
(see I-1).

**Note also:** `cage -s` (`:17`) is what permits console switching at all. The
contract in this section only exists because of that flag.

---

## I-3 — the profile location

**Contract, two halves that do not agree.**

- What the runner accepts: **the first `*.remmina` file found** at
  `/var/lib/encore/.local/share/remmina/`, at depth 1
  (`encore-kiosk.sh:6`), in Remmina's own key/value format.
- What the installer writes: exactly `encore-kiosk.remmina` at that path
  (`encore-install.sh:26`, `:118-124`), followed by a check that there is
  exactly one profile present (`:131-132`).

**Callers:** `encore-install.sh` (writes it), `encore-kiosk.sh` (reads it),
`encore-uninstall.sh:117` (deletes it with the home directory),
`docs/tests.md` Test 3 and Test 6, `docs/troubleshooting.md`, and an
administrator placing a file by hand.

**Stability:** **unstable, and it is the contract that matters most.** `head -n
1` over `find` has no defined order, so two profiles on one machine give a
nondeterministic target host. The installer's count check makes that
unreachable *on a fresh install* and does nothing afterwards: anyone who copies
a second profile in, or restores a backup beside the live one, gets a terminal
that may connect somewhere else after the next restart, with no error.

**Corrected 2026-09-23:** this section used to name "the configuration step
(not built)" and "the packaging (not built)" as future callers. The
configuration step is built and is `encore-install.sh`. The packaging will
never exist (D-027).

---

## I-4 — the run-as identity and its home

**Contract:** a system user `encore`, group `encore`, home `/var/lib/encore`,
stated in four places now: `encore-kiosk.service:7-8`, `:10-11`,
`encore-kiosk.sh:3`, and `encore-install.sh:25`, `:88-94`.

**Callers:** the installer (creates the user and the directory, and adds it to
`video`, `input` and `render` — `encore-install.sh:94`); the uninstaller
(`userdel -r`, `encore-uninstall.sh:112-117`); the profile path in I-3;
Remmina's own config directory; every path in `docs/troubleshooting.md`.

**Stability:** **stable in intent, duplicated in fact.** `HOME` is now set in
three places. The script's copy exists because it is also runnable by hand;
that is a reasonable reason, but it must be recorded as a deliberate
duplication rather than left to be "cleaned up" by someone later. The
installer's copy is not optional — it is what creates the directory the other
two assume.

**The group memberships are part of this contract and were never argued for.**
`video,input,render` is what lets the compositor reach the GPU and the input
devices. It is also more than `constraints.md` C-4 describes. Named here so it
is visible; see `debt.md` item D-A10.

---

## I-5 — the script's executable path

**Contract:** `/usr/local/bin/encore-kiosk.sh`, written by
`encore-install.sh:154`, invoked by `encore-kiosk.service:17`, removed by
`encore-uninstall.sh:106`.

**Stability: stable. This changed on 2026-09-23 and it changed in our favour.**
This section used to argue that `/usr/local/` is reserved for the local
administrator by the Filesystem Hierarchy Standard and Debian policy, that a
`.deb` may not ship into it, and that packaging would have to move the script
to `/usr/bin/` or `/usr/libexec/`. **D-027 says there will never be a package.**
The installer *is* the local administrator, acting on that machine, which is
precisely what `/usr/local/bin` is for. The contract is correct as it stands
and is no longer pending anything.

**What survives of the old objection:** the path is now genuinely public,
because it is what an administrator types to run the runner by hand while
debugging (`docs/troubleshooting.md`), so it is as hard to change as the unit
names are.

---

## I-6 — the RDP connection itself

**Contract:** RDP to the host named in the profile, with the username and the
stored password from that profile.

**Callers:** the machine being connected to, which is out of scope and which we
may not constrain (D-002).

**Stability:** **stable by necessity.** We do not own the far end, so this
contract can change without us being told. The product must treat every failure
of it as normal operation, not as an error (R-18, D-026).

**Identity is part of this contract, as of 2026-09-13.** R-16 was clarified to
mean *the* machine it was configured to connect to, not something answering to
its name. The contract is therefore not "RDP to a hostname" but "RDP to a
host whose identity we can check" — and the shipped template does not check it
(`cert_ignore=1` at `encore-kiosk.remmina.template:46`, `ignore-tls-errors=1`
at `:107`). That makes R-14 and R-16 one question: a credential handed to an
impostor was never protected by being hard to read. See `debt.md` items D-A8,
D-A5 and D-A7.
(Source: product manager report, 2026-09-13. Citation moved 2026-09-23 from
`group_rdp_server_server.remmina`, which is an untracked personal profile at
the repository root and will never exist on an adopter's machine, to the
template, which is the shipped artifact.)

---

## I-7 — the install record

**Added 2026-09-23. This contract did not exist before the installer did.**

**Contract:** `/var/lib/encore/encore-install.conf`, a shell-sourceable
key/value file written by `encore-install.sh:105-112` and parsed by
`encore-uninstall.sh:29-39` with `sed`. Two keys today:
`PREVIOUS_DEFAULT_TARGET=` and `INSTALLED_ON=`. Root-owned, mode 644,
deliberately not writable by `encore` — the identity the product runs as must
never be able to edit the note that decides what the machine turns back into.

**Callers:** the uninstaller, and nothing else. A human reading it years later
is the second caller and the reason it carries comments.

**A second caller and two more keys are decided but not built** (ADR-0009,
2026-09-23). The runner's pre-flight needs the target's address, and this file
is where it will get it: `RDP_HOST=` and `RDP_PORT=`, written by the installer,
the port always explicit so no reader supplies a default. This is the "keys may
be added" case the stability note below already permits; the two original keys
are untouched. Two consequences for whoever builds it: the runner becomes a
reader of a file it does not write, so the mode-644 root-owned arrangement
below is now protecting two things rather than one; and machines converted
before this exists will not have the keys, so **absence must stay a tolerated
state**, exactly as the failure behaviour below already requires.

**Stability:** **stable, and it is a one-way door in miniature.** It is written
on every machine ever converted and read by an uninstaller that may be a much
later version. Keys may be added; the two above may never be renamed or
removed, or an old machine becomes one that cannot be given back without a
human remembering — which is exactly the failure it was created to remove.

**Failure behaviour, and it is deliberate:** if the file is missing or the
recorded target no longer exists on the machine, the uninstaller offers a
choice of `graphical.target` or `multi-user.target`
(`encore-uninstall.sh:41-66`) and, if the operator declines, leaves the default
alone with a loud warning (`:88-92`). It never guesses. The list is restricted
to those two on purpose — most isolatable targets would be a disaster as a
permanent default.
