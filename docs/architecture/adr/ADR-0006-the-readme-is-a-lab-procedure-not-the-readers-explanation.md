# ADR-0006 — The README is a lab procedure, not the reader-facing explanation
- **Date:** 2026-09-13
- **Kind:** reversible

**Attribution, corrected 2026-09-13.** The restructure first recorded this as
the author's own decision. It was not. The author asked for "a clear README
with clean install instructions" in order to run the first test; **the choice
to write it as a lab procedure rather than an install guide, and to keep R-13's
reader-facing explanation as a separate later document, was the architect's.**
The author has not yet seen or approved that framing. It is recorded as a
decision because it is made and is shaping the repository, not because it was
ratified.

## Context
The prototype is deployed by hand and has never been observed running end to
end. Two defects (items D-A1 and D-A2 in `debt.md`) make it unsuitable to put
in front of a child. At the same time the author needs written steps in order
to run the first real test at all, and `BACKLOG.md` records R-13 — a written
explanation a stranger can act on — as unbuilt, with the note "there is no
readme".

Those are two different documents wanting the same filename.

## Options

**One document.** A single `README.md` that both installs the prototype and
explains the product to a stranger.
*Forever cost:* it has to be optimistic to serve the stranger and honest to
serve the test, and it cannot be both. Publishing install steps for a
prototype that shows a child a file chooser is the "half-converted machine"
the problem statement warns about.

**Two documents, written at different times.** An engineering install-and-test
procedure now; the reader-facing explanation (R-13) later, once there is
something observed to describe.
*Forever cost:* two files to keep in agreement, and a period where the
repository's front page is addressed to the author rather than to a visitor.

## Decision
Two documents. `README.md` is, for now, **a lab procedure**: installation of
the prototype exactly as it stands, a five-test diagnostic sequence, and a
plain statement that nothing has been observed running and that two known
defects make it unsuitable to put in front of a child.

Honest steps for a broken prototype are more useful than optimistic ones for
an imagined finished one. The reader-facing explanation R-13 promises is
deliberately **not** written yet: it is the product manager's to shape, and it
should not be written while there is still nothing observed to describe.

## Consequences
**Easier:** the first real test can be run from written steps, and the
warnings in those steps are allowed to be blunt.

**Harder:** `BACKLOG.md`'s R-13 row now needs care — the existence of a
`README.md` must not be read as R-13 being satisfied. The row's note "there is
no readme" is stale as written.

**No longer possible:** treating the repository front page as marketing while
the prototype is unobserved.

## Revisit when
The prototype has been observed running end to end and D-A1 and D-A2 are
fixed. At that point R-13 can be written against something real, and the two
documents should be reconciled — or merged, if the lab procedure has shrunk to
an install section.
