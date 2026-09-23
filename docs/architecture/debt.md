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
