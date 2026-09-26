# Architecture knowledge base — index

**Last restructure:** 2026-09-13 (the working log was folded into the formal
documents on this date; the record itself was opened the same day by reading
the prototype)

**Last correction sweep: 2026-09-23.** The whole record was checked against the
code and rewritten where it disagreed. Three things had gone stale: the names
(D-022 and D-023 renamed everything on 2026-09-13, the code shipped on
2026-09-14, this record had not followed), the packaging assumption (D-027 on
2026-09-23 says there will never be a package), and the health claims (the
product has been watched working twice since this record said nothing had ever
been observed). Every `file:line` was re-checked against the file, not renamed.

This is the engineering half of the record. `docs/product/` says what the
product is for and what was decided; this says what shape it has and why.
Mechanism — paths, units, config keys, protocols, libraries — lives only here.

| Doc | What's in it |
|---|---|
| `NOTES.md` | Append-only working log. Open questions Q-1, Q-2, Q-4, Q-5, Q-7, Q-8 and Q-11, plus findings from 2026-09-23 of which two are for the product manager. Q-3 and Q-6 are closed and kept as a record. **Past the restructure trigger at 538 lines** — not folded on 2026-09-23 because a ticket citing this record was in flight. Two `for-architecture` findings from the probe's implementation were taken on 2026-09-23 and are marked `(taken)` in place. |
| `overview.md` | The system on one page, with a diagram: the installer, four installed parts, one boundary, and what has actually been watched. |
| `boundaries.md` | The six parts, what each owns, what it must not know — including the configuration boundary, which now exists — and the one job nothing owns. |
| `interfaces.md` | Seven contracts, all of them files or paths: which are public, which are fragile, and which changed status when the package went away. |
| `data.md` | The complete inventory, split by deactivate versus uninstall; the honest account of the one secret; and why the key no longer has to travel. |
| `constraints.md` | The environment, the absolutes, the fleet size of two or three, and the conflict the design must not hide. Two version floors live in C-1, systemd ≥ 254 and CPython ≥ 3.10, and nothing on a machine enforces either. **The Python floor was recorded as 3.14 on 2026-09-23 and corrected to 3.10 the same day** — it had been read off a defect that was fixed concurrently; C-1 keeps the full trail, which is the record's best example of a constraint that was measured correctly and still wrong. |
| `stack.md` | Every part adopted except the probe, none pinned — and why nothing will ever pin them now. CPython was added on 2026-09-23; the probe's language had been missing from this table entirely. |
| `debt.md` | Eighteen items, worst first, with what each is waiting on. Three of the original eleven are repaid or void; seven new ones were added on 2026-09-23 (D-A12 to D-A18), two of them not yet built. |
| `adr/` | **Nine** decisions: four reconstructed from code, five the author's or the architect's own. |

## Decisions on file

