# Contributing

This is a personal project published so other people can reuse it. It is small,
and the rules below are not ceremony — each one exists because skipping it cost
somebody an evening.

**The one thing to understand first.** This product's recurring failure is
*things reporting healthy while not working*: a terminal that has been broken
for three days telling every channel it is fine, a log that looks empty because
the query was wrong, a document that reads correct while being stale. Most rules
here are defences against that one shape.

## Contents

- [Where everything is written down](#where-everything-is-written-down)
- [Before you change code](#before-you-change-code)
- [Before you change documentation](#before-you-change-documentation)
- [Evidence rules](#evidence-rules)
- [Testing](#testing)
- [Never do these](#never-do-these)
- [Commits](#commits)

---

## Where everything is written down

| Where | What |
|---|---|
| [`docs/product/`](docs/product/) | What the product is for, who it serves, what was decided |
| [`docs/product/problem.md`](docs/product/problem.md) | The problem, in prose |
| [`docs/product/solution.md`](docs/product/solution.md) | The envisioned solution and its requirements, `R-n` |
| [`docs/product/decisions.md`](docs/product/decisions.md) | Closed decisions, `D-NNN` |
| [`docs/product/alternatives.md`](docs/product/alternatives.md) | Why not one of the existing thin-client projects |
| [`docs/architecture/`](docs/architecture/) | How it is built, and why it is shaped this way |
| [`docs/architecture/adr/`](docs/architecture/adr/) | Architecture decisions, `ADR-NNNN` |
| [`docs/architecture/debt.md`](docs/architecture/debt.md) | Everything known to be wrong, worst first, `D-An` |
| [`docs/tests.md`](docs/tests.md) | What to run on a converted machine, and what has been watched |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Every failure seen so far, and what caused it |
| [`docs/other-machine.md`](docs/other-machine.md) | What to set up on the machine terminals connect to |
| [`BACKLOG.md`](BACKLOG.md) | What order it gets fixed in — **and nothing else** |
| [`README.md`](README.md) | For somebody deciding whether to install this |

**`BACKLOG.md` is not product documentation.** It says order. What the product
is and what was decided live in `docs/product/` and are referenced by ID from
the backlog, never restated in it.

**Nothing is documented in two places.** Where a fact is needed twice, the
second place links to the first. Three copies of a command is three chances for
two of them to go stale — and both times that happened here, the stale copy was
the one somebody followed.

## Before you change code

1. **A ticket exists in `BACKLOG.md`** and names the requirements and decisions
   it serves.
2. **Read the decisions it names.** If your change contradicts one, that is a
   product conversation, not an implementation detail. Say so before building.
3. **Write the test first.** `docs/tests.md` is the record of what has been
   *watched*, and a change that cannot be watched cannot be claimed.
4. **Run the whole validation sequence and report the real output.** Not a
   summary of it. If tests fail, say so with the output.
5. **If part of the work is blocked, finish everything else and say what you
   left out and why.** Scaling the work down is the author's call.

## Before you change documentation

**Say what is true, and mark what is not yet known.**

- **Requirements carry a truth marker.** `real` means somebody watched it.
  `intended` means it is the design and nobody has seen it. **Never promote
  `intended` to `real` without an observation**, and name the machine and the
  date when you do.
- **Decisions are closed, numbered, and never edited in place.** A `D-NNN` entry
  gives *Decision*, *Why*, *Costs accepted*, *Source*. Changing your mind means
  a new decision that supersedes the old one, so the reasoning survives.
- **`NOTES.md` is append-only, in both `docs/product/` and
  `docs/architecture/`.** A correction is a new entry that supersedes an earlier
  one. **Do not edit the wrong entry away** — being wrong is part of the record,
  and the pattern of *how* the project got things wrong is worth more than a
  tidy file.
- **`problem.md` and `solution.md` quote each other word for word.** If you
  change a sentence in one that the other quotes, change both in the same
  commit. Check before committing.
- **No dates or schedules in `docs/product/`.** What the product is does not
  have a clock. Dates belong on observations.
- **Check every link and anchor resolves** before committing. A dead link in a
  troubleshooting file is found by somebody already having a bad evening.

**Two distinctions that keep getting confused:**

- A **known issue** is something this software does wrong. A **requirement** is
  something the machine must bring. Needing a certain version is not a defect.
- **"Nobody here has measured it" is not "nobody knows it."** Search first.
  Public knowledge does not need an experiment, and four times now the expensive
  path was taken to establish something already documented upstream.

## Evidence rules

**Do not reason from configuration to runtime.** The files saying a thing should
happen is not the thing happening. This has produced a wrong answer three times
on this project — a journal declared broken that was fine, a delay attributed to
code that never ran, and a security hole reported that did not exist. Each was a
confident argument from reading. **Go and measure it on a machine.**

**A failure you write down is worth more than a pass you assume.** The status
column in `docs/tests.md` is what was *watched*, never what is believed. "Never
run" is an honest entry and appears often.

**Before you write a check, ask it out loud: if the thing this checks were
absent, broken, or doing nothing, would this report anything different?** If
the answer is no, the check reports nothing and the pass is decoration. Ask it
*while writing*, because a check of this shape has by construction never been
seen to fail, so nothing will ever prompt the question later. This project has
met that failure six times — a loop over an empty list that passed having
examined nothing, a check satisfied by a file that did not exist, a package
that provided a decoder's name and decoded nothing. It is named and all six are
listed as `H-1` in
[`docs/architecture/constraints.md`](docs/architecture/constraints.md). Read it
before adding to `docs/tests.md`.

**Name the machine and the date on every observation.** A pass on the
development workstation is not a pass on a terminal; `/bin/sh` is `bash` on one
and `dash` on the other, and that difference has mattered.

**When something is reported working, say who watched it and through which
channel.** "It was heard" and "the log said so" are different claims.

## Testing

Tests live in `docs/tests.md`, in order, each with what has actually been
watched. Run them in order; each assumes the ones before it passed.

**Expect some to fail.** Every failure there answers a question the project
cannot currently answer from its own records.

Two things to know before you start:

- **`systemctl status` will lie.** The runner loops for ever, so the service
  reports `active (running)` whatever is happening, and the restart policy can
  never fire. Read the journal, and read it **by identifier**:

  ```sh
  journalctl -t encore-kiosk -b --no-pager
  ```

  **`-u encore-kiosk.service` does not work here, and fails quietly** — it
  returns systemd's own start and stop lines and nothing the capability wrote,
  so it reads like a capability that logs nothing. `docs/troubleshooting.md`
  explains why under *Before anything else*.

- **Debug over SSH, not through the terminal's screen.** When the kiosk wedges,
  the screen is the one thing you cannot use.

If something fails, `docs/troubleshooting.md` lists every failure seen so far
with the check that identifies it. **Nearly all of them were silent** — no
error, no log line, no dialog — so the order of the checks matters more than
usual. When there is no message at all, suspect waiting rather than crashing.

## Never do these

- **Never edit files on a terminal somebody is using.** Test on a virtual
  machine you can snapshot and revert. A converted machine in somebody's room is
  production, and the person using it cannot repair it.
- **Never commit a `*.remmina` profile or a `remmina.pref`.** A profile carries
  an encrypted password; the preferences file carries the key that decrypts it.
  Either alone is a secret. Together they are the password in plain text.
  `.gitignore` covers both, and templates are named `*.template` so the rules
  cannot match them.
- **Never hard-code an encryption key in anything shipped.** It is generated per
  deployment, on the terminal.
- **Never write a second, prose copy of a script.** It will drift, silently, and
  somebody will follow the stale one. The script is the document — comment it
  there instead.
- **Never change the machine terminals connect to as part of this product.**
  `D-002` puts it out of scope. Recommendations for it go in
  `docs/other-machine.md`, as recommendations.

## Commits

**Explain why, not what.** The diff already says what changed. The message
should say what was wrong, what was decided, and what it costs — so that
somebody reading it in a year understands a choice they would otherwise undo.

**When you correct the record, say what was believed before and why it was
wrong.** A commit that silently fixes a false statement destroys the evidence
that the project ever held it.

**State the status of the work in the first line of any report.** A commit hash
leads only when something shippable landed. A hash at the top of a message reads
as "shipped" whatever the words around it say.
