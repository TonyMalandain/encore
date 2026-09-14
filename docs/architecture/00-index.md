# Architecture knowledge base — index

**Last restructure:** 2026-09-13 (the working log was folded into the formal
documents on this date; the record itself was opened the same day by reading
the prototype)

This is the engineering half of the record. `docs/product/` says what the
product is for and what was decided; this says what shape it has and why.
Mechanism — paths, units, config keys, protocols, libraries — lives only here.

| Doc | What's in it |
|---|---|
| `NOTES.md` | Append-only working log. **Empty of findings** — everything folded on 2026-09-13. Four open questions remain, one of them closed and kept as a record. |
| `overview.md` | The system on one page, with a diagram: four components, one boundary, and how the record was started. |
| `boundaries.md` | The five parts, what each owns, and the configuration boundary that does not exist yet. |
| `interfaces.md` | Six contracts, all of them files or paths — which are public, which are fragile, and that the RDP contract now includes the host's identity. |
| `data.md` | The complete data inventory, the honest account of the one secret, and why the profile cannot travel without its key file. |
| `constraints.md` | The environment, the absolutes, the fleet size of two or three, and the one real conflict in the design. |
| `stack.md` | Every part, all of them adopted, none of them pinned — plus why `remmina-gnome` and the platforms were rejected. |
| `debt.md` | Eleven items found by reading the prototype, worst first, with what each is waiting on. |
| `adr/` | Six decisions: four reconstructed from code, two the author's own. |

## Decisions on file

