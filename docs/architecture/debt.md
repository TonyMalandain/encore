# Debt — what is knowingly wrong, and what would repay it

Items D-A1 to D-A11 were found by reading the prototype on 2026-09-13, the day
the architecture record was opened. Severity is about the user harmed, not the
effort.

**Names and citations corrected 2026-09-23** to the ones D-022 and D-023 fixed
on 2026-09-13 and the code shipped on 2026-09-14. Every `file:line` in this
file was re-checked against the file on 2026-09-23 rather than renamed, because
the files were rewritten and the lines moved.

**Several of these are no longer code reads.** The header used to say nothing
here had ever been deployed or observed — `which remmina cage`,
`getent passwd kiosk`, `ls /var/lib/kiosk` all empty on the development machine
on 2026-09-13. That was true then and is not true now. A terminal reached a
remote session on a VM on 2026-09-14 and again on a clean Ubuntu 26.04 VM on
2026-09-23. Where an item has been watched happening, it now says so and gives
the date; where it is still reasoned from documentation, it still says
`assumed`.

`BACKLOG.md` tracks *unbuilt* work against requirements and decides what gets
done. This file tracks *built things that are wrong or that will bite*, and
decides nothing — it is a record of compromises taken, with what would repay
each one.

---

## D-A1 — The no-profile fallback hands the terminal to the person sitting at it
**Severity: highest. This is the product's central promise failing.**

**What:** if no profile is found, the runner executes plain `remmina -k`
(`encore-kiosk.sh:13`), which starts Remmina's own user interface.

**Observed, not reasoned, since 2026-09-14.** `docs/tests.md` Test 3 does
exactly this and records the result: the client's own interface appears, with a
connection editor and a file chooser. It was a code read when this item was
written; it is now a watched fact.

**Why it matters:** R-6 and D-004 say the person at the terminal sees the
remote machine and nothing else. Remmina's UI is a local application with a
connection editor, a preferences dialog, and a file chooser. A child in front
of a terminal whose profile is missing or misnamed is given an application that
can open arbitrary hosts and browse the filesystem. The problem statement calls
this exact outcome out: "a half-converted machine is worse than an unconverted
one".

