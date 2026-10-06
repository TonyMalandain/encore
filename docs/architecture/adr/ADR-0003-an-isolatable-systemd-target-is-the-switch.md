# ADR-0003 — An isolatable systemd target is the on/off switch
- **Date:** 2026-09-13 (recorded; the choice was made earlier and undated)
- **Kind:** one-way door

> **Reconstructed from code.** `encore-kiosk.target` declares
> `AllowIsolate=yes` (`:7`), `Requires=multi-user.target` (`:4`), and
> `Wants=encore-kiosk.service` (`:5`).
>
> *Citations corrected and re-checked 2026-09-23. The target was `kiosk.target`
> when this was written; D-022 renamed it on 2026-09-13 and the code shipped on
> 2026-09-14. The decision is unchanged.*

## Context
Three requirements land on one mechanism. R-4: converting a machine is an
install, a short configuration, and an activation. R-9: only root can
deactivate. R-11: deactivating returns the machine to what it was, with no
repair by hand. C-3 makes that last one an absolute.

Whatever carries the switch is the thing a stranger will read about, type, and
depend on — so it is effectively public interface.

## Options

**A custom systemd target, isolatable** — activation is
`systemctl set-default encore-kiosk.target`, deactivation is setting the
default back.
*Forever cost:* the target name becomes public and appears in every written
instruction, so it can never be renamed after publication; `isolate` is a blunt
instrument that stops everything not wanted by the target, so the target's
dependencies have to be right or the machine loses services it needed; and
`Wants=` versus `Requires=` becomes a correctness question (item D-A3 in
`debt.md`).

**Disable the display manager and enable one service** — activation is two
`systemctl` commands against existing units.
*Forever cost:* two commands instead of one, with no single name for the state.
"Is this machine a terminal?" has no one-line answer, and a half-applied pair
of commands is exactly the half-converted machine the problem statement warns
about. Also assumes a display manager exists to disable, which R-2's "no
particular hardware" and a bare apt install do not guarantee.

## Decision
A custom isolatable target, because **the state has to have a name**. R-11 and
C-3 require deactivation to be a single act that cannot be half-done, and a
target is the only systemd construct that makes "this machine is a terminal" a
single value you can read, set, and unset.

## Consequences
**Easier:** activation, deactivation and "which mode is this machine in" are
one command each. Reversibility is one symlink, so C-3 is satisfied almost for
free. Root-only (R-9) comes from systemd's own permissions, so nothing was
written to enforce it.

**Harder:** the target's dependency list is now load-bearing and unreviewed. If
it omits something the machine needed, isolating to it silently removes that
service.

**No longer possible:** renaming the target after a stranger has read the
instructions. This is why it is a **one-way door**, and it is why the name
deserved one moment of thought before publication — `kiosk.target`, as it was
originally written, is generic enough to collide with another package on the
same machine.

## Revisit when
Before the first published release — specifically to settle the target name and
the `Wants=` / `Requires=` question. After publication this decision is
effectively frozen.

---

## Addendum, 2026-09-23 — both "revisit when" conditions have been met and
## closed

This ADR asked for two things to be settled before publication. Both are
settled, and neither reverses the decision, so this is an addendum rather than
a supersession.

**1. The name.** Closed by D-022 and D-023 on 2026-09-13 and shipped on
2026-09-14: the target is `encore-kiosk.target` and the identity that runs it
is `encore`. This also closes question Q-4 in `NOTES.md` — "is `kiosk.target`
too generic a name to publish?" — which was asked on 2026-09-13 and answered
the same day by the author, before this ADR's citations were updated. The
namespaced form this section asked for exists; the prefix chosen was the
product's name rather than the repository's, which is what D-022 reasons
about.

**2. `Wants=` versus `Requires=`.** Closed by ADR-0007 on 2026-09-14 in favour
of `Wants=`, with the reason recorded there: under ADR-0007 the *service* is
the accountable object and its own state tells the truth, so `Requires=` adds
no signal — and it would tear the target down on precisely the failure where a
still, inspectable machine is worth most.

**The one-way door has been walked through.** `encore-install.sh:165-166`
prints both activation commands verbatim and `encore-uninstall.sh:81` compares
against the target name as a literal string. The name is now load-bearing in
code as well as in prose.

**What this ADR did not anticipate, and the record should carry it here** — *the
"untested" below was true until 2026-10-05 and is not any more; see the second
addendum at the end of this file:*
`systemctl isolate encore-kiosk.target` on a machine already running a desktop
did **not** bring the capability's console to the foreground. Whether a machine
that *boots* into the target behaves the same way is **untested** — Test 7 in
`docs/tests.md` has never been run. If boot is affected too, the `isolate`
half of this decision's "activation is one command" claim is weaker than
stated; if only `isolate` is affected, the lasting activation path is sound and
the fault belongs to switching away from a live session. Neither branch is
established, and this is recorded as untested rather than as either.

---

## Addendum, 2026-10-05 — the boot half of "activation is one command" has been
## watched, and it works

The section above records that `systemctl isolate encore-kiosk.target` on a
machine already running a desktop did not bring the capability's console to the
foreground, and that whether a machine which *boots* into the target behaves the
same way was **untested**, Test 7 never having been run. **Test 7 has now been
watched passing:** on 2026-10-05 a Fedora 44 machine was rebooted and came back
into a working session by itself, with nothing done by hand.

So of the two branches that section named, the second is the one that holds. The
`set-default` path — the lasting activation, and the one R-8 depends on — reaches
a session from a cold boot. The fault belongs to switching away from a live
session, not to the console choice, and `ExecStartPre=+/usr/bin/chvt 7` is
sufficient on the path that matters. This ADR's "activation is one command" claim
is intact on the boot form and still carries one unexplained failure on the
`isolate` form.

**This does not reverse or narrow the decision, so it is an addendum.** Two limits
on it, both worth keeping: it is **one machine, once**, and it is not the machine
the `isolate` failure was seen on — that was an apt VM and this was a dnf
machine, so the two halves of the comparison come from different systems. The
SELinux mode the boot came up in was not recorded either, which matters because
`docs/tests.md` test 14c's enforcing comparison is a pair of `isolate` calls and
explicitly does not reproduce boot conditions.
