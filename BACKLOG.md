# Backlog

**This is not product documentation.** It is a working list of what is left to
build, in the order it should be done. `docs/product/` says what the product is
and what was decided; it makes no statement about order or timing. That is what
this file is for.

Nothing here is a decision. Decisions live in `docs/product/decisions.md` and
are referenced by ID. Requirements live in `docs/product/solution.md` and are
referenced as `R-n`. What is wrong with the built code, and why, lives in
`docs/architecture/debt.md` and is referenced as `D-An` — **that file says what
is broken; this file says what order it gets fixed in.** Neither is the other's
summary.

One list, not several. Everything competes for the same evenings, so everything
is ranked against everything else. An item that is built and wrong is not in a
separate category from an item that was never built — both are work, and the
only question is which matters more.

Last rewritten: 2026-09-13.

---

## Resume here — next session

Written 2026-09-23. Delete a line when it is done; if this section is stale,
trust the numbered list below it instead.

**First, ten minutes on a terminal.** Four tests are unrun and everything else
waits behind them. Details for each are in `docs/tests.md`.

- [ ] **Test 7 — the reboot.** The highest-value unrun test in the record. It
      promotes R-8 from `intended` to `real`, and it settles whether the
      console failing to come forward is a real defect or an artefact of
      switching over on a machine that was already running a desktop. Several
      other questions are stuck behind this one answer.
- [ ] **Test 8 — where the pin file is read from.** One command. **Blocks 7b.**
      A pin written to a path the library does not read is inert, and the
      terminal goes on trusting anything while the record says it is pinned.
- [ ] **Test 10 — does running setup twice leave a working terminal.** D-031
      promises this and nobody has ever watched it.
- [ ] **Test 11 — the probe against a real target**, not a fake one. Only one
      machine has ever been spoken to.

**Then the next ticket.**

- [ ] **7b — capture and confirm inside setup.** Designed; waiting only on
      Test 8. See *Item 7, broken down* below.

**Two decisions waiting on the author.**

- [ ] **Ask the architect first: does the recovery design actually need the
      settings that set the systemd 254 floor?** If a simpler retry works, the
      floor drops by two years of distributions and the next question
      disappears. Nobody has asked.
- [ ] **Refuse to convert a machine below the floor, or let it install and
      misbehave quietly?** D-024 accepted excluding older releases; what was
      never decided is whether the exclusion should be visible. It now has a
      face: Raspberry Pi OS before October 2025.

**Housekeeping, whenever.**

- [ ] `docs/architecture/NOTES.md` is past its fold trigger and nothing is in
      flight, so it is safe to restructure.

---

## The state of things, in one line
The positive path was reached once, on a virtual machine, on 2026-09-14 — a
session on the screen, watched by a human. It has not been reproduced, it has
never run on old hardware, and it is still deployed entirely by hand. Four
known defects stand, all listed in `README.md` and `docs/architecture/debt.md`.

## The order, and why it is this one
Set by the author on 2026-09-13: **get the positive path working, then make it
installable, then handle the failures.** Nothing on the error-handling half is
worth designing against a connection nobody has seen succeed, and every fix
below item 9 is a guess until item 2 lands.

Item 2 landed on 2026-09-14. **Item 2a is the next milestone**: reproduce it
from nothing on a clean machine and label the result `v0.1`. It is inserted
rather than renumbered because the numbers below are referenced from
`docs/architecture/debt.md`, `README.md` and the notes.

Two consequences of that order, both accepted deliberately:

- **No child uses a terminal until item 11 is done.** A terminal that cannot
  find its configuration hands the person in front of it a connection editor
  and a file browser. That is fine on the author's own bench and is exactly
  what the product exists to prevent in a child's room.
- **Packaged is not published.** Items 3 and 4 make the product installable for
  the household. Publishing it to strangers is item 15, after the failures are
  handled, because R-13 promises a reader something they can rely on.

## The list

