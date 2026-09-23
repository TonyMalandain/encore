**Mode:** non-commercial

# Product knowledge base — index

**Last restructure:** 2026-09-13

This project is a personal side project, published so that strangers can use
it. There is no buyer, no price, and no go-to-market, so there is no `icp.md`
and no `positioning.md`.

| Doc | What's in it |
|---|---|
| `NOTES.md` | Append-only working log, in date order. Where a fact lands before it reaches a formal document, and where the open questions and handoffs live. |
| `users.md` | The four roles that touch the product, including the stranger deciding whether to try it. |
| `problem.md` | A short essay: old machines going unused, the afternoon of hand-assembly, and why a half-converted machine is worse than none. |
| `solution.md` | Prose describing the envisioned product, then requirements `R-1`..`R-18`, each marked `real` or `intended`. Also what the solution is not. |
| `alternatives.md` | Why the project exists when thin-client platforms already do. Written for the stranger, in categories rather than product names. |
| `decisions.md` | Dated decision log, `D-001`..`D-027`. Superseded entries stay, marked. Closed decisions only. |
| `glossary.md` | Terms in users' words. The architect may add the code-side name for each. |

Other documents appear here only when there is something true to put in them.

## Rules this knowledge base is kept to
- **`problem.md` and `solution.md` are prose first, and a matched pair.** The
  problem is a short essay a stranger can read and argue with. The solution
  opens with prose, then lists the numbered `R-n` requirements it implies.
  There is no separate scope or capabilities document.
- **They agree by being read, not by matching identifiers.** Whenever either
  changes, read both end to end: is every pain answered or named as a stated
  exclusion, and does every `R-n` trace back to something the problem says?
- **`real` and `intended` are truth markers, never a schedule.**
- **These documents have no clock.** No roadmap, phases, priorities, effort,
  todos or delivery status. Anything with a clock in it belongs in
  `BACKLOG.md` at the project root, which is not product documentation.
- **Nothing here describes how the product works.** If a sentence would stop
  being true after a rewrite on a different stack, it belongs to the architect
  in `docs/architecture/`. Mechanism is logged in `NOTES.md` as a `handoff`.
- **`decisions.md` holds closed decisions only.** Open questions live in
  `NOTES.md` as `Kind: question` until they are answered or ruled out.

## Health of this record
- **No requirement has been observed working on an old machine.** On
  2026-09-14 a terminal was watched reaching a remote session on a virtual
  machine, which is the first evidence in this record that anyone watched
  rather than read; on 2026-09-23 that was repeated on a virtual machine
  converted from nothing by following the written procedure. Everything else
  rests on a read of the prototype. Where a `real` requirement carries an
  evidence line, that line says which it is.
- **R-6 — the person at the terminal sees nothing but the remote session — is
  the product's central promise and is marked `intended`, not `real`.** It was
  marked `real` until that read found two ways out of the remote session, and
  both have since been watched happening.
- **Two questions are open and need the author**, not the architect and not the
  product manager. They are in `NOTES.md`: what the stored credential can
  honestly promise (`Q-P2`), and what a terminal shows — and for how long —
  while it waits for a machine it cannot reach. A third, whether the encryption
  key must travel between machines, was answered by experiment on 2026-09-23:
  it does not.

## Not part of this record
- `docs/product-ignore/` — excluded by the author. Not read, not maintained.
- `BACKLOG.md` — delivery status, not product truth.