| ADR | Decision | Kind | Status |
|---|---|---|---|
| ADR-0001 | Remmina is the remote desktop client | reversible | accepted; deciding reason **confirmed by the author** 2026-09-13 |
| ADR-0002 | `cage` is the single-window Wayland compositor | reversible | accepted (reconstructed); addendum 2026-09-23 |
| ADR-0003 | An isolatable systemd target is the on/off switch | **one-way door** | accepted (reconstructed); **both "revisit when" conditions closed** — addendum 2026-09-23 |
| ADR-0004 | RDP is the protocol | reversible | accepted (reconstructed) |
| ADR-0005 | Assemble from systemd parts, not a thin-client platform | reversible | accepted (author's own reasoning) |
| ADR-0006 | The README is a lab procedure, not the reader-facing explanation | reversible | accepted — **architect's call, not yet ratified by the author** |
| ADR-0007 | systemd owns recovery; the runner is a launcher, not a supervisor | reversible | accepted 2026-09-14; addendum 2026-09-23 — its missing premise is now D-026 |
| ADR-0008 | We speak the RDP preamble ourselves, to capture and to classify | one-way door | accepted 2026-09-23 — follows D-028, D-029, D-030; the exchange is verified on the wire, nothing is built; two addenda, 2026-09-23: option D (bind to the installed `libfreerdp` from `ctypes`) examined and rejected, and the runner contract completed — **the Connection Confirm bytes in the Decision block were corrected the same day**; a third correction the same day removed the cipher string `DEFAULT@SECLEVEL=0`, which was measured to narrow the envelope it was chosen to widen — the permissive envelope is now recorded as a property, not a literal; a **third addendum**, same day, completes the runner contract against the probe's ten actual statuses — `2 USAGE` and `9 NO_CERTIFICATE` stop, `5 TIMEOUT` and a crash (exit 1) retry, and nothing falls through to the default any more |
| ADR-0009 | The installer tells the runner where to connect; the profile never does | reversible | accepted 2026-09-23 — unblocks the runner's pre-flight; **decided, not built**; narrows boundary 4 and adds two keys to I-7 |

**Nine, not seven.** ADR-0009 was added on 2026-09-23. The count in this
heading has been wrong before — check it against the table below, which is the
authority.

**None is superseded.** ADRs are never renumbered or deleted; a replaced one is
marked superseded in place. Where a decision has been confirmed, narrowed or
overtaken by events without being reversed, an addendum is appended to it with
the date — three carry one as of 2026-09-23.

**ADR-0002 to ADR-0004 are reconstructed, not recorded.** The choices are real
and visible in the code; the reasons were never written down, so the Context
and Options sections are the architect's reconstruction and are marked as such
at the top of each file. The author should confirm or correct the deciding
reason in each.

**ADR-0001 was reconstructed and has since been confirmed.** On 2026-09-13 the
author gave the reasoning: wide apt availability, and — the load-bearing one,
which the reconstruction had missed — that Remmina's own GUI builds reusable
configuration files. Note that the install path no longer relies on copying a
file built elsewhere: the profile comes from a template and the password is set
on the terminal (`data.md`). The author is not committed to Remmina if
something better appears; the live trigger is whether the profile format can
carry certificate pinning and audio defaults.

**ADR-0005 is the author's own**, given on 2026-09-13. It is the standing
answer to "why not LTSP?".

**ADR-0006 is the architect's call and has not been ratified.** The author
asked for install instructions; writing them as a lab procedure, and holding
R-13's reader-facing explanation back as a separate later document, was a
choice made on their behalf. It is on file so that it can be overruled easily
rather than absorbed silently.

## How to read this record

1. **`overview.md` first.** It is one page and it is the whole system.
2. **`debt.md` second, if you are about to change anything.** Fourteen items,
   and the top two are the difference between a terminal and an unmanaged
   computer in a child's bedroom.
3. `NOTES.md` for the questions still waiting on a human.

## Health of this record

**Rewritten 2026-09-23. This section used to say "nothing here has been
observed at runtime" and that has been false since 2026-09-14.**

- **The product has been watched working, twice.** On 2026-09-14, on a VM, a
  remote session appeared for the first time — reaching it needed three things
  the record did not describe: the capability's console must be the foreground
  one, the credential must be written on the terminal rather than copied to it,
  and the client's keyring plugin must be out of reach. On 2026-09-23, on a
  clean Ubuntu 26.04 VM built by following the written procedure, a session
  appeared again. Remmina 1.4.43, cage 0.2.1, FreeRDP 3.31, x86_64.
- **The `getent passwd kiosk` / `ls /var/lib/kiosk` evidence is void twice
  over.** It was a check for a user that has since been renamed (D-023), run on
  the development machine, which was never where a terminal was going to be.
- **What is confirmed rather than argued, as of 2026-09-23:** the encryption
  key is created on the terminal during the password step, so nothing secret
  travels between machines and every terminal has its own key. That closes an
  open product question from 2026-09-14 and narrows `debt.md` item D-A5.
- **What is still a code read**, and says so where it appears: everything about
  a *dropped* connection (Test 2, never run), reversibility (Test 4, never
  run), audio (Test 5, never run), and surviving a reboot (Test 7, never run).
  `docs/tests.md` is the authority on which is which.
- **File-line references were re-checked against the repository on
  2026-09-23**, against `encore-kiosk.sh`, `encore-kiosk.service`,
  `encore-kiosk.target`, `encore-kiosk.remmina.template`, `encore-install.sh`,
  `encore-uninstall.sh`, `encore-push.sh` and `.gitignore`. The previous check
  on 2026-09-13 pointed at four files that have since been renamed and
  rewritten, so the lines had moved even where the claims held.
- **Citations that pointed at a personal file have been moved.**
  `group_rdp_server_server.remmina` at the repository root is an untracked
  personal connection profile; it will never exist on an adopter's machine, and
  `constraints.md` C-5, `interfaces.md` I-6, ADR-0004 and three `debt.md` items
  were all measuring shipped behaviour against it. They now cite
  `encore-kiosk.remmina.template`, which is what we ship.
- **The claim about a stale reference outside this record was itself stale.**
  This section said `BACKLOG.md`'s R-13 row "still says there is no readme". It
  does not, and has not for some time — `BACKLOG.md` item 15 now says `README.md`
  exists but does not satisfy R-13 because it is a lab procedure aimed at the
  author (ADR-0006). Corrected 2026-09-23.

## Open contradictions

Three were listed here. **One is closed, one is narrower than it was, and one
survives in a reduced form.** Reviewed 2026-09-23.

**1. The virtual consoles — still open, but half of it dissolved.**
*(both sides recorded 2026-09-13; narrowed 2026-09-21 and 2026-09-23)*
As written, this pitted R-6 (nothing but the remote session) against R-10 (the
administrator can reach the machine). **R-10 is no longer a side.** It was
reworded on 2026-09-21 to promise that an administrator can reach an active
terminal *from another machine*, and it never promised a person standing at the
terminal a text login prompt. What remains is R-6 against **D-017's own
reason**: a terminal whose network has died would otherwise be unreachable for
good. Both still hold, so the author must pick.

Two corrections of fact that went with it. The keys are `Ctrl+Alt+F1` through
`F6` and **which one gives a login prompt varies by machine**; three documents
each named a single different key and all three were wrong. And the mechanism
is one character: `cage -s` (`encore-kiosk.service:17`) is what permits console
switching at all, so this is a cheap conflict, not an expensive one.

**2. What replaces the no-profile fallback — the cost argument was wrong.**
*(both sides recorded 2026-09-13; corrected 2026-09-21, folded here 2026-09-23)*
This said `debt.md` item D-A1's repayment ("show a static 'not configured'
screen") collides head-on with ADR-0002, because showing anything beside the
session needs a component `cage` exists to prevent. **The premise was wrong,
and it was the architect's own.** It assumed the message had to be drawn inside
the session. It does not — the runner can write to the console before the
compositor starts, which is roughly twenty lines of shell, no new package and
no new window. ADR-0002 forbids drawing *alongside a running session* and says
nothing about the screen when there is no session, which is exactly this case.
So the collision is not real and this is no longer a contradiction. What is
left is a product question — whether the terminal explains itself while it is
waiting, and with a countdown or not — and it is open with the author in
`docs/product/NOTES.md`, not here.

**3. Whether removing the shell loop produces a failure signal — survives,
reduced, and now with evidence.**
*(recorded 2026-09-13; narrowed by ADR-0007 on 2026-09-14; observed 2026-09-23)*
The surviving half: supervision of the connection is only as real as the
client's willingness to exit. Upstream says it does not exit on a dropped
connection by default, and Test 2 has still never been run.

**What 2026-09-23 added is worse than the contradiction.** A failed connection
produced a clickable certificate dialog on the terminal's screen while the
journal recorded only "started" and "session opened". ADR-0007 consequence 4
had named the journal as the channel that carries this signal when the unit
state cannot. On that occasion it did not. The cause was never identified — a
later clean reinstall connected successfully, most likely a difference in stale
files from an earlier session — and it is recorded as **unexplained**, because
the symptom is precisely the one `debt.md` item D-A2 exists to name.

## Related records, not part of this one

- `docs/product/` — the problem, the requirements, the product decision log.
  Not editable from here.
- `docs/product/glossary.md` — shared. Code-side names may be added there.
- `README.md` — the install-and-test procedure for the prototype. Ours, and
  governed by ADR-0006.
- `docs/tests.md` — what has been run on a converted machine and what has not.
  It is the authority on which claims here are observations.
- `docs/troubleshooting.md` — every failure seen so far, with the check that
  identifies it. Several facts in this record are sourced to it.
- `BACKLOG.md` — delivery order. Tracks *unbuilt* work and decides what is done
  next; `debt.md` tracks *built* things that are wrong and decides nothing.
- `docs/product-ignore/` — excluded by the author. Not read.

## Where things live

Resolved by the architect agent on 2026-09-23. Correct anything wrong here —
the agents read this before they read anything else. **This is the architecture
record's copy**; it is here because there is no `CLAUDE.md` and no top-level
`docs/` index, and the root `README.md` is not the architect's to edit. If a
`CLAUDE.md` is ever created, this table belongs there instead.

| What it holds | Where it is |
|---|---|
| the problem, in prose | `docs/product/problem.md` |
| the solution and its numbered requirements | `docs/product/solution.md` |
| user profiles | `docs/product/users.md` |
| closed product decisions and their reasons | `docs/product/decisions.md` |
| why not an existing project | `docs/product/alternatives.md` |
| shared vocabulary, product and code | `docs/product/glossary.md` |
| the product working log, and handoffs to the architect | `docs/product/NOTES.md` |
| delivery order / the backlog | `BACKLOG.md` (repository root) |
| architecture: overview, boundaries, interfaces, data, constraints, stack | `docs/architecture/` |
| known compromises already taken | `docs/architecture/debt.md` |
| architecture decision records | `docs/architecture/adr/ADR-NNNN-<slug>.md` |
| the architecture working log | `docs/architecture/NOTES.md` |
| findings waiting for product | `docs/architecture/NOTES.md`, entries of kind `for-product` |
| findings waiting for architecture | `docs/product/NOTES.md`, under "Handoffs" |
| the design for a feature, before it is built | `docs/plans/<slug>.md` — created 2026-09-23 by the senior engineer for the certificate probe; there was nothing holding this role before |
| what has been run on a machine, and what has not | `docs/tests.md` |
| every failure seen, with its check | `docs/troubleshooting.md` |
| how to install and remove | `README.md`, and the scripts at the repository root |
| the shipped artifacts | repository root: `encore-kiosk.{target,service,sh}`, `encore-kiosk.remmina.template`, `encore-{push,install,uninstall}.sh` |
| **not** shipped, and secret-bearing | repository root: `*.remmina`, `remmina.pref` — untracked, see `.gitignore` |