| # | What | Why it sits here | Refs | Size |
|---|---|---|---|---|
| 1 | ~~**Add a `.gitignore`**~~ **DONE 2026-09-14** | Was out of competition — the only item that got worse rather than staying the same. The rules exclude `*.remmina` and `remmina.pref`; templates are tracked deliberately and named so the rules cannot match them. | — | **XS** |
| 2 | **Get one terminal connecting, end to end** | **The primary goal. Root cause found 2026-09-14:** the capability opens its session on a console that is never in the foreground, so the session is never activated and the compositor waits for a screen it is never given. Everything else observed that day — silence in the log, black screen, frozen console switching, hanging stop — is that one fault. One old machine, one working connection, a session on the screen, watched by a human. The previous attempt did not reach this, suspected to be a bad connection profile. Everything else on this list is a guess until this succeeds: the recovery argument, the failure-handling design, and every `real` requirement marked `read in code`. Decide while doing it what "working" includes — in particular whether sound counts, or whether item 5 is separate. | all `real` R-n | **M** |
| 2a | **Redeploy from scratch on a brand-new VM, confirm, and label v0.1** | **The next milestone.** Item 2 proved the product can reach a session once, on a machine that had been fought with all day. This proves it can be done again, from nothing, by following the written procedure — which is the difference between a thing that worked and a thing that works. Build a clean VM, follow `README.md` end to end without improvising, and write down every step the README failed to mention. Run **Test 7** while you are there (does it survive a reboot) — it is the cheapest requirement to promote, and it is what R-8 promises. Run **Test 6** too (must the encryption key travel), which closes an open question by experiment rather than argument. Tag `v0.1` only if the procedure completed without undocumented steps. | R-8, R-11, D-025 | **S** |
| 3 | **A configuration step: the target machine, and the encryption key** | Hand-editing the profile is the suspected cause of item 2's failure, and it is why the product exists only on the author's own machines. Where configuration lives, how it is set, how it is changed, and what makes it invalid — that last part is what item 11 needs. **Must settle where the encryption key comes from (D-025).** Observed 2026-09-14: a terminal cannot read its stored credential without a key file present. Unresolved: whether that key must be copied from the machine where the profile was built, or can be created on the terminal and the credential set there afterwards. Either way it is established per deployment and never shipped — a key that is the same everywhere protects nothing while reading as protection.  **And the guarantee is made once, 2026-09-23.** The installer writes one profile under a pinned name and checks there is exactly one; the runner takes whatever `*.remmina` it finds first, in no defined order. So a second profile arriving later — a backup copy, a half-finished edit, a restore — silently changes which machine a terminal connects to, with no error. R-16 promises the machine it was configured to connect to; today that holds at install time and is never checked again. | R-5, R-16, D-002, D-A13 | **L** |
| 4 | **Make installing from a clone something a stranger can do twice** | **No package, decided 2026-09-23 (D-027): install is a clone plus a script, and undo is the matching script.** That closes the packaging question and opens three the package would have answered for us. **Prerequisites are nobody's job but ours** — D-024's minimum versions must be checked by `encore-install.sh` or they are not checked at all, and an adopter on an older release still gets a terminal that fails in ways nothing describes. **There is no upgrade path**: a converted machine is updated by copying a newer clone over it and installing again, and nothing says that leaves a working terminal — that needs trying on a machine that is already working, not reasoned about. **Removal is now a promise we keep by hand** — a package manager would have remembered the file list; `encore-uninstall.sh` has to be right instead, which is what makes Test 4 worth running every time the installer changes. **Renames: partly done 2026-09-14.** The units are `encore-kiosk` (D-022) and the system user, group and home directory are `encore` (D-023) — both done in the repository, and the migration path for an already-converted machine is untested beyond one VM. Still open: "kiosk" must stop naming a machine anywhere it still does (D-018). `README.md` documents the old names in its install and removal steps and has to change with them, or the removal instructions will leave an orphaned account behind. The current names carry no product prefix and carry the remote desktop client's name, which the architect may one day replace.  **The floor has a number now: systemd 254.** The recovery design depends on directives that arrived there, and older systemd ignores them silently and gives flat retries instead of backing off — no error, no warning, just different behaviour. Nothing checks it. That is D-024's accepted cost arriving in a specific, checkable form. | R-4, D-003, D-018, D-022, D-023, D-027, D-A14 | **L** |
| 5 | **Audio works in both directions, out of the box** | Output, and input where the machine has a microphone, default with no device-picking, and the host's devices stay out of the session. A terminal with no microphone must still be fully usable. Old machines vary, so this needs checking on each kind. Part of the positive path, not of error handling. | R-12, D-009, D-014 | **M** |
| 6 | **Ordinary users cannot deactivate** | No record that this is enforced. Cheap, and it is half of what the lock means. D-017 puts the whole arrangement on there being no ordinary accounts on a terminal, which nothing checks. | R-9, D-006, D-017 | **S** |
| 7 | **Confine what the capability can reach** | It runs unprivileged already. Not done: pinning the connection to the one configured machine rather than whatever answers to its name, and closing the shared clipboard. **And a protection was dropped on 2026-09-14 to get a working session** — the setting that hides other users' home directories also hides the directory the graphical session needs. It has to come back in a form that does not break startup, or D-012's promise is weaker in fact than in writing.  **No longer blocked, 2026-09-23:** pinning the connection to the one configured machine was deferred into the configuration design, and that design shipped without it — so this needs the author's reading of what R-16 means, not more waiting. Also newly recorded: the identity runs in `video`, `input` and `render`, which is wider than the privilege ceiling describes and nobody has checked which are needed.  **Investigated 2026-09-23, and it is buildable.** A terminal can be made to accept exactly one certificate and refuse everything else, with nobody asked and nothing drawn on the screen — the refusal happens below the client, so no dialog can be constructed. That delivers R-16 and shrinks what R-14 has to promise: the credential's remaining exposure becomes somebody holding the machine, rather than anything on the network that answers to the right name. **Three things came with it.** The pin and the current accept-anything setting are **one change, not two** — the ignore short-circuits above the pin, so a pin added first would sit there inert. Capture at install needs a tool we do not ship: either an extra package or a small piece of protocol code, and nobody has chosen. And the pin lives outside the product's own footprint, so `encore-uninstall.sh` must remove it or R-11 is broken by a file that changes how every remote desktop client on that machine behaves. **Capture solved, 2026-09-23, size S.** A first-connection capture mode already exists below the client, runs with no graphical session and no credentials, and writes the certificate where a standard tool can read the fingerprint back. It needs one extra package on the terminal — which then stays for good, so `encore-uninstall.sh` must remove it. The runner can tell a refused certificate from an unreachable machine by **exit code**, not by matching log text, which is what makes D-028's "stop and say why" affordable. **Both author questions are answered: D-028 and D-029.** **Capture designed and proven, 2026-09-23 (D-030, ADR-0008).** Nineteen bytes each way before encryption starts, then the standard library completes the handshake and returns the certificate — tried against a live target and it produced the same fingerprint the borrowed client had, in the exact form the pin needs. No extra package; the language is in the base system. **The same probe answers D-028:** the runner runs it before launching the client, and a mismatch exits with a status that already means "stop permanently". **Size is L, not M** — the probe is the cheap part. What costs is making the pin govern anything: the accept-anything setting must leave the profile in the same change, a second permissive setting in a file we generate but have never read must be asserted, a machine-wide file written and later removed, the confirmation step built, and the runner given a permanent-stop path. **Two risks named:** our probe is stricter about encryption than the client, so a weak certificate could be refused by us and accepted by it — a healthy terminal stopped for ever, the expensive direction; and the probe is a gate, not the guard, so the machine-wide file stays as the real enforcement. Still blocked on Test 8 and Test 9. | R-16, R-14, R-11, D-012, D-019, D-020, D-028, D-029, D-030, D-A8, D-A5 | **L** |
| 8 | **Settle what the stored credential can honestly promise** | R-14 promises more than anything can deliver on an unattended machine. **Observed 2026-09-14:** the client asked for a keyring to be unlocked, which no unattended terminal can answer — so the only storage that works here is the reversible file-based one. That is the answer to `Q-P2`'s technical half; what remains is the author deciding what R-14 says to a reader. Ties to item 7: a credential that can be handed to an impostor was never protected by being hard to read.  **No longer blocked, 2026-09-23.** This was deferred into the configuration design; that design has now shipped as `encore-install.sh` without it, so the reason for waiting is gone and nothing stands between this and the author. **And the question got wider:** R-14 covers the credential *at rest* and nothing covers it *during setup* — the password reaches a command line, so it is briefly in the process list and can land in the journal. The installer detects this and says so, which is honest, but no requirement in the record admits the exposure exists. | R-14, D-011, D-A5, D-A12 | **M** |
| 9 | **Stopping the capability takes effect promptly** | Stopping or restarting waits the full default timeout because the compositor does not answer the first request — ninety seconds, with a frozen console for the whole of it. Observed repeatedly on 2026-09-14. The immediate lever is a shorter stop timeout; the real question is why it does not answer at all, which is the same silence behind the root cause found that day. Whether this becomes a promise to adopters, rather than only a fix, is the author's call. | R-9, R-11, D-017 | **S** |
| 10 | **Watch what a terminal does when the connection drops** | Where error handling starts, and it starts with watching rather than coding. Pull the network on a working terminal. If the client sits there showing its own dialog instead of exiting, neither the shell loop nor the supervisor ever fires and item 12's fix changes nothing. **Must happen before item 12 is written.** Needs item 2 first — you cannot drop a connection that never worked. | R-18, D-A2 | **XS** |
| 11 | **No configuration means a message and a stop, never a local application** | **Observed 2026-09-14, not merely read:** with no profile found, the client shows a connection editor and a file chooser, and its own kiosk flag does not prevent this. The exact outcome the problem statement is written against. Blank ships first; a message is separate work, because nothing may draw beside the session without a new component. Also harden the real connection so the toolbar, tabs and escape hotkeys are gone. Needs item 3 to define what invalid means. | R-6, R-17, D-020, D-A1 | **S** |
| 12 | **Make recovery one layer's job, and make failure visible** | Two layers promise recovery, so neither does it, and a terminal that has failed for three days reports itself healthy. **Answered 2026-09-14 (ADR-0007): the startup system can carry all of it, including increasing backoff, and the loop in the runner goes.** The runner becomes a launcher — it picks the profile, then hands over. A broken configuration exits with a distinct status and the capability stays stopped, which is D-020's stop half, mechanically. **Three parts are safe to build now** — removing the loop, the distinct exit status, and not capping retries. **The backoff numbers are not**, because they tune for an event nobody has watched: run item 10 first. **And one thing must move in the same edit:** the console is returned to its normal state on every stop, which is harmless while the runner never exits and becomes a text login prompt in front of a child on every reconnect once it does.  **Evidence against the plan, 2026-09-23:** a terminal sat with a dialog on its screen while every channel an administrator has reported it healthy — **including the journal**, which ADR-0007 names as the fallback signal when the unit state cannot carry one. The fallback was watched failing. Why is unexplained and is recorded as unexplained. | R-18, R-17, D-005, D-020, ADR-0007 | **S** |
| 13 | **Reliability, error handling and recovery — specify before building** | What a terminal owes an administrator when it is stuck: what is recorded, what is visible, what is silent. Specify it before implementing, not during. **The author's position, 2026-09-14: the startup system alone may not be enough and the approach will probably need refining.** ADR-0007 says it is sufficient, with two caveats worth re-reading when this is picked up. First, its restart counter never decays — a terminal that has reconnected many times over months waits the full delay on the next one, which argues for a low cap rather than a different tool. Second, and larger: **no supervisor of any kind can supervise a client that never exits.** If the client stays on screen showing its own error, everything reports healthy and no policy at any layer fires. If refinement is needed, that is where it is needed — something that notices a stuck session and ends it — not a better restart policy. **Answered 2026-09-21 (D-026): the machine being connected to is not always on — design against 99% availability.** An outage is an ordinary event, so a terminal waits through it rather than reporting a fault, and a single wait can run to hours. But the exposure is the overlap between an outage and somebody wanting to use a terminal, not the downtime itself, and that overlap is small and rare — so a blank screen during an outage is a low-frequency annoyance rather than the thing to design around. **The asymmetry is the useful part here: an outage rarely collides with use, while a genuine fault always does.** One open question still feeds this: what a person at the terminal sees, and for how long, while the wait is happening. | R-18, D-026, ADR-0007 | **M** |
| 14 | **Run it on real hardware, end to end** | One virtual machine is not hardware. Until an old machine is converted, used and turned back, the record's confidence rests on a VM and a careful read. **Three things to check before assuming a Raspberry Pi qualifies, identified 2026-09-14:** the client's version, because a distribution on stable repositories may ship one too old for the launch flags this depends on — under D-024 that machine does not qualify at all; whether the compositor runs on that machine's graphics, which is where "no particular hardware is assumed" gets tested for real; and the architecture-specific plugin path in the unit, which is already handled. | all `real` R-n, R-1, R-2, D-024 | **M** |
| 15 | **Write the reader-facing explanation** | R-13 is a promise to people who have not installed anything: what qualifies, what changes on their machine, how to undo it. **Publishing happened first, on 2026-09-23** — the project is on GitHub and the prototype warning has been removed, so `README.md` is now the first and only thing a stranger meets. It was written as a lab procedure for the author (ADR-0006) and it assumes a reader comfortable being told that a failed connection reports itself healthy. The ordering this item assumed — explanation first, publication after a product whose failures are handled — no longer holds, so the open question is whether the README now partly satisfies R-13 or has quietly taken an audience it was not written for. `alternatives.md` already answers "why not use something else". | R-13, D-010, ADR-0006 | **M** |