| ADR | Decision | Kind | Status |
|---|---|---|---|
| ADR-0001 | Remmina is the remote desktop client | reversible | accepted; deciding reason **confirmed by the author** 2026-09-13 |
| ADR-0002 | `cage` is the single-window Wayland compositor | reversible | accepted (reconstructed) |
| ADR-0003 | An isolatable systemd target is the on/off switch | **one-way door** | accepted (reconstructed); name and `Wants=`/`Requires=` to settle before publication |
| ADR-0004 | RDP is the protocol | reversible | accepted (reconstructed) |
| ADR-0005 | Assemble from systemd parts, not a thin-client platform | reversible | accepted (author's own reasoning) |
| ADR-0006 | The README is a lab procedure, not the reader-facing explanation | reversible | accepted — **architect's call, not yet ratified by the author** |

**None is superseded.** ADRs are never renumbered or deleted; a replaced one is
marked superseded in place.

**ADR-0002 to ADR-0004 are reconstructed, not recorded.** The choices are real
and visible in the code; the reasons were never written down, so the Context
and Options sections are the architect's reconstruction and are marked as such
at the top of each file. The author should confirm or correct the deciding
reason in each.

**ADR-0001 was reconstructed and has since been confirmed.** On 2026-09-13 the
author gave the reasoning: wide apt availability, and — the load-bearing one,
which the reconstruction had missed — that Remmina's own GUI builds reusable
configuration files. The author is not committed to Remmina if something
better appears; the one live trigger is whether the profile format can carry
certificate pinning and audio defaults, which is to be decided inside the
configuration design (item D-A7 in `debt.md`), not before it.

**ADR-0005 is the author's own**, given on 2026-09-13. It is the standing
answer to "why not LTSP?".

**ADR-0006 is the architect's call and has not been ratified.** The author
asked for install instructions; writing them as a lab procedure, and holding
R-13's reader-facing explanation back as a separate later document, was a
choice made on their behalf. It is on file so that it can be overruled easily
rather than absorbed silently.

## How to read this record

1. **`overview.md` first.** It is one page and it is the whole system.
2. **`debt.md` second, if you are about to change anything.** Eleven items,
   and the top three are the difference between a terminal and an unmanaged
   computer in a child's bedroom.
3. `NOTES.md` for the questions still waiting on a human.

## Health of this record

- **Nothing here has been observed at runtime.** `which remmina cage`,
  `getent passwd kiosk` and `ls /var/lib/kiosk` all returned empty on the
  development machine on 2026-09-13, no unit is installed, and `BACKLOG.md`
  confirms nothing has been run end to end on any old machine. The terminals
  themselves are elsewhere and unobserved. Every behavioural claim is a code
  read. Findings reasoned from documented behaviour rather than observed are
  marked `assumed` where they appear.
- **The product record no longer claims otherwise either.** After the
  architecture report of 2026-09-13 the product manager downgraded R-6 from
  `real` to `intended` and retired the phrase `verified in code` across the
  whole requirement set in favour of "read in code, never observed". The
  strongest evidence in this project, on both sides, is now openly stated to
  be a code read.
- **File-line references were re-checked against the repository root on
  2026-09-13** — `remmina-kiosk.sh`, `remmina-kiosk.service`, `kiosk.target`
  and `group_rdp_server_server.remmina`. All of them still point at the line
  they describe; none is stale. **No file-line reference has ever been checked
  against a deployed system**, because there is not one.
- One reference *outside* this record is stale and is not ours to fix:
  `BACKLOG.md`'s R-13 row still says "there is no readme". `README.md` exists
  as of 2026-09-13 — see ADR-0006 — but it is a lab procedure and does not
  satisfy R-13.

## Open contradictions

Three. None is resolved here, because in each case both sides still hold.

**1. The virtual consoles serve R-6 and R-10 in opposite directions.**
*(both sides recorded 2026-09-13)*
Leaving consoles 1–6 as text logins is how the administrator reaches a machine
whose screen is gone (R-10); it is also how the person at the terminal leaves
the remote session (R-6). Recorded in `constraints.md` and as question Q-1 in
`NOTES.md`. Note the correction of the same date: disabling VT switching is
**not** "the cost D-006 already accepted" — D-006 accepted the lock-out risk
while a console still existed as a way in, so closing it accepts a strictly
larger cost. Needs the author, not the architect.

**2. What replaces the no-profile fallback.**
*(both sides recorded 2026-09-13)*
- `debt.md` item D-A1 says the repayment is to "show a static 'not configured'
  screen, or let the unit fail loudly".
- ADR-0002 says that showing anything of our own beside the session is **no
  longer possible without adding a component**, because that is exactly what
  `cage` was chosen to prevent — and `docs/product/users.md` names "a black
  screen" as a reason the person at the terminal gives up, so the blank
  console that a bare deletion leaves behind is a real cost too.

Blank is safer than a file chooser and should ship first; that much is agreed.
What it becomes afterwards is not decided, and it collides with ADR-0002 head
on.

**3. Whether removing the shell loop produces a failure signal at all.**
*(both sides recorded 2026-09-13)*
- `debt.md` item D-A2's recommendation is to delete the `while true` loop and
  let systemd supervise, so that repeated failures surface as a failed unit.
- The same day's finding, citing
  [Remmina issue 3113](https://gitlab.com/Remmina/Remmina/-/issues/3113), is
  that Remmina does not exit on a dropped connection by default — in which
  case the process never exits, the restart layer never fires, and deleting
  the loop changes nothing about the silence.

Both are code-and-upstream reads, neither is observed. The exit behaviour must
be established on real hardware before D-A2 can be called fixed. Related but
distinct: whether anyone is *owed* a signal is an open product question (Q-5 in
`NOTES.md`).

## Related records, not part of this one

- `docs/product/` — the problem, the requirements, the product decision log.
  Not editable from here.
- `docs/product/glossary.md` — shared. Code-side names may be added there.
- `README.md` — the install-and-test procedure for the prototype. Ours, and
  governed by ADR-0006.
- `BACKLOG.md` — delivery order. Tracks *unbuilt* work; `debt.md` tracks
  *built* things that are wrong. Items D-A1 and D-A2 appear there under "Built
  and wrong" as one piece of work.
- `docs/product-ignore/` — excluded by the author. Not read.