**Compounding it, and narrowed 2026-09-23:** `-k` alone does not harden the UI.
Upstream added `--disable-toolbar`, `--enable-fullscreen` and
`--enable-extra-hardening` precisely because kiosk mode by itself does not
disable escape hotkeys, tabs, or the exit prompt.
([Remmina merge request 2392](https://gitlab.com/Remmina/Remmina/-/merge_requests/2392))
The **profile branch now carries all three flags** (`encore-kiosk.sh:10`), so
this applies only to the fallback branch at `:13`, which is still bare
`remmina -k`. The two branches of one `if` are hardened differently, which is
the kind of asymmetry nobody notices until the unhardened one is the branch
that runs.

**And hardening the client does not close it anyway, observed 2026-09-14 and
2026-09-23.** With the flags on and a profile present, the client still put
windows on the screen the person at the terminal could see and click: its own
main window above the session, a credential prompt behind it, and on 2026-09-23
a certificate dialog after a failed connection. `cage` offers no way to raise
or switch windows, so some of those cannot even be answered. C-2 is breached on
the ordinary path, not only on the no-profile path.

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
`00-index.md`. (Source: `encore-kiosk.sh:13`; ADR-0002;
`docs/product/users.md`, 2026-09-13.)

**The cost argument above was wrong, and the correction is dated 2026-09-21.**
"Showing a message requires adding a component" assumed the message had to be
drawn *inside* the session, as a window beside it. It does not: the runner can
write to the console before the compositor ever starts. The architect reported
this to the product manager on 2026-09-21 — roughly twenty lines of shell, no
new package, no new window — and it is recorded in `docs/product/NOTES.md`. So
the collision with ADR-0002 is narrower than this item and the index both
claimed: ADR-0002 still forbids drawing *alongside a running session*, and says
nothing about the screen when there is no session to draw alongside, which is
exactly the no-profile case.

**Scheduled, and scheduled together with D-A2.** Both are written into
`BACKLOG.md` under its "Built and wrong" heading, separate from "Decided, not
built", and flagged to be fixed and tested as one piece of work. They are the
same failure wearing two hats: if Remmina does not exit on a dropped
connection — and upstream says it does not by default
([issue 3113](https://gitlab.com/Remmina/Remmina/-/issues/3113)) — then the
restart layer never fires *and* the person at the terminal is left looking at
the client's own UI. Fixing the supervision without fixing the fallback leaves
a child staring at a dialog; fixing the fallback without checking the exit
behaviour leaves R-18 absent rather than duplicated.
(Source: `encore-kiosk.sh:8,13`, `encore-kiosk.service:19`. "R-8" in this
paragraph was corrected to R-18 on 2026-09-23: R-8 was split on 2026-09-21 and
now covers surviving a restart, while a dropped connection is R-18.)

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

**What:** `encore-kiosk.sh:8` loops forever; `encore-kiosk.service:19` sets
`Restart=always`. The script never exits, so the restart policy can never fire.

**Still true on 2026-09-23.** ADR-0007 decided this on 2026-09-14 — systemd
owns recovery, the loop goes — and the decision is not built. The loop is at
`encore-kiosk.sh:8-16` and none of ADR-0007's directives
(`RestartPreventExitStatus=`, `RestartSteps=`, `RestartMaxDelaySec=`,
`StartLimitIntervalSec=0`) is in the unit. Decided is not built, and this is
the gap.

**Why it matters beyond tidiness:** because the script never exits, **the unit
never enters a failed state**. A terminal that has been failing to connect for
three days looks perfectly healthy to `systemctl status`. There is no metric,
no alert, and no signal to the administrator — who, by R-10, is managing this
machine from another machine. The product manager already flagged the
duplication (handoff, 2026-09-13); the invisibility is the part that actually
hurts.

**This item stopped being an argument on 2026-09-23. It was watched.** On a VM,
a connection failed, a clickable certificate dialog appeared on the terminal's
screen, and the journal recorded only that the service had started and a
session had opened. `systemctl` said active, the journal said healthy, the
screen said otherwise and the screen is the one surface
`docs/troubleshooting.md` tells you not to debug through. **Every channel
available to an administrator reported a healthy terminal while it was
stuck.** That is this item, exactly as written, occurring.

**The cause of that particular failure was never identified, and it is
recorded as unexplained rather than explained away.** A later clean reinstall
connected successfully; the most likely difference is stale files left by an
earlier session, but nobody established it. Writing down that we do not know is
worth more here than a plausible cause, because the same symptom — silence
everywhere but the screen — is the thing this item exists to name.

**What repays it:** pick one owner. **Decided 2026-09-14 as ADR-0007:** systemd
owns recovery, the runner becomes a launcher that `exec`s the client and never
retries. Delete the loop.

**The rate-limit half of the original recommendation is withdrawn.** It read:
"`Restart=always` plus a `StartLimitIntervalSec` / `StartLimitBurst` so
repeated fast failures eventually surface as a failed unit." That was written
on 2026-09-13, before D-020 was decided. D-020 says an unreachable machine
keeps trying **indefinitely**, and any burst limit is a promise to give up, so
ADR-0007 sets `StartLimitIntervalSec=0` instead. The consequence is that the
failure signal this item was written about **cannot come from the unit state
for the unreachable case** — only for the broken-configuration case, which
exits 78 (`CONFIG`) and does land in `failed`. Anything more than that is
`BACKLOG.md` item 13's subject, not this one's. (Source: D-020;
`systemd.service(5)` on `StartLimitIntervalSec=`, read 2026-09-14.)

**Two mechanism facts established 2026-09-14, both by reading source.**
`cage` returns its child's exit status as its own (`cage.c:199-213`,
`cage.c:722-726`), so an exit code written by the runner reaches systemd
through the compositor intact — this is what makes the exit-code scheme work at
all. And systemd's restart delay never decays on its own: `s->n_restarts` is
flushed only on a non-automatic start (`src/core/service.c:3623-3625`,
`:6073`), so running successfully for a month does not reset the backoff.
The cap in ADR-0007 is deliberately small for that reason.

**Caveat on that recommendation, and it is unresolved.** It assumes Remmina
exits when a connection drops. Upstream says it does not do so by default
([issue 3113](https://gitlab.com/Remmina/Remmina/-/issues/3113)), in which
case removing the loop produces no failure signal either — the process simply
sits there. The exit behaviour must be established on a real machine before
this fix is called done. See the open contradiction in `00-index.md`.

**Scheduled with D-A1**, in `BACKLOG.md` under "Built and wrong": one piece of
work, fixed and tested together, for the reason given at the end of D-A1.

**What it is waiting on:** whether anybody is owed a signal when a terminal
fails silently is an open product question (Q-5 in `NOTES.md`), and it decides
the size of this fix. Note D-026 (2026-09-21) makes it harder, not easier: an
unreachable target is now explicitly an ordinary event to be waited through
quietly, so "cannot connect" can never be treated as evidence of a fault, and a
genuinely broken terminal is indistinguishable from an outage for as long as an
outage could plausibly last.

**One thing that must move at the same time, or the fix causes a new fault.**
`ExecStopPost=+/usr/bin/chvt 1` (`encore-kiosk.service:18`) is harmless only
while the loop never exits. The moment the unit restarts on every dropped
connection, that line flips the foreground console to tty1 on every reconnect
and shows the person at the terminal a text login prompt — a C-2 breach through
the recovery path. It belongs on the deactivation path, not the restart path.
See ADR-0007, consequence 2.

---

## D-A3 — `Wants=` means the target succeeds even when the terminal does not
**Severity: medium.**

**What:** `encore-kiosk.target:5` uses `Wants=encore-kiosk.service`.

**Why it matters:** if the service cannot start at all, the machine still
reaches `encore-kiosk.target` and sits there with no graphical session. Combined with
D-A2, the machine reports itself healthy while showing nothing.

**What repays it:** decide deliberately between `Wants=` and `Requires=`, and
write the reason down. `Requires=` makes the failure visible; it also means a
failing service tears the target down, which needs a stated safe landing place.

**Decide it with D-A2**, and before publication — ADR-0003 already names the
`Wants=` / `Requires=` question as one of the two things to settle before the
first published release. There is no point making the target's failure visible
while the service can never fail.

**Closed 2026-09-14 by ADR-0007: `Wants=` stays, and here is the reason it was
missing.** Under ADR-0007 the service is the accountable object and its own
state tells the truth — `failed` with `status=78/CONFIG` for a broken
configuration, restarting for ever for an unreachable machine. `Requires=` adds
no signal that the service does not already carry, and it would tear the target
down on precisely the failure where a still, inspectable machine is worth most.
This item is now a recorded reason rather than an open question; it stops being
debt when the loop is removed alongside it.

---

## D-A4 — `ProtectHome=` had to be switched off, so the intended confinement is absent
**Severity: high. Rewritten 2026-09-23; it used to be the opposite item.**

**What it said when it was written (2026-09-13):** `ProtectHome=true` is
present and hides `/home`, `/root` **and `/run/user`**, which is where the
Wayland display socket and PipeWire's sockets live — so the compositor cannot
see its own socket, and this is a plausible cause of the prototype not working.
It was marked `assumed` and named as the first thing to test on a real machine.

**What happened:** it was tested. The prediction was right, and the setting was
turned off to reach a working session on 2026-09-14 — then turned back on to
confirm the failure and off again. `encore-kiosk.service:35` is now
`#ProtectHome=true`, commented out. `docs/troubleshooting.md` carries the check
and the cause.

**So the debt inverted, and this is the live form of it.** The capability runs
with no `ProtectHome=` at all, which means it can read other users' home
directories and `/root` is protected only by file permissions. `constraints.md`
C-4 claimed the confinement was present until 2026-09-23; it was not, and the
record described a stronger product than exists. R-16 is weaker in fact than in
writing, which the product manager recorded on 2026-09-14 as a finding rather
than a decision — nobody decided the extra reach was acceptable, a blocker was
cleared.

**What repays it:** hide only what matters, which does not touch the runtime
directory —

```ini
InaccessiblePaths=-/home
InaccessiblePaths=-/root
```

— or `ProtectHome=tmpfs` plus `BindPaths=/run/user/%U`, or move to a user unit
(see D-A6). Note the home directory is `/var/lib/encore`, outside `/home`, so
`ProtectHome=` was buying very little in the first place; what it was buying is
the protection of everyone *else's* home.

**Status:** observed, both ways, on a VM on 2026-09-14. Not `assumed` any more.

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

**"Worse than described above: the key travels too" — withdrawn 2026-09-23.**
The paragraph that stood here said the workflow ADR-0001 relies on is really
"copy the secret and its key together", so the exposure is on every machine the
profile was built on, not only the terminal. **That is no longer how a terminal
is set up.** `encore-install.sh:137-142` runs the client on the terminal
itself, with the keyring plugin made inaccessible, and has it write the
password into the profile — which creates that machine's own `secret=` in its
own `remmina.pref`. Confirmed on a clean Ubuntu 26.04 VM on 2026-09-23: nothing
secret travels between machines, and every terminal has its own key.

**What survives, and it is the part that cannot be designed away.** On the
terminal, the ciphertext and the key sit under one home directory. Anyone who
picks the machine up still recovers the password. Per-terminal keys mean
recovering one tells an attacker nothing about the next, which is a real
improvement in blast radius and not a change in what R-14 can promise.

**One exposure was added by the same mechanism:** see item D-A12.
(Source: [Remmina FAQ](https://remmina.org/faq/); profile format read at
`encore-kiosk.remmina.template:12`; on-terminal key observed 2026-09-23. The
2026-09-13 citation was `group_rdp_server_server.remmina:2`, an untracked
personal profile at the repository root that is not shipped.) See `data.md`.

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

## D-A7 — The configuration step — **largely repaid 2026-09-23, with a remainder**
**Severity: was highest structurally. Now low, and specific.**

**What it said when it was written (2026-09-13):** there is no configuration
step, so the product exists only on machines the author touched personally. The
host, username and password reached a terminal by an administrator hand-placing
a `.remmina` file, and R-4, R-5 and R-13 all stood on a hole.

**It is built.** `encore-install.sh` prompts for the host, the account and the
password (`:64-77`), installs the profile from the shipped template at a pinned
filename (`:118-124`), refuses to continue if the template and the script
disagree (`:126-128`), checks there is exactly one profile (`:131-132`), and
sets the password on the terminal itself (`:137-149`). D-027 fixes this as the
*only* way the product is ever installed — there will be no package.

**The remainder, and it is a real one: two views of one contract.** The
installer writes an exact filename; the runner accepts *any* `*.remmina` at
depth 1, first one wins, `find | head -n 1`, no defined order
(`encore-kiosk.sh:6`). The count check runs once, at install time, and never
again. Anyone who later copies a second profile in — a backup beside the live
one is the obvious way — gets a terminal that may connect to a different host
after the next restart, silently. The installer closed the hole for a fresh
install and left it open for the rest of the machine's life. See
`interfaces.md` I-3.

**What repays the remainder:** make the runner's view match the installer's —
name the file it expects, or refuse to start when there is more than one. It is
no longer a one-way door and no longer deserves the long argument; the door was
walked through on 2026-09-23 and the file format is now on disk on every
converted machine.

**What is still not decided inside it:** certificate pinning (D-A8) and what
the credential can reach on the far host (D-A5) were both supposed to be
settled "inside the configuration design". The configuration step shipped
without either. That is not an oversight this item can fix by itself — it needs
the author — but it is worth saying that the conversation those two were
waiting for has already happened without them.

---

## D-A8 — The RDP session accepts any certificate
**Severity: medium.**

**What:** `cert_ignore=1` and `ignore-tls-errors=1`
(`encore-kiosk.remmina.template:46,107` — citation moved 2026-09-23 off the
untracked personal profile at the repository root and onto the artifact we
actually ship).

**And `cert_ignore=1` is load-bearing in a way nobody intended.** The template
was hand-curated until 2026-09-23 and had silently lost that key — 18 keys
against the working profile's 103 — which cost a debugging session, because
without it a failed certificate check raises a dialog on the terminal's screen
instead of connecting. The template is now generated verbatim from the profile
observed working, with only host, account, password and label blanked, and its
header forbids hand-curation (`encore-kiosk.remmina.template:1-10`). So the
setting this item objects to is currently the thing holding the happy path up.
Removing it without pinning a certificate first turns a silent security
weakness into a visible C-2 breach.

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
(Source: product manager report, 2026-09-13;
`encore-kiosk.remmina.template:46,107`.)

**What repays it:** pin the host's certificate during the configuration step.
This is a natural companion to D-A7 and to D-A5, and all three should be
decided together, inside the configuration design.

---

## D-A9 — The clipboard channel is open and was never argued for
**Severity: low.**

**What:** `disableclipboard=0` (`encore-kiosk.remmina.template:41` — citation
moved 2026-09-23 onto the shipped template).

**Why it matters:** D-012 lists what the capability may reach — screen,
keyboard, mouse, audio, the one host. The clipboard is a bidirectional data
channel that is not on that list. D-012 says anything extra "would have to be
argued for individually". Nobody argued for this one; it is a default.

**It has since been decided, and the shipped artifact contradicts the
decision.** D-019 (2026-09-13) says a terminal does not share a clipboard with
the session it displays. The template says it does. The product manager
recorded this on 2026-09-23 as a deliberate consequence of regenerating the
template verbatim from a working profile: policy and baseline had been bundled
together, and separating them makes D-019, D-009 and D-014 visibly undelivered
rather than invisibly claimed. **That is the right call and it is worth naming
why** — the previous template asserted all three decisions in a file nobody had
ever tested against a working connection, which is how it also lost
`cert_ignore` unnoticed.

**What repays it:** one line in the template, proved on a connection that works
before it goes back in — which is the rule the template's own header now sets.

---

## D-A10 — Packaging conflicts already visible — **three of five gone, 2026-09-23**
**Severity: low. Two survive, and one of them changed owner rather than going
away.**

This item was written on 2026-09-13 against a `.deb` that will now never exist
(D-027, 2026-09-23). Each line, re-checked:

- ~~`/usr/local/bin/remmina-kiosk.sh` is reserved for the local administrator;
  a `.deb` may not install there.~~ **Void.** With no package, `/usr/local/bin`
  is exactly correct — the installer *is* the local administrator acting on
  that machine. `interfaces.md` I-5 is now stable rather than pending.
- ~~Nothing creates the `kiosk` user, group, or `/var/lib/kiosk`.~~ **Done.**
  `encore-install.sh:88-94` creates the `encore` user and group with
  `--system --create-home`, and `:99-100` creates the two config directories
  mode 700. `encore-uninstall.sh:112-117` removes them again.
- **No versions are pinned for Remmina, cage or systemd anywhere. Still true,
  and now nobody's job by construction.** A resolver would have enforced it;
  there is no resolver, and `encore-install.sh:79-83` checks nothing. The
  systemd ≥ 254 floor that ADR-0007 depends on is unenforced. See
  `constraints.md` C-1 and `stack.md`.
- **`HOME` is now set in three places** (`encore-kiosk.service:11`,
  `encore-kiosk.sh:3`, `encore-install.sh:25`). Deliberate — the script is
  runnable by hand, and the installer's copy is what creates the directory the
  other two assume — but record it, or someone will "tidy" one of them away.
- **`ProtectSystem=yes` is the weakest of the three levels and leaves `/etc`
  writable** (`encore-kiosk.service:34`). Still true. `strict` or `full` is
  likely correct and costs nothing. Note this sits next to D-A4: the unit's
  sandboxing is now one level weaker than it looks in two separate places.
- **New line, 2026-09-23: the identity is in `video`, `input` and `render`**
  (`encore-install.sh:94`). Needed for the GPU and input devices, never written
  down before, and wider than `constraints.md` C-4 describes. `strict` or `full` is likely correct here and costs nothing.

---

## D-A11 — The credential file is sitting in the repository — **guarded 2026-09-23**
**Severity: was highest for publication. Now low and residual.**

`group_rdp_server_server.remmina` at the repository root carries a hostname, a
username and a recoverable password; `remote.remmina` beside it is a second
one, and `remmina.pref` is the key for both. All three are untracked.

**The guard exists.** `.gitignore:5-6` excludes `*.remmina` and `remmina.pref`,
and says in a comment why either alone is a secret and both together are the
password in plain text. Templates are deliberately named `*.template` so the
rule cannot match them (`.gitignore:8-9`). `encore-push.sh:8-11` copies by name
rather than recursively for the same reason, and says so.

**What is residual, and it is not nothing.** Three live secret-bearing files
still sit in the working tree of the repository that gets cloned onto every
terminal. They are one `git add -f` or one careless archive away from being
published, and `encore-push.sh`'s by-name copy is the only thing standing
between them and a `scp -r`. The protection is real and it is entirely
convention plus one ignore file.

**Note also `remmina.pref:5`** still points its screenshot path at
`/var/lib/kiosk`, the pre-D-023 name. It is a personal file, not shipped, and
it is named here only so nobody finds it later and concludes the rename was
incomplete.

---

## D-A12 — The password reaches a command line, and may reach the journal
**Severity: medium. Added 2026-09-23. The installer already admits it.**

**What:** the password is set by running the client under `systemd-run` with
`--set-option password="$RDP_PASS"` on the command line
(`encore-install.sh:137-142`). A transient unit's command line is visible to
anything that can read the process table for the instant it runs, and systemd
logs the invocation, so it can land in the journal. The script greps for it
afterwards and, if it finds it, tells the administrator the password is in the
journal and to rotate it or clear it (`:173-176`).

**Why it matters:** R-14 is about the credential at rest on the terminal. This
is the credential in transit during setup, which no requirement covers, and it
leaks into a place that survives a reboot and is readable by anyone in
`systemd-journal`. The prompt is careful — no echo, no shell history
(`:72-76`) — and then the value is handed to a command line anyway, so the care
taken at the top is partly undone at the bottom.

**What is good about it, and worth keeping:** the script does not pretend. It
checks and says so in plain words rather than letting the prompt imply privacy
it did not deliver. That is the behaviour to preserve in whatever replaces it.

**What repays it:** pass the secret on stdin or through a file descriptor
rather than `argv`, so it never becomes a command line at all.

---

## D-A13 — The runner's profile check and the installer's do not agree
**Severity: medium. Added 2026-09-23. Split out of D-A7 so it is not lost
inside a repaid item.**

**What:** `encore-install.sh` writes exactly one profile at an exact filename
and verifies the count (`:26`, `:118-124`, `:131-132`). `encore-kiosk.sh:6`
takes the first `*.remmina` it finds, in no defined order, and never counts.

**Why it matters:** the guarantee is made once, at install time, and never
again — while the thing that depends on it runs on every start for the life of
the machine. A second profile arriving later (a backup copied beside the live
one is the ordinary way) gives a terminal that may connect to a different host
after the next restart, with nothing logged and nothing on screen to say it
changed. It is a silent failure of R-5, which promises the configuration names
the machine.

**What repays it:** one view of the contract instead of two — the runner names
the file the installer writes, or refuses to start when it finds more than one.

---

## D-A14 — Nothing enforces the version floor the design depends on
**Severity: low today, and it will be invisible when it bites. Added
2026-09-23.**

**What:** `constraints.md` C-1 declares systemd ≥ 254 because ADR-0007's
backoff uses `RestartSteps=` and `RestartMaxDelaySec=`, both added in that
release. `encore-install.sh:79-83` installs packages and checks the version of
nothing.

**Why it matters:** systemd silently ignores directives it does not know. On an
older release the terminal installs cleanly, runs, and retries flat — no error,
no warning, no log line, and behaviour the record does not describe. D-024
accepts excluding older distributions; it does not say the exclusion should be
undetectable.

**Why it is here rather than treated as an oversight:** under D-027 there is no
package and therefore no dependency resolver, so this check either lives in the
installer or nowhere. That is a cost D-027 names explicitly in its own words.
This item is that cost, recorded on the engineering side with the line number
where it would go.

---

## D-A15 — A permanently broken far-end TLS hides behind an ordinary outage
**Severity: medium, and it is a compromise chosen on purpose. Added
2026-09-23. Not built — it arrives with the runner's pre-flight.**

**What:** ADR-0008's addendum puts "the negotiation succeeded and the TLS
handshake did not" on the retry side of D-020. A target whose TLS is broken in
a way that never recovers — a certificate the probe cannot parse, a far end
that only offers something OpenSSL will not touch even at `SECLEVEL=0` — will
therefore be retried for ever, which is the harm D-028 exists to prevent.

**Why it was taken:** the other branch is worse. The same status is what our
own probe produces if its acceptance envelope turns out to be stricter than the
client's, and stopping a healthy terminal for ever is the direction D-020 names
as the expensive one. Only one far end has ever been spoken to (Q-11), so there
is no evidence with which to prefer the strict reading.

**What would repay it:** having probed an `xrdp` and a `gnome-remote-desktop`
target, so that a failed handshake can be told from our own strictness. If it
turns out our envelope never causes it, this status moves to the stop side and
this item closes. Until then, the journal line on every attempt is the only
thing carrying the reason, which makes it worth more than usual.

---

## D-A16 — The target's address will exist in two places
**Severity: low, and it is the price of ADR-0009. Added 2026-09-23. Not built.**

**What:** ADR-0009 has the installer record `RDP_HOST=` and `RDP_PORT=` in the
install record (I-7) so the runner's pre-flight knows where to connect without
reading the profile. The same address is already inside `server=` in the
profile. Two copies, written from one input.

**Why it was taken:** the alternative was the runner parsing a file format we
do not own, in a component with nobody watching, and splitting `host:port` on a
character that is ambiguous for an IPv6 literal — see ADR-0009, option A.

**What it costs:** an administrator who hand-edits the profile afterwards gets a
terminal that probes one address and connects to another, and nothing detects
it. The probe would pass against the old host while the client fails against
the new one, which reads as a healthy pre-flight and a broken session.

**What would repay it:** either a check that the two agree — which needs the
runner to read the profile and so undoes ADR-0009 — or the profile ceasing to
be the primary record of the address. Neither is worth doing before a second
key is ever wanted; ADR-0009's *Revisit when* is the trigger.

---

## D-A17 — The probe's TLS context builder mutates process-global state
**Severity: low today, and it becomes real the moment the probe is imported
rather than run. Added 2026-09-23. Built.**

**What:** `permissive_tls_context()` in `encore-probe.py` uses
`warnings.catch_warnings` to suppress the deprecation warning raised by
lowering the TLS floor to 1.0. That context manager swaps the interpreter's
global warnings filter and restores it afterwards; it is not thread-safe, and
two threads inside it at once leave the filter in whichever state the loser
restored.

**Why it was taken:** as a standalone script run once, with one thread and no
other Python in the process, it is invisible and the alternative — carrying the
warning through to the operator's terminal on every probe — is worse for a
person watching the setup step.

**What it costs:** the probe is not a script only. ADR-0008 has the runner's
pre-flight call it, and the installer ticket calls it from Python. Any host
process that is threaded, or that relies on its own warnings filter, inherits a
window where the filter is not what it set. The symptom is a warning that
appears or disappears somewhere unrelated, which is close to undiagnosable.

**What would repay it:** the entry point that the installer and the runner call
declares the seam — either the caller owns warning suppression and the builder
does not touch the global filter, or the builder is documented as
single-threaded-only and the installer ticket honours that. Either is a
sentence of design, not a rewrite; the cost is only that it must be decided
before the second caller exists rather than after.

---

## D-A18 — The Python floor is undeclared on the machine and unchecked
**Severity: very low, and it fails loudly. Added 2026-09-23 and reduced the
same day. Built.**

**Reduced 2026-09-23, hours after it was written.** This item was raised
against a floor of **3.14** and it said the failure below that floor was
silent: the IDNA error for a structurally invalid name was a bare
`UnicodeError` with no `.reason`, the probe's handler read `.reason`, and the
resulting `AttributeError` escaped as a traceback and exited **1** — the status
held unassigned so a crash cannot be read as a classification. ADR-0008 stops
for ever on `2 USAGE`, so on an older Python the same malformed `RDP_HOST=`
would have retried for ever. **That defect was fixed concurrently** — the
handler now interpolates the exception itself — so the floor is **3.10** and
the whole silent-inversion argument above is void. The item survives only in
its weaker form below.

**What:** `constraints.md` C-1 declares CPython ≥ 3.10.
`encore-probe.py` carries a bare `#!/usr/bin/python3`, names no version
anywhere, and `encore-install.sh:79-83` checks the version of nothing.

**Why it matters, now:** barely. Below 3.10 `encore-probe.py` does not import —
`bytes | None` in a signature at `:255` is a runtime-evaluated PEP 604 union —
so an adopter on an older interpreter gets a `SyntaxError` at the first run,
which is a visible failure, not a misclassified one. The second-order effect,
`socket.timeout` not being a `TimeoutError` below 3.10 and collapsing `5
TIMEOUT` into `4 UNREACHABLE`, is unreachable for the same reason. 3.10 is four
years old and every release in scope ships something newer on either family
(Fedora 44 ships 3.14).

**Why it was taken:** this is the same shape as D-024's accepted cost. The
product tracks current releases and carries no compatibility handling, and
Ubuntu 26.04 — the only distribution a terminal has ever been built on — ships
3.14, so the floor costs nothing today. What D-024 accepts is *excluding* older
releases; it does not accept the exclusion being undetectable, which is the
part recorded here. Under D-027 there is no package and no resolver, so a check
lives in the installer or nowhere — identical to D-A14.

**What would repay it:** anything that makes the floor visible on the machine
rather than only in this record — a version guard, or an interpreter named in
the shebang. **Whether the installer should check it is a backlog question and
is deliberately not settled here**; it is named so it is not lost. On the
technical facts the case for checking Python is now thin, and D-A14's case for
checking systemd ≥ 254 is not — that one still bites silently.

**One of the two things that would have shrunk this item has happened.** It
said the probe not depending on `.reason` would drop the floor to the syntactic
3.10. It did, on the day the item was written. The other — measuring 3.12 and
3.13 — is now moot, because the boundary it would have pinned down no longer
exists.

---

## D-A19 — The keyring suppression is written in Debian paths, at two sites, and one of them blocks Fedora conversion outright
**Severity: highest of the new items. Raised 2026-10-04, the same day it was
filed, when the second site was found. It is the first defect D-036 bought, and
it is a blocker rather than a degradation.**

**What: the same Debian multiarch path is constructed twice, in two files, for
two different purposes. Neither can match on a dnf-family machine.**

**Site 1 — the unit, and the milder symptom.** `encore-kiosk.service:28-30`
suppresses Remmina's secret plugin at *runtime* by making it unreachable, and
it does so by naming three literal paths:

```ini
InaccessiblePaths=-/usr/lib/x86_64-linux-gnu/remmina/plugins/remmina-plugin-secret.so
InaccessiblePaths=-/usr/lib/aarch64-linux-gnu/remmina/plugins/remmina-plugin-secret.so
InaccessiblePaths=-/usr/lib/arm-linux-gnueabihf/remmina/plugins/remmina-plugin-secret.so
```

**Site 2 — the installer, and the blocking symptom.**
`encore-install.sh:42-48` computes the same path from `uname -m`:

```sh
case "$(uname -m)" in
    x86_64)  TRIPLET=x86_64-linux-gnu ;;
    aarch64) TRIPLET=aarch64-linux-gnu ;;
    armv7l)  TRIPLET=arm-linux-gnueabihf ;;
    *)       die "unsupported architecture: $(uname -m)" ;;
esac
SECRET_PLUGIN="/usr/lib/$TRIPLET/remmina/plugins/remmina-plugin-secret.so"
```

`SECRET_PLUGIN` is then handed to `systemd-run -p "InaccessiblePaths=-$SECRET_PLUGIN"`
at `:173` — the step that writes the RDP password into the profile, which is
the one moment the suppression has to work or the client demands a keyring.

**Fedora puts the file at `/usr/lib64/remmina/plugins/remmina-plugin-secret.so`**
— measured 2026-10-04 with `dnf repoquery -l remmina-plugins-secret` against
Fedora 44 (`remmina-plugins-secret-1.4.41-2.fc44`). No Debian triplet appears
anywhere in a Fedora filesystem, so **every one of the four constructions
misses.**

**The miss is silent by construction at both sites, and the two consequences
are not the same.** The leading `-` tells systemd to tolerate a path that does
not exist. That is correct on apt — it is what lets one unit cover three
architectures — and on Fedora it makes the suppression a no-op with nothing
logged:

- **Site 1 gives a working terminal that prompts for a keyring.** The unit
  starts cleanly and the suppression is simply absent, so the client asks for a
  keyring no unattended terminal can unlock, and the session stops in front of
  a child with a password prompt. That is the symptom `BACKLOG.md` item 8
  records as **observed** on 2026-09-14. A terminal reporting healthy while not
  working is this project's oldest failure shape, and this is a new door into
  it.
- **Site 2 gives a conversion that cannot complete.** With the plugin
  unsuppressed, `remmina --update-profile … --set-option password=` does not
  store the password, and the installer's own guard catches it: `:183-184`
  greps the profile and runs `die "no password stored in the profile"`. **The
  install fails and stops.** No terminal exists to degrade.

**So this item is not "a prompt comes back". It is "the install fails", and
item 16 is undeliverable without it.** That is why the plan fixes both sites in
one change rather than treating the second as a follow-on.

**Worth recording how it was found, because the lesson is about reading rather
than about Fedora.** The site with the *milder* symptom was found first, by the
architect, from the unit file. **The blocking site sat eight lines into the
installer the same reader had already opened, and was missed** — along with the
`systemd-run` call 125 lines further down that consumes it. It was found by the
senior engineer while planning item 16 and confirmed by the product manager
before it reached this file. One grep for the plugin's filename across the
whole tree would have returned both on the first day. The defect was findable
in one command and was instead found in two passes by two people.

**Why it matters more than its size:** `BACKLOG.md` item 16 states that
`encore-kiosk.service` mentions no package manager and is therefore untouched
by the second family. That is true of the *package manager* and false of the
*distribution*. These two sites are the only places in the whole product where
the design reasoned from a distribution's filesystem layout rather than from a
capability — everything else is written in terms both families carry, which is
exactly what `overview.md` claims and what made D-036 cheap. **It still does
not make the work L:** two files, no Fedora-only component, no conditional on
the package manager, and `constraints.md` C-1's SELinux finding is unaffected.

**Why it was taken:** it was not taken. Both sites were correct when written,
for the only family that existed, and D-036 made them wrong on 2026-10-04
without anyone touching either file. That is the characteristic cost of
widening a claimed platform — the defect arrives in code nobody edited — and
here it arrived in the step that the installer's own guard protects, which is
the one piece of luck in the item: site 2 fails loudly.

**What repays it, and it is planned — `docs/plans/fedora-dnf-family.md`, steps
2, 3 and 5, written by the senior engineer on 2026-10-04.** Two halves, and the
second one is the part worth defending at this level:

- **The installer stops computing the path and asks the machine for it** — a
  `find` over `/usr/lib` and `/usr/lib64`, once, feeding the password step.
  `TRIPLET`, the `case` and `SECRET_PLUGIN` all go. The installer then makes no
  claim about any distribution's layout, which is the D-A19 root cause removed
  rather than extended.
- **The unit keeps literal paths, and the installer checks they cover the
  machine.** Step 3 adds the `/usr/lib64` line; step 5 adds a loop that greps
  the installed unit for every path the `find` actually located and `die`s with
  the exact line to add if one is missing. **This is the half that repays the
  class rather than the instance.** The item's own complaint was that a list of
  literal paths grows by one line per distribution *with no way to notice a
  missing line* — the check is that way. A layout nobody has met now produces a
  loud failure at install time, on the machine, naming the fix, instead of a
  terminal that converts cleanly and then shows a child a keyring prompt. It
  converts the silent failure mode into a loud one, which is the thing this
  project needs more than it needs any particular path.

It is also, per the plan, **the only part of this ticket that can be watched
without a Fedora machine** — which matters, because everything else about
D-036 is currently claimed and unobserved.

**Two things are settled about the mechanism, and one is not.**

- **Closed negative, 2026-10-04: Remmina cannot be told not to load the
  plugin.** This item previously asked whether a configuration setting could
  replace the growing path list. The senior engineer established that no such
  preference exists; the maintainer said in 2019 that a hidden option could be
  added and it never was; and upstream documents exactly two mechanisms —
  uninstall the package, or hide the `.so`. Uninstalling is closed by R-11 and
  D-007, which forbid the product changing software the machine already had.
  **So hiding the file is not a shortcut this product took. It is the only
  mechanism available**, and the list of paths is a consequence of that, not a
  design preference. Nobody should reopen this.
- **Still open, and deliberately unplanned: whether the installer should write
  a `encore-kiosk.service.d/` drop-in** from what it discovered, instead of the
  unit shipping literal paths at all. The planned repair leaves the unit
  asserting paths and adds a check that the assertion is true on this machine;
  a drop-in would mean the unit asserts nothing and the one discovery feeds
  both the password step and the runtime suppression. **The check makes this
  question non-urgent, not closed** — it removes the silence, which was the
  harm, and leaves the duplication, which is only a cost. **It is not a
  ticket-sized question**, because a drop-in is a new installed artifact:
  `encore-uninstall.sh` has to remove it and C-3's clean-undo promise depends
  on that, which makes it a contract across three files and an architecture
  question rather than an implementation one. The record already carries two
  items of exactly that shape, D-A8 and I-7 — an artifact written once at
  install that nothing re-checks and the undo must remember — so the pull
  against a third is real and not merely conservatism. Named here so it is not
  lost. Not sized and not ordered.

### The coverage check fails late, and that is an open question — 2026-10-04

**Repaid, with one thing left open that is not about Fedora.** Steps 2, 3 and 5
shipped (`8827dd6`, `5d56939`): the installer finds the plugin at `:249` instead
of computing a triplet, the unit names `/usr/lib64` at `:38`, and the coverage
check at `:282-285` refuses to finish when the unit misses a path the machine
actually has. **The silent failure mode is gone, which was the harm.** What
remains is *when* the loud one fires.

**Verified order in the shipped file:**

| line | what happens |
|---|---|
| `:144` | packages installed — the earliest the `find` can truthfully run (`5d56939`) |
| `:152` | the `encore` identity is created |
| `:192` | the profile is written |
| `:249` | the `find` locates the machine's plugin paths |
| `:253` | **the RDP password is stored** |
| `:271` | the unit is copied to `/etc/systemd/system/` |
| `:282` | the coverage check runs, and dies |

So a machine with a layout the unit does not name is **converted most of the
way and then refused**: it keeps a system identity, a connection profile and a
stored credential, and the person running it has no reason to expect any of
that from a message about a missing path. `encore-uninstall.sh` is what cleans
it up, and nothing in the failure message says so.

**The credential is the part that matters, and it is not merely untidy.** The
identity and the profile are files, and deleting files is what the undo does.
The password is a secret that has been handed to `remmina` on a `systemd-run`
command line — which is D-A12, the item that records the password reaching a
process list and possibly the journal. A conversion that fails *after* `:253`
has paid D-A12's full cost for a terminal that will never exist.

**The check does not need to be there.** `install -m 644` at `:271` has just
overwritten `/etc/systemd/system/encore-kiosk.service` **with
`$HERE/encore-kiosk.service`**, so at `:282` the two files are byte-identical by
construction. The check is grepping a file whose content it dictated eleven
lines earlier. It cannot detect a hand-edited unit, a stale version from a
previous install, or anything else about the machine's prior state, because
`install` destroyed that evidence at `:271`. **Reading the installed copy rather
than the source copy therefore buys no information at all**, and pays for it
with the identity, the profile and the stored password. `$HERE` is set at `:19`
and the source copy is present from the first line.

**The earliest it could run is immediately after the packages step at `:144`** —
the `find` needs the packages and nothing else, so the find and the check move
together as one block, before `echo "==> user"`. That would leave a refused
machine holding installed packages and nothing else.

**What this does not buy, so that nobody oversells it:** the password is
*prompted* at `:117`, before the packages step, so the person has typed it
either way. The gain is that it is never *stored* and never reaches a command
line — D-A12's exposure, not the typing.

**Two things stop this being a clear call, which is why it is recorded here and
not fixed:**

- **Neither copy is the complete answer, and nobody has said so.** A grep of the
  unit file misses any `InaccessiblePaths=` in a drop-in under
  `/etc/systemd/system/encore-kiosk.service.d/`. The only complete check is the
  effective merged value — `systemctl show -p InaccessiblePaths
  encore-kiosk.service`, which needs `daemon-reload` first and is therefore
  *later* than the check already is. So the real fork is **early and
  approximate** against **late and exact**, and the current code has chosen
  late *without* being exact, which is the one combination with nothing to
  recommend it.
- **An early source-copy check can refuse a machine that would have worked.**
  If an administrator has already written a drop-in naming their layout, the
  early grep misses it and dies on a covered machine. That is a false refusal,
  and it is the same shape as the risk ADR-0008 already tracks — our gate being
  stricter than the thing it gates, stopping a healthy terminal for ever, the
  expensive direction. It is narrow today, because `docs/troubleshooting.md`
  now tells people not to hand-edit the unit, but it is the reason this is a
  contract question and not a line move.

**And the equivalence is a property of the sequence, not an invariant.** The
source and installed copies are identical only because the installer *copies*
the unit. If it ever *composes* it — which is exactly the
`encore-kiosk.service.d/` drop-in question still open above — then `$HERE` stops
being the truth and a source-copy check becomes wrong. **Whichever way this
goes, the two questions have to be answered together**, or the drop-in work will
silently invalidate the check.

**Status: the Fedora path is measured** (`dnf repoquery`, Fedora 44,
2026-10-04), and **both construction sites are read directly from the files**
(`encore-kiosk.service:28-30`; `encore-install.sh:42-48`, `:173`, `:183-184`).
**That the suppression therefore fails on Fedora is read, not watched** — no
terminal has ever been booted on Fedora, so neither the failed install nor the
keyring prompt has been seen there. The apt-side observation the runtime
symptom would reproduce is `docs/tests.md` and `BACKLOG.md` item 8, 2026-09-14.

---

## D-A20 — The architecture refusal was an artefact, and removing it relocated the refusal rather than ending it
**Severity: moderate on consequence, high on what it says about the record.
Filed 2026-10-04 and **corrected the same day**, after review found this entry
claimed more than the code delivers. Read the correction before acting on this
item: it is the entry somebody will open in a year before deciding whether to
restore or remove a refusal, and the first version of it would have told them
the problem was solved when it is only moved.**

**What it was:** `encore-install.sh:46` ended the architecture `case` with
`die "unsupported architecture: $(uname -m)"`. Anything that was not `x86_64`,
`aarch64` or `armv7l` was refused before a single package was installed.

**That was never a product limit.** R-2 says no particular hardware is
required, and `constraints.md` C-1 records "32-bit and ARM must be considered
in scope". Nothing in the product record has ever restricted the instruction
set. The refusal existed for one reason and it was a mechanism reason: **a
Debian multiarch triplet had to be constructed, the constructor only knew
three, and the fallback was made fatal.** That is mechanism leaking out of a
script and being enforced as policy on a reader — the product refused a machine
it claims to support, and said "unsupported architecture" while doing it, which
is a sentence no requirement in the record authorises.

**D-036 made the gap wider and visible.** Fedora builds for `ppc64le`, `s390x`
and `riscv64` in addition to the three the `case` knew. It was equally wrong on
the apt side and nobody noticed, because nobody had an unusual machine to try.

**The ruling, and it is the product manager's, taken 2026-10-04: the refusal is
not to be preserved.** The `case`, the triplet and the `die` are gone, replaced
by a `find` (`encore-install.sh:249`). **That was a deliberate behaviour change,
not a tidy-up**, and it is recorded here so nobody restores the line as a
safety check later.

### What actually changed, corrected 2026-10-04

**This entry first said the product "stops claiming anything about exotic
architectures in either direction" and that "an adopter on `riscv64` gets
whatever the packages and the compositor actually do on that machine". That is
wrong, and wrong in the direction that matters — it describes the problem as
solved when it is relocated.**

Traced through the shipped code on a Debian `riscv64` machine: the plugin
installs at `/usr/lib/riscv64-linux-gnu/remmina/plugins/remmina-plugin-secret.so`;
the `find` at `:249` locates it; the coverage check at `:282-285` greps
`encore-kiosk.service`, whose list at `:35-38` names three Debian triplets and
`/usr/lib64` and **not** that path; and the install dies. **The fourth-triplet
machine is still turned away.**

**So the refusal moved; it did not end.** It moved from *an unconditional list
of three processor names* to *a condition on the one thing that genuinely
matters* — whether this machine's plugin path is named in the unit. That is a
real improvement and it is what the plan intended:

- the old refusal was **unconditional and wrong**: it turned away a machine for
  its processor name, a fact that has no bearing on whether the product works
  there;
- the new refusal is **conditional and true**: it turns away a machine only
  when the unit genuinely cannot hide that machine's plugin, which is a fact
  about whether the terminal would work;
- and the message changed from `unsupported architecture` — which R-2 does not
  authorise anybody to say — to a named path and the exact line to add.

**R-2's cost is reduced, not eliminated.** The honest sentence is that the
product no longer refuses a machine for its processor, and still refuses a
machine whose library layout the unit does not name. The two overlap heavily in
practice, because a new processor on a Debian-family system means a new
multiarch triplet, which means a path the unit does not have. **A fifth layout
is a one-line change to the unit and the installer now says which line** — that
is the whole of the improvement, and it is enough, but it is not "says nothing
in either direction".

**The same overclaim is in `8827dd6`'s commit message.** That is history and it
stays. The record carries the correction rather than pretending the claim was
never made — which is the same discipline C-1 applies to the Python floor.

**Still true, and unaffected by the correction:** **nothing has ever been run on
any architecture other than `x86_64`** (`docs/tests.md`), so the old refusal,
the new condition and R-2's breadth are all claims rather than observations.
The difference is that the new one is a claim about something that matters.

**What would repay what is left:** nothing in `encore-install.sh`. Two things
elsewhere, neither of them scheduled here:

- **The unit's path list is still a list**, so "a fifth layout costs one line"
  is only true for somebody who has a machine to discover it on. D-A19's open
  drop-in question is the structural answer and is deliberately unplanned.
- **The refusal's timing is the live question**, and it is a bigger one than
  this item — see the ordering question under D-A19 and in `NOTES.md`,
  2026-10-04. A machine turned away by the coverage check is turned away
  *after* its identity, its profile and the RDP password have been written.
