# ADR-0004 — RDP is the protocol
- **Date:** 2026-09-13 (recorded; the choice was made earlier and undated)
- **Kind:** reversible

> **Reconstructed from code.** `encore-kiosk.remmina.template:49` sets
> `protocol=RDP`.
>
> *Citation moved 2026-09-23. It used to point at
> `group_rdp_server_server.remmina:38`, an untracked personal connection
> profile at the repository root which is not shipped and will never exist on
> an adopter's machine. The template is the artifact we ship and it says the
> same thing. The decision is unchanged. FreeRDP 3.31 was the implementation
> observed working on 2026-09-23.*

## Context
D-002 puts the machine being connected to out of scope, so the protocol is
really chosen by whatever that machine already accepts. But the choice still
constrains us, because audio (R-12, C-5) is a protocol feature and each
protocol handles it differently.

## Options

**RDP** (via FreeRDP inside Remmina). Carries bidirectional audio as part of
the protocol, redirects devices, and negotiates resolution.
*Forever cost:* the far machine must run an RDP server; on Linux that usually
means xrdp or GNOME's built-in remote desktop, each with its own quirks. We
cannot help with any of it, because D-002 says we do not touch that machine.

**VNC.** Simpler and more universal.
*Forever cost:* no audio in the base protocol at all, which makes R-12 and C-5
impossible to satisfy. That alone rules it out.

## Decision
RDP, because it is the only one of the two that carries sound in both
directions, and D-014 makes two-way audio a requirement rather than a nicety.

## Consequences
**Easier:** R-12 becomes a configuration problem rather than an impossible one.
Resolution negotiation comes free.

**Harder:** the adopter's own machine must accept RDP, and we have made that
their problem by decision (D-002). A stranger whose host only does VNC is
excluded, and the written explanation (R-13) has to say so plainly.

**Currently contradicted by the code:** the shipped profile sets `sound=off`
and leaves `microphone=` empty — the one reason this protocol was chosen is
switched off. See items D-A* in `debt.md` and C-5 in `constraints.md`.

## Revisit when
Someone needs a terminal against a host that cannot speak RDP. Because Remmina
is plugin-based (ADR-0001), changing this is a profile edit rather than a
rewrite — which is why this is marked reversible.
