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

## The state of things, in one line
The prototype is deployed by hand and has never been watched working. The
positive path — one terminal, one connection, a session on the screen — has not
been achieved yet, and the author suspects the connection profile was at fault.

## The order, and why it is this one
Set by the author on 2026-09-13: **get the positive path working, then make it
installable, then handle the failures.** Nothing on the error-handling half is
worth designing against a connection nobody has seen succeed, and every fix
below item 9 is a guess until item 2 lands.

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
| 1 | **Add a `.gitignore`** | Out of competition — two minutes, and the only item that gets worse rather than staying the same. One `git add -A` puts the connection profile, with its recoverable password, into history permanently. | — | **XS** |
| 2 | **Get one terminal connecting, end to end** | **The primary goal. Root cause found 2026-09-14:** the capability opens its session on a console that is never in the foreground, so the session is never activated and the compositor waits for a screen it is never given. Everything else observed that day — silence in the log, black screen, frozen console switching, hanging stop — is that one fault. One old machine, one working connection, a session on the screen, watched by a human. The previous attempt did not reach this, suspected to be a bad connection profile. Everything else on this list is a guess until this succeeds: the recovery argument, the failure-handling design, and every `real` requirement marked `read in code`. Decide while doing it what "working" includes — in particular whether sound counts, or whether item 5 is separate. | all `real` R-n | **M** |
| 3 | **A configuration step: the target machine, and the encryption key** | Hand-editing the profile is the suspected cause of item 2's failure, and it is why the product exists only on the author's own machines. Where configuration lives, how it is set, how it is changed, and what makes it invalid — that last part is what item 11 needs. **Must settle where the encryption key comes from (D-025).** Observed 2026-09-14: a terminal cannot read its stored credential without a key file present. Unresolved: whether that key must be copied from the machine where the profile was built, or can be created on the terminal and the credential set there afterwards. Either way it is established per deployment and never shipped — a key that is the same everywhere protects nothing while reading as protection. | R-5, D-002 | **L** |
| 4 | **Ship as an installable package** | What turns a personal setup into something that can be put on a second machine the same way twice: versions, upgrades that must not break a working terminal, clean removal, declared prerequisites. **Must declare the minimum versions it needs (D-024)** — an adopter on an older release currently gets a terminal that fails in ways nothing describes. **Renames: partly done 2026-09-14.** The units are `encore-kiosk` (D-022) and the system user, group and home directory are `encore` (D-023) — both done in the repository, and the migration path for an already-converted machine is untested beyond one VM. Still open: "kiosk" must stop naming a machine anywhere it still does (D-018). `README.md` documents the old names in its install and removal steps and has to change with them, or the removal instructions will leave an orphaned account behind. The current names carry no product prefix and carry the remote desktop client's name, which the architect may one day replace. | R-4, D-003, D-018, D-022, D-023 | **L** |
| 5 | **Audio works in both directions, out of the box** | Output, and input where the machine has a microphone, default with no device-picking, and the host's devices stay out of the session. A terminal with no microphone must still be fully usable. Old machines vary, so this needs checking on each kind. Part of the positive path, not of error handling. | R-12, D-009, D-014 | **M** |
| 6 | **Ordinary users cannot deactivate** | No record that this is enforced. Cheap, and it is half of what the lock means. D-017 puts the whole arrangement on there being no ordinary accounts on a terminal, which nothing checks. | R-9, D-006, D-017 | **S** |
| 7 | **Confine what the capability can reach** | It runs unprivileged already. Not done: pinning the connection to the one configured machine rather than whatever answers to its name, and closing the shared clipboard. **And a protection was dropped on 2026-09-14 to get a working session** — the setting that hides other users' home directories also hides the directory the graphical session needs. It has to come back in a form that does not break startup, or D-012's promise is weaker in fact than in writing. | R-16, D-012, D-019 | **M** |
| 8 | **Settle what the stored credential can honestly promise** | R-14 promises more than anything can deliver on an unattended machine. **Observed 2026-09-14:** the client asked for a keyring to be unlocked, which no unattended terminal can answer — so the only storage that works here is the reversible file-based one. That is the answer to `Q-P2`'s technical half; what remains is the author deciding what R-14 says to a reader. Ties to item 7: a credential that can be handed to an impostor was never protected by being hard to read. | R-14, D-011, D-A5 | **M** |
| 9 | **Stopping the capability takes effect promptly** | Stopping or restarting waits the full default timeout because the compositor does not answer the first request — ninety seconds, with a frozen console for the whole of it. Observed repeatedly on 2026-09-14. The immediate lever is a shorter stop timeout; the real question is why it does not answer at all, which is the same silence behind the root cause found that day. Whether this becomes a promise to adopters, rather than only a fix, is the author's call. | R-9, R-11, D-017 | **S** |
| 10 | **Watch what a terminal does when the connection drops** | Where error handling starts, and it starts with watching rather than coding. Pull the network on a working terminal. If the client sits there showing its own dialog instead of exiting, neither the shell loop nor the supervisor ever fires and item 12's fix changes nothing. **Must happen before item 12 is written.** Needs item 2 first — you cannot drop a connection that never worked. | R-8, D-A2 | **XS** |
| 11 | **No configuration means a message and a stop, never a local application** | **Observed 2026-09-14, not merely read:** with no profile found, the client shows a connection editor and a file chooser, and its own kiosk flag does not prevent this. The exact outcome the problem statement is written against. Blank ships first; a message is separate work, because nothing may draw beside the session without a new component. Also harden the real connection so the toolbar, tabs and escape hotkeys are gone. Needs item 3 to define what invalid means. | R-6, R-17, D-020, D-A1 | **S** |
| 12 | **Make recovery one layer's job, and make failure visible** | Two layers promise recovery, so neither does it, and a terminal that has failed for three days reports itself healthy. The same fix settles whether the capability counts as started when the session never opened. Test with item 11 and only after item 10. | R-8, D-A2, D-A3 | **S** |
| 13 | **Specify failure handling, then build it** | What a terminal owes an administrator when it is stuck: what is recorded, what is visible, what is silent. It must be specified before it is implemented, not during. Raised as `Q-P3` and turned into work rather than left as a question. | R-8, R-10 | **M** |
| 14 | **Run it on real hardware, end to end** | One virtual machine is not hardware. Until an old machine is converted, used and turned back, the record's confidence rests on a VM and a careful read. **Three things to check before assuming a Raspberry Pi qualifies, identified 2026-09-14:** the client's version, because a distribution on stable repositories may ship one too old for the launch flags this depends on — under D-024 that machine does not qualify at all; whether the compositor runs on that machine's graphics, which is where "no particular hardware is assumed" gets tested for real; and the architecture-specific plugin path in the unit, which is already handled. | all `real` R-n, R-1, R-2, D-024 | **M** |
| 15 | **Write the reader-facing explanation, and publish** | R-13 is a promise to people who have not installed anything: what qualifies, what changes on their machine, how to undo it. `README.md` exists but does not satisfy R-13 — it is a lab procedure aimed at the author debugging the prototype (ADR-0006). Last on purpose: a stranger who follows it must land on a product whose failures are handled. `alternatives.md` already answers "why not use something else". | R-13, D-010 | **M** |

