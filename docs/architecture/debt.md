# Debt — what is knowingly wrong, and what would repay it

All entries dated 2026-09-13, found by reading the prototype on the day the
architecture record was opened. None was observed at runtime; every one is a
code-read finding. Severity is about the user harmed, not the effort.

**Nothing here is deployed on the development machine.** `which remmina cage`,
`getent passwd kiosk` and `ls /var/lib/kiosk` all came back empty on
2026-09-13, and no unit is installed. The terminals themselves are elsewhere
and unobserved. Any item marked `assumed` stays that way until somebody runs
it on real hardware.

`BACKLOG.md` already tracks *unbuilt* work against requirements. This file
tracks *built things that are wrong or that will bite*. Where they overlap,
this file says why, and `BACKLOG.md` says when.

---

## D-A1 — The no-profile fallback hands the terminal to the person sitting at it
**Severity: highest. This is the product's central promise failing.**

**What:** if no profile is found, the runner executes plain `remmina -k`
(`remmina-kiosk.sh:13`), which starts Remmina's own user interface.

**Why it matters:** R-6 and D-004 say the person at the terminal sees the
remote machine and nothing else. Remmina's UI is a local application with a
connection editor, a preferences dialog, and a file chooser. A child in front
of a terminal whose profile is missing or misnamed is given an application that
can open arbitrary hosts and browse the filesystem. The problem statement calls
this exact outcome out: "a half-converted machine is worse than an unconverted
one".