## Item 7, broken down

Certificate pinning is one piece of work in four parts. They land in this order
because each needs the one before it.

| # | Part | Why here |
|---|---|---|
| 7a | ~~**The probe**~~ **DONE 2026-09-23** | Built, reviewed twice, fixed twice. 61 tests, no live host needed, standard library only. Both review rounds found real defects in the taxonomy — a crash that could be read as a verdict — and the second found the same flaw inside the first fix. |
| 7b | **Capture and confirm, inside setup** | Setup shows the fingerprint, the administrator confirms it (D-029), the pin is written, and the accept-anything setting leaves the profile **in the same change** — until it does, no pin has any effect. Needs Test 8 first, to establish where the pin is read from on the machine it is written on. |
| 7c | **Undo removes the pin** | The pin sits outside the product's own directory and changes how every remote desktop client on that machine behaves. Left behind, it breaks R-11. |
| 7d | **The runner checks before launching** | A certificate that no longer matches stops the terminal permanently and says why where an administrator can read it (D-028), instead of retrying for ever. |

**Running setup again must work (D-031).** An administrator whose target certificate
has changed will re-run setup to update it, so 7b has to be safe on a machine that
already has a profile, a stored credential and a pin. Today setup overwrites the
profile and asks for the password again — not broken, but it re-asks for
everything, and every re-ask is a chance to enter something different. Whether it
should detect an existing terminal and offer to update only what changed is a
design question for 7b. Nothing in the record has ever watched setup run twice.