## Also true, and not on the list

- **Which old machines actually qualify?** D-003 limits terminals to apt-family
  Linux with Wayland and systemd. The Raspberry Pis qualify. The old iMac and
  the old PC were never recorded. If either is outside the family it is out of
  scope by our own decision, and item 2 has one fewer machine to try.
- **Reversibility is claimed, never demonstrated.** Nobody has converted a
  machine, switched it off, and confirmed they got the machine back. Folded into item 14.
- **The connection profile at the repository root must never be tracked.** The
  author states it is temporary. Item 1 is what stops an accident.
- **The prototype files and `docs/` are untracked.** The repository still shows
  only its initial commit.
- **`alternatives.md` is written.** The named projects and their liveness
  checks are kept in `docs/architecture/stack.md` and ADR-0005, so the product
  record carries no product names or version numbers that age.

## Withdrawn
- **R-7** (nobody is signed in for you; anyone with valid credentials can use
  any terminal) was withdrawn under D-015. Signing in happens inside the
  connection. Nothing is owed against it and the number is retired.

## Open questions
One, in `docs/product/NOTES.md`.

- `Q-P2` — what R-14 should promise a reader about the stored credential. This
  is item 5 above.
Everything else raised by the architect's read of the prototype was answered
and closed as D-016 through D-022, including the name collision (D-022).

## Not for this file
Implementation detail. `docs/architecture/` holds it: `debt.md` for built
things that are wrong, `stack.md` and `adr/` for the choices, and its own
`NOTES.md` for what is still open there.