**Compounding it:** `-k` alone does not harden the UI. Upstream added
`--disable-toolbar`, `--enable-fullscreen` and `--enable-extra-hardening`
precisely because kiosk mode by itself does not disable escape hotkeys, tabs,
or the exit prompt.
([Remmina merge request 2392](https://gitlab.com/Remmina/Remmina/-/merge_requests/2392))

**What repays it:** no profile must mean *no session*, never *a local
application*. Show a static "not configured" screen, or let the unit fail
loudly so the administrator sees it. Plus the hardening flags on every
invocation.

**But deleting the fallback is not a free win, and the replacement is not
decided.** Removing the bare `remmina -k` leaves a blank console when no
profile is present. Blank is unambiguously safer than a file chooser and
should ship first. Showing a "not configured" message instead requires adding
a component, because `cage` was chosen precisely so that nothing can draw
beside the session (ADR-0002) — and `docs/product/users.md` lists "a black
screen" as one of the reasons the person at the terminal gives up, so the
blank is a real cost rather than a clean win. Recorded so the trade is not
discovered later and mistaken for an oversight. See the open contradiction in
`00-index.md`. (Source: `remmina-kiosk.sh:13`; ADR-0002;
`docs/product/users.md`, 2026-09-13.)

**Scheduled, and scheduled together with D-A2.** Both are written into
`BACKLOG.md` under its "Built and wrong" heading, separate from "Decided, not
built", and flagged to be fixed and tested as one piece of work. They are the
same failure wearing two hats: if Remmina does not exit on a dropped
connection — and upstream says it does not by default
([issue 3113](https://gitlab.com/Remmina/Remmina/-/issues/3113)) — then the
restart layer never fires *and* the person at the terminal is left looking at
the client's own UI. Fixing the supervision without fixing the fallback leaves
a child staring at a dialog; fixing the fallback without checking the exit
behaviour leaves R-8 absent rather than duplicated.
(Source: `remmina-kiosk.sh:8,13`, `remmina-kiosk.service:13`.)

**The claim this was a defect against has since been withdrawn.** After the
architecture report, the product manager downgraded R-6 from `real` to
`intended` and retired the phrase `verified in code` across the whole
requirement set in favour of "read in code, never observed". So D-A1 is no
longer a defect against a standing claim — but it remains the thing standing
between `intended` and `real`, and the severity above is unchanged.
(Source: product manager report, 2026-09-13; `docs/product/solution.md` R-6.)

---

## D-A2 — Two layers promise recovery, so neither is accountable
**Severity: medium. Operability, and the reason nobody will know it is broken.**

**What:** `remmina-kiosk.sh:8` loops forever; `remmina-kiosk.service:13` sets
`Restart=always`. The script never exits, so the restart policy can never fire.

**Why it matters beyond tidiness:** because the script never exits, **the unit
never enters a failed state**. A terminal that has been failing to connect for
three days looks perfectly healthy to `systemctl status`. There is no metric,
no alert, and no signal to the administrator — who, by R-10, is managing this
machine without a screen. The product manager already flagged the duplication
(handoff, 2026-09-13); the invisibility is the part that actually hurts.

**What repays it:** pick one owner. Recommendation: delete the loop and let
systemd supervise, with `Restart=always` plus a `StartLimitIntervalSec` /
`StartLimitBurst` so repeated fast failures eventually surface as a failed
unit. systemd already does backoff, logging and rate limiting; the shell loop
does none of them.

**Caveat on that recommendation, and it is unresolved.** It assumes Remmina
exits when a connection drops. Upstream says it does not do so by default
([issue 3113](https://gitlab.com/Remmina/Remmina/-/issues/3113)), in which
case removing the loop produces no failure signal either — the process simply
sits there. The exit behaviour must be established on a real machine before
this fix is called done. See the open contradiction in `00-index.md`.

**Scheduled with D-A1**, in `BACKLOG.md` under "Built and wrong": one piece of
work, fixed and tested together, for the reason given at the end of D-A1.

**What it is waiting on:** whether anybody is owed a signal when a terminal
fails silently is an open product question (Q-5 in `NOTES.md`, Q-P3 in the
product record), and it decides the size of this fix.

---

## D-A3 — `Wants=` means the target succeeds even when the terminal does not
**Severity: medium.**

**What:** `kiosk.target:5` uses `Wants=remmina-kiosk.service`.

**Why it matters:** if the service cannot start at all, the machine still
reaches `kiosk.target` and sits there with no graphical session. Combined with
D-A2, the machine reports itself healthy while showing nothing.

**What repays it:** decide deliberately between `Wants=` and `Requires=`, and
write the reason down. `Requires=` makes the failure visible; it also means a
failing service tears the target down, which needs a stated safe landing place.

**Decide it with D-A2**, and before publication — ADR-0003 already names the
`Wants=` / `Requires=` question as one of the two things to settle before the
first published release. There is no point making the target's failure visible
while the service can never fail.

---

## D-A4 — `ProtectHome=true` hides `/run/user`, which is where Wayland and audio live
**Severity: high. Suspected to prevent the thing working at all.**

**What:** `remmina-kiosk.service:27`. `ProtectHome=true` makes `/home`, `/root`
**and `/run/user`** appear empty to the unit.

**Why it matters:** `$XDG_RUNTIME_DIR` is `/run/user/<uid>`. That is where the
Wayland display socket lives, and where PipeWire's `pipewire-0` and
`pulse/native` sockets live. With that path blanked, the compositor's socket
and the audio sockets are invisible. This is a plausible cause of the prototype
"not fully working", and it makes C-5 / R-12 (audio both directions)
unreachable no matter what the profile says.

**Status:** `assumed` — reasoned from systemd's documented semantics, not
observed. **This is the first thing to test on a real machine.**

**What repays it:** `ProtectHome=tmpfs` plus `BindPaths=/run/user/%U`, or
`ProtectHome=read-only`, or move to a user unit (see D-A6). Note the home
directory is `/var/lib/kiosk`, which is outside `/home`, so `ProtectHome` is
buying us very little here in the first place.

---

## D-A5 — The stored credential is obfuscated, not protected
**Severity: high, and it is the thing a prospective adopter will check.**

**What:** the profile's `password=` is 3DES-encrypted with a key sitting in
`remmina.pref` in the adjacent directory. Recoverable in a few lines of script;
there is an off-the-shelf Metasploit module for it.

**Why it matters:** R-14 promises the credential "is not readable by anyone who
picks the machine up". The current mechanism does not deliver that, and the
product record correctly still marks R-14 `intended`. The risk is that someone
later reads "encrypted" in the profile and marks it done.

**What repays it:** design work, not a flag. The honest options are libsecret
with a keyring unlocked at boot (which means the unlock secret is on the disk
too, so it may be no better), full-disk encryption on the terminal (pushes the
problem to the adopter and conflicts with "no hardware assumed"), or accepting
the exposure explicitly and narrowing what the credential can reach on the far
host. **The last one is probably the real answer**, and it is a product
conversation, not an architecture one. See question Q-2 in `NOTES.md`.

**Worse than described above: the key travels too.** A profile's stored
password is decrypted with a key held in a *separate* file,
`~/.config/remmina/remmina.pref`. So the workflow ADR-0001 relies on — build
the connection in Remmina's GUI on a machine you already use, then copy the
file to the terminal — is really "copy the secret and its key together". The
exposure is not confined to the terminal; it is on every machine the profile
was built on. (Source: [Remmina FAQ](https://remmina.org/faq/); profile format
read at `group_rdp_server_server.remmina:2`, 2026-09-13.) The same fact is the
most likely way a first install fails for a non-obvious reason — see
`data.md`.

---

## D-A6 — A system unit is doing a user session's job
**Severity: low now, structural later.**

**What:** the capability runs as a system unit with `User=`, `PAMName=login`,
and manual TTY handling, to reproduce what a logind user session provides for
free.

**Why it matters:** `%t`, `XDG_RUNTIME_DIR`, the seat, the Wayland socket and
PipeWire are all correct by construction in a user unit and are all hand-built
here. Every one of D-A4's symptoms comes from this.

**What repays it:** evaluate `systemctl --user` with lingering enabled, or a
plain autologin on a TTY with the session started from there. Not urgent, but
it is the shape the rest of the ecosystem expects.

---

## D-A7 — There is no configuration step, so the product exists only on the author's machines
**Severity: highest structurally. Already `BACKLOG.md`'s "largest hole".**

**What:** the host, username and password reach the terminal by an
administrator hand-placing a `.remmina` file. Discovery is `find | head -n 1`
(`remmina-kiosk.sh:6`) with no defined order when there is more than one.

**Why it matters:** R-4 and R-5 both stand on this. Until it exists, R-13 (a
stranger can judge the product) cannot be honestly written either, because
there is nothing to describe.

**What repays it:** an ADR deciding where configuration lives, how it is set,
and how it is changed. It is a **one-way door** — it becomes a file format
strangers have on disk — so it deserves the long argument. **Size: L.**

---

## D-A8 — The RDP session accepts any certificate
**Severity: medium.**

**What:** `cert_ignore=1` and `ignore-tls-errors=1`
(`group_rdp_server_server.remmina:39,97`).

**Why it matters:** the terminal will hand its stored credential to anything on
the LAN that answers to the configured name. That defeats most of what
encrypting the credential at rest was for, and it sits badly with D-012's
promise that the terminal reaches "the machine it was configured to connect
to". It currently reaches *whatever claims to be* that machine.

**There is now a requirement behind this, not just an architect's objection.**
R-16 was clarified on 2026-09-13 to state that "the machine it was configured
to connect to" means *that machine and not something answering to its name*.
That makes R-14 and R-16 one question: a credential handed to an impostor was
never protected by being hard to read. Certificate pinning and credential
storage are therefore one design conversation, not two.
(Source: product manager report, 2026-09-13; `group_rdp_server_server.remmina:39,97`.)

**What repays it:** pin the host's certificate during the configuration step.
This is a natural companion to D-A7 and to D-A5, and all three should be
decided together, inside the configuration design.

---

## D-A9 — The clipboard channel is open and was never argued for
**Severity: low.**

**What:** `disableclipboard=0` (`group_rdp_server_server.remmina:30`).

**Why it matters:** D-012 lists what the capability may reach — screen,
keyboard, mouse, audio, the one host. The clipboard is a bidirectional data
channel that is not on that list. D-012 says anything extra "would have to be
argued for individually". Nobody argued for this one; it is a default.

**What repays it:** one line in the profile, plus a note saying which way it
was decided and why.

---

## D-A10 — Packaging conflicts already visible
**Severity: low, but cheap to fix now and annoying later.**

- `/usr/local/bin/remmina-kiosk.sh` (`remmina-kiosk.service:12`) is reserved
  for the local administrator; a `.deb` may not install there.
- Nothing creates the `kiosk` user, the `kiosk` group, or `/var/lib/kiosk`.
- No versions are pinned for Remmina or cage anywhere.
- `HOME` is set in two places (`remmina-kiosk.service:11` and
  `remmina-kiosk.sh:3`). Deliberate — the script is runnable by hand — but
  record it, or someone will "tidy" one of them away.
- `ProtectSystem=yes` is the weakest of the three levels and leaves `/etc`
  writable. `strict` or `full` is likely correct here and costs nothing.

---

## D-A11 — The credential file is sitting in the repository
**Severity: highest for publication. Already in `BACKLOG.md` hygiene.**

`group_rdp_server_server.remmina` at the repository root carries a hostname, a
username and a recoverable password. It is currently untracked. **It must never
be committed**, and the repository needs a `.gitignore` before anything else is
added, because one careless `git add -A` publishes it permanently to history.