## Also true, and not on the list

- **Which old machines actually qualify?** D-003 limits terminals to apt-family
  Linux with Wayland and systemd. The Raspberry Pis qualify. The old iMac and
  the old PC were never recorded. If either is outside the family it is out of
  scope by our own decision, and item 2 has one fewer machine to try.
- **Reversibility is claimed, never demonstrated.** Nobody has converted a
  machine, switched it off, and confirmed they got the machine back. Folded into item 14.
- **The connection profile at the repository root must never be tracked.** The
  author states it is temporary. Item 1 is what stops an accident.
- **Done 2026-09-14: the prototype files and `docs/` are committed** as
  `v0.0.1`, behind a `.gitignore` that excludes every `*.remmina` profile and
  `remmina.pref`. Item 1 is closed.
- **`alternatives.md` is written.** The named projects and their liveness
  checks are kept in `docs/architecture/stack.md` and ADR-0005, so the product
  record carries no product names or version numbers that age.

## Withdrawn
- **R-7** (nobody is signed in for you; anyone with valid credentials can use
  any terminal) was withdrawn under D-015. Signing in happens inside the
  connection. Nothing is owed against it and the number is retired.

## Open questions
Three, all in `docs/product/NOTES.md`, all needing the author.

- `Q-P2` — what R-14 should promise a reader about the stored credential. Its
  technical half is answered; what is left is what the record says. **Item 8.**
- Whether the encryption key must travel between machines, or can be born on
  the terminal. **Item 3**, and Test 6 answers it.
- What a terminal shows, and for how long, while it waits for a machine it
  cannot reach. **Item 13**, and R-18 needs it.

Closed 2026-09-21: whether the machine being connected to is always on. It is
not — D-026 sets the expectation at 99% availability, which makes an outage an
ordinary event a terminal must sit through rather than a fault to surface.

Everything else raised by the architect's read of the prototype was answered
and closed as D-016 through D-022, including the name collision (D-022).

## Not for this file
Implementation detail. `docs/architecture/` holds it: `debt.md` for built
things that are wrong, `stack.md` and `adr/` for the choices, and its own
`NOTES.md` for what is still open there.
