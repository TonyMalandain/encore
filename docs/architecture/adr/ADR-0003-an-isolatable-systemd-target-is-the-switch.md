# ADR-0003 — An isolatable systemd target is the on/off switch
- **Date:** 2026-09-13 (recorded; the choice was made earlier and undated)
- **Kind:** one-way door

> **Reconstructed from code.** `kiosk.target` declares `AllowIsolate=yes`,
> `Requires=multi-user.target`, and `Wants=remmina-kiosk.service`.

## Context
Three requirements land on one mechanism. R-4: converting a machine is an
install, a short configuration, and an activation. R-9: only root can
deactivate. R-11: deactivating returns the machine to what it was, with no
repair by hand. C-3 makes that last one an absolute.

Whatever carries the switch is the thing a stranger will read about, type, and
depend on — so it is effectively public interface.

## Options

**A custom systemd target, isolatable** — activation is
`systemctl set-default kiosk.target`, deactivation is setting the default back.
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
`kiosk.target` deserves one moment of thought before publication — it is
generic enough to collide with another package on the same machine. A namespaced
name such as `thinclient-kiosk.target` costs nothing today and is impossible
later.

## Revisit when
Before the first published release — specifically to settle the target name and
the `Wants=` / `Requires=` question. After publication this decision is
effectively frozen.
