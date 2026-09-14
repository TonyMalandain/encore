# ADR-0005 — Assemble from systemd parts rather than adopt a thin-client platform
- **Date:** 2026-09-13
- **Kind:** reversible

This is the standing answer to "why didn't you just use LTSP?" — a question
`BACKLOG.md` predicts every stranger will ask. Unlike ADR-0001 to ADR-0004,
this one is **not reconstructed**: the reasoning is the author's own, given on
2026-09-13.

## Context
Thin clients are a solved problem with mature projects behind them. Building
anything ourselves needs justifying against them, and `stack.md` sets a high
bar for writing code when something already exists.

The fleet this is built for is **two or three machines in one household**
(C-7). That number is the whole argument, because every established thin-client
platform is built for the opposite case.

## Options

**Adopt LTSP.** The long-standing Linux thin-client project, with a documented
Remmina kiosk recipe.
*Forever cost:* it is a fleet platform. Clients network-boot from a centrally
managed image, so adopting it means standing up and operating boot
infrastructure, and in practice installing and learning a distribution chosen
to host it. That is a second system to understand, keep patched and debug at
3am, permanently — to manage three machines. It also conflicts with the
product's own premise: the solution record says explicitly this is "a
capability you add to a machine you already have, rather than an operating
system you install over it", because reimaging defeats the reuse the project
exists for.

**Adopt a kiosk distribution** (Thinstation, porteus-kiosk, ThinLinc).
*Forever cost:* same shape — an image replaces the machine, so the old computer
stops being itself. Directly contradicts D-007 and R-11, since "give me my
machine back" is not a thing a reimage can offer.

**Assemble from parts already on the machine** — a systemd target, a service,
a kiosk compositor, a remote desktop client.
*Forever cost:* we own the assembly. No central management, no fleet view, no
push of configuration — every terminal is configured on its own, and that hole
is real and currently unfilled (item D-A7 in `debt.md`). Upstream changes in
any of the four parts can change behaviour under us, and nothing is version
pinned.

## Decision
Assemble from parts, because **at two or three clients the platforms cost more
than the problem does.** Each one asks the adopter to learn a new distribution
and a new deployment technique in order to avoid writing sixteen lines of
shell. The parts are already installed on any common Linux, which is also what
makes the result deployable on whatever is in the cupboard.

## Consequences
**Easier:** no new distribution, no boot infrastructure, no second system to
learn. The product installs onto a machine that already boots, which is the
premise the whole product record rests on. Reversibility (R-11) stays cheap
because we add files instead of replacing an operating system.

**Harder:** every service a platform would have provided is now ours or
nobody's — central configuration above all. **LTSP would have given
configuration management away for free, and that is precisely the largest hole
in this design.** This decision does not avoid that work; it chooses to do a
small version of it locally instead.

**No longer possible:** claiming this scales. It is not a fleet tool and should
never be described as one.

## Revisit when
The number of terminals reaches roughly a dozen, or terminals appear in more
than one household — the point at which configuring each machine individually
costs more than operating a platform would. Watch for the symptom rather than
the count: the first time a change has to be applied to every terminal by hand
and one gets missed.
