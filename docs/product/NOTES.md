# NOTES — append-only working log

Never rewrite past entries. One fact per entry. Restructure when this passes
150 lines or 25 entries, or when asked.

Folded entries are removed once they are true somewhere in `problem.md`,
`solution.md`, `decisions.md`, `users.md` or `glossary.md`. What is left here
is only what is not settled: open questions, and mechanism belonging to the
architect.

Last fold: 2026-09-13. Every entry written before that date has been folded and
removed; nothing was folded into `decisions.md` unless it was a made decision.

---

# Open questions — not decisions, not requirements

One outstanding: Q-P2. Q-P7, the name collision, was closed by D-022 — what the product installs carries an `encore` prefix. The other five raised by the architect's cold-start read
of the prototype were answered by the author on 2026-09-13 and closed as
decisions — the text consoles stay open (D-017), the public words are settled
(D-018), the clipboard is out (D-019), a broken configuration stops while an
unreachable machine keeps trying (D-020), and D-016 was confirmed as the
author's own. What a terminal owes an administrator when it is stuck is not a
question any more either: it is work to be specified, and it sits in
`BACKLOG.md`. Every earlier question has been answered by the author and
closed as a decision: the machine being connected to is out of scope (D-002),
who may deactivate and what deactivation restores (D-006, D-007), whether each
person gets their own session (D-008, superseded by D-011), whether the
terminal stores a credential (D-011), whether the microphone is in (D-014),
and where the product's responsibility stops (D-015).

## 2026-09-13 — Q-P2: what should R-14 promise a reader about the stored credential?
- **Kind:** question
- **Fact:** R-14 promises the connection credential "is not readable by anyone who picks the machine up". The architect reports no mechanism available to an unattended terminal delivers that: the stored form is obfuscation that is recoverable off the shelf, a keyring needs a human to unlock it at boot, and whole-disk encryption pushes the cost onto the adopter and sits badly with R-2.
- **Why:** R-14 is marked `intended`, so nothing in the record is false today — but an intended requirement nothing can deliver is a false promise with a delay on it. The likely honest destination is to promise less and say plainly what it does not protect against, which changes what a stranger is told and is therefore the author's call.
- **Narrowed 2026-09-13:** the author asks what Linux offers here, and notes that the remote desktop client already stores its password in a non-plain form — that may be enough. The architect owes a plain answer to "what can actually be promised on an unattended machine", and the author then decides what R-14 says. Until then R-14 stays `intended` and carries its warning note.
- **Source:** the architect, 2026-09-13 (their question Q-2 and item D-A5); narrowed by the author, 2026-09-13
- **Touches:** solution.md R-14, decisions.md D-011 and D-013

---

# Handoffs — the architect owns these

None outstanding. Both 2026-09-13 handoffs — the prototype's mechanism and the
connection profile sitting at the repository root — were taken up by the
architect on the same day and are recorded in `docs/architecture/`.

---

## 2026-09-13 — All three coverage questions closed by one boundary
- **Kind:** decision
- **Fact:** D-015 settles them together: the product's job ends when the connection is established. R-7 was withdrawn rather than justified, because signing in happens inside the connection; concurrency is the host's business for the same reason; and D-013's narrowing note stands as the resolution of D-011's stale cost line, with no heading change.
- **Why:** The author's analogy: a tunnel is not responsible for what travels through it. Two of the three questions were the same question wearing different clothes.
- **Source:** the author, 2026-09-13
- **Touches:** decisions.md D-015, solution.md R-7 (withdrawn), problem.md

## 2026-09-13 — The author rejected a proposed widening of problem.md
- **Kind:** decision
- **Fact:** A paragraph was drafted arguing that people need their own accounts because shared logins mean shared home folders, files and bookmarks. The author rejected it: all of that lives inside the connection and is out of scope.
- **Why:** Worth recording because it was the wrong instinct — the coverage check had flagged R-7 as untraceable, and the fix was to withdraw the requirement, not to grow the problem to fit it.
- **Source:** the author, 2026-09-13
- **Touches:** problem.md, solution.md R-7

## 2026-09-13 — Q-P6: is D-016 the author's decision, or the architect's inference?
- **Kind:** question
- **Fact:** D-016 — the product is sized for two or three terminals in one household, is not a fleet tool and does not scale — was written into `decisions.md` sourced to the author, who has not stated it. The Source line has been corrected to `assumed`.
- **Why:** The reasoning is sound and the record does lean on it everywhere, but a decision log is only worth reading if its Source lines are true. `alternatives.md` and ADR-0005 both rest on this one, so it carries more weight than most.
- **Source:** consistency audit, 2026-09-13
- **Touches:** decisions.md D-016, alternatives.md, solution.md

## 2026-09-13 — R-6 was specified properly rather than argued about
- **Kind:** decision
- **Fact:** The author specified the missing behaviour directly: no local application ever, a plain error message instead, and the terminal refuses to continue until the configuration is repaired. This became R-17 and D-020, and separates a broken configuration from an unreachable machine.
- **Why:** Worth recording that the gap was closed by deciding what should happen, not by weakening the requirement to match what the prototype does.
- **Source:** the author, 2026-09-13
- **Touches:** solution.md R-6, R-17, decisions.md D-020, BACKLOG.md

## 2026-09-13 — The two backlog lists were merged into one
- **Kind:** decision
- **Fact:** `BACKLOG.md` no longer separates "decided, not built" from "built and wrong". One ordered list.
- **Why:** The author: everything competes for the same evenings, so everything has to be ranked against everything else. Two lists let an item hide by being at the top of the shorter one.
- **Source:** the author, 2026-09-13
- **Touches:** BACKLOG.md


# Handoffs — the architect owns these

## 2026-09-13 — HANDOFF: the exact installed names
- **Kind:** handoff
- **Fact:** D-022 requires everything the product installs to carry an `encore` prefix, and the author has chosen the name: `encore-kiosk`. One name, not a choice between several.
- **Why:** Naming a unit for the kiosk is consistent with D-018, since the kiosk is the capability — only a machine may never be called one. The existing names built around the remote desktop client are wrong twice over: they carry no product prefix, and they name the product after a component the architect may replace.
- **Source:** the author, 2026-09-13
- **Touches:** docs/architecture/interfaces.md, BACKLOG.md item 7

## 2026-09-13 — The architect's three open contradictions, checked against the record
- **Kind:** decision
- **Fact:** Of the three, one was already closed and the architect's copy was stale (the console escape, closed by D-017); one is answered by the record's own machinery (R-17 is `intended`, so a message is what the product is meant to do and a blank screen is a delivery state, which belongs in `BACKLOG.md` and not in a product doc); and one was not addressed at all — the circular recovery fix — which is now `BACKLOG.md` item 3, ordered ahead of the fix it validates.
- **Why:** Worth recording that only the third needed anything from the product record, and what it needed was an ordering change rather than a decision.
- **Source:** the architect via the author, 2026-09-13
- **Touches:** BACKLOG.md, solution.md R-17, decisions.md D-017

## 2026-09-14 — First observations: three facts, one of them a confirmed defect
- **Kind:** question
- **Profiles:** person at the terminal, terminal administrator
- **Fact:** Running the compositor by hand on a test machine showed three things. The compositor renders and the remote desktop client starts, so the graphics path works. The client's own interface — a connection editor and a file chooser — appears when no profile is found, even with the client's kiosk flag set; this was previously read in code and is now observed. And the client asked for a keyring to be unlocked, which no unattended terminal can answer.
- **Why:** These are the first facts in the record that anyone has watched rather than read. The second confirms the breach of R-6 that R-17 exists to close. The third bears directly on Q-P2: a credential store that needs a human at boot cannot serve a machine that must reconnect on its own, which means the honest answer for R-14 is to promise less.
- **Source:** the author, observed on a virtual machine, 2026-09-14
- **Touches:** solution.md R-6, R-14, R-17, BACKLOG.md items 8, 9, 10

## 2026-09-14 — Root cause found: the kiosk's session is never the active one
- **Kind:** question
- **Profiles:** terminal administrator
- **Fact:** The capability opens its session on a console that is not the one in the foreground, so the session is never activated, and the compositor waits to be granted the screen. Observed directly: the session reports itself inactive. This is why the prototype has never been seen working, and it explains the silence, the black screen, the frozen console switching and the hanging stop as one behaviour rather than four faults.
- **Why:** The first root cause this project has found, and it was found by watching rather than reading. It also confirms the author's earlier doubt about the chosen console being a convention with nothing keeping it true.
- **Source:** the author, observed on a virtual machine, 2026-09-14
- **Touches:** solution.md R-6, R-10, BACKLOG.md item 2

## 2026-09-14 — A terminal in this state cannot be recovered from its own screen
- **Kind:** question
- **Profiles:** terminal administrator
- **Fact:** While the compositor holds a console it was never granted, switching consoles freezes and stopping the capability hangs. Remote access still worked; the screen did not. Observed on a virtual machine.
- **Why:** R-10 promises a text console stays reachable on an active terminal, and D-006 accepted the risk of lock-out on the understanding that it does. Both were written from a reading of the code. This is the first evidence against them, and it is one machine, so it is recorded as a question rather than a correction.
- **Source:** the author, observed on a virtual machine, 2026-09-14
- **Touches:** solution.md R-10, decisions.md D-006, D-017

## 2026-09-14 — First time the kiosk has been seen on a screen
- **Kind:** question
- **Profiles:** terminal administrator
- **Fact:** With the capability's console in the foreground, the compositor starts and the remote desktop client is displayed. The remote session itself does not begin. Observed on a virtual machine.
- **Why:** Until this moment nothing in the record had been watched working; every `real` requirement rested on a reading of the code. The screen half of the product is now observed. The connection half is not, and is suspected to be a fault in the connection settings rather than in the product.
- **Source:** the author, observed on a virtual machine, 2026-09-14
- **Touches:** solution.md R-6, BACKLOG.md item 2

## 2026-09-14 — Observed: a dialog the person at the terminal cannot reach
- **Kind:** question
- **Profiles:** person at the terminal, terminal administrator
- **Fact:** The remote desktop client raised a credential prompt behind its own main window. The compositor shows one window and offers no way to raise, move or switch between them, so the prompt could not be reached at all. Observed on a virtual machine, 2026-09-14.
- **Why:** This is the cost of the single-window choice arriving in a new form. R-6 is satisfied — nothing local is usable — but a terminal can now be stuck on a window nobody can answer, which no requirement covers. It is not only credential prompts: certificate warnings and disconnect notices would behave the same way.
- **Source:** the author, observed on a virtual machine, 2026-09-14
- **Touches:** solution.md R-6, R-17, BACKLOG.md item 11

## 2026-09-14 — The keyring is why the connection does not sign in by itself
- **Kind:** question
- **Profiles:** terminal administrator
- **Fact:** The remote desktop client prompts for credentials rather than using the stored one, which points at the password being held in a keyring rather than in the connection profile. A keyring needs a human to unlock it at login, and a terminal has none.
- **Why:** This is Q-P2 arriving as a practical blocker rather than a theoretical one. It confirms that the only credential storage available to an unattended terminal is the reversible file-based kind, and therefore what R-14 can honestly promise.
- **Source:** the author, observed on a virtual machine, 2026-09-14
- **Touches:** solution.md R-14, NOTES.md Q-P2, BACKLOG.md item 8

## 2026-09-14 — A remote session has been reached on a terminal
- **Kind:** question
- **Profiles:** person at the terminal, terminal administrator
- **Fact:** The capability started, the connection was made and the remote session appeared. Observed on a virtual machine, 2026-09-14. Reaching this needed three things the record did not describe: the capability's console must be the one in the foreground, the credential must be written on the terminal itself rather than copied to it, and the client's keyring plugin must not be reachable.
- **Why:** The product's core claim — put this on an old machine and it shows you a session — has now been watched once. Every `real` requirement in the record was written from a reading of the code before this.
- **Source:** the author, observed on a virtual machine, 2026-09-14
- **Touches:** solution.md, BACKLOG.md item 2

## 2026-09-14 — The client's own window sits above the session and cannot be dismissed safely
- **Kind:** question
- **Profiles:** person at the terminal
- **Fact:** With a session running, the client's main window stays on top. Closing it leaves the session window unreachable, because the compositor offers no way to raise or switch windows. Observed 2026-09-14.
- **Why:** A second instance of the unreachable-window finding, and this one is on the ordinary path rather than an error path. R-6 says the terminal shows the remote session and nothing else; today it shows the client's own interface on top of it, which is also a way for a person at the terminal to reach connection settings.
- **Source:** the author, observed on a virtual machine, 2026-09-14
- **Touches:** solution.md R-6, BACKLOG.md item 11

## 2026-09-14 — A sandboxing protection had to be dropped for the product to work at all
- **Kind:** question
- **Profiles:** terminal administrator, prospective adopter
- **Fact:** The setting that hides other users' home directories from the capability also hides the directory the graphical session needs, so the capability cannot start with it on. It was turned off to reach a working session, and the terminal therefore reaches more of its own filesystem than the record describes. Confirmed by turning it back on and watching the failure, 2026-09-14.
- **Why:** R-16 says the capability reaches only what it needs, and an adopter deciding whether to convert a machine is deciding what it may touch unattended. That promise is now weaker in fact than in writing. The protection was removed to get past a blocker, not because anyone decided the reach was acceptable — so this is a finding, not a decision.
- **Source:** the author, observed on a virtual machine, 2026-09-14
- **Touches:** solution.md R-16, decisions.md D-012, BACKLOG.md item 7

## 2026-09-14 — OPEN QUESTION: must the encryption key travel, or can it be born on the terminal?
- **Kind:** question
- **Profiles:** terminal administrator, prospective adopter
- **Fact:** A terminal cannot read its stored credential without a key file present. It is not established whether that key must be copied from the machine where the connection was built, or whether a key can be created on the terminal and the credential set there afterwards.
- **Why:** This decides whether a secret travels between machines during setup, and therefore how much D-025 actually buys. If the key must travel, every terminal shares one and the honest promise in R-14 shrinks again.
- **Source:** the author, observed on a virtual machine, 2026-09-14
- **Touches:** solution.md R-14, decisions.md D-025, BACKLOG.md item 5

## 2026-09-14 — OPEN QUESTION: how long may a terminal show nothing after a drop?
- **Kind:** question
- **Profiles:** person at the terminal
- **Fact:** No number has ever been stated for how long a person at a terminal may sit in front of a blank screen after a connection drops before it counts as broken. The recovery design makes that delay visible rather than hidden, so the number now has consequences.
- **Why:** `users.md` names a black screen as a reason the person at the terminal gives up. A delay that is fine for an adult debugging is not fine for a child who concludes the computer is broken and walks away.
- **Source:** found by the architect, 2026-09-14
- **Touches:** users.md, solution.md R-8

## 2026-09-21 — Answered: the machine being connected to is not always on
- **Kind:** decision
- **Profiles:** person at the terminal, owner of the machine being connected to
- **Fact:** The author's answer is no — the target may be down, and the figure to design against is 99% availability. Closed as D-026 and folded out of the open questions. The architect's Q-6, which found the premise attributed to a decision about audio, is answered by this.
- **Why:** It settles whether an outage is an incident or an ordinary event, and the answer is ordinary. That makes patience, rather than alerting, the correct behaviour for a terminal that cannot connect — and it sharpens the remaining question, because a terminal now has to sit through outages that may last hours with nothing useful on the screen.
- **Source:** the author, 2026-09-21
- **Touches:** decisions.md D-026, D-020, solution.md R-18, docs/architecture/NOTES.md Q-6

## 2026-09-21 — The "waiting" message is feasible, and it delivers R-17 almost for free
- **Kind:** question
- **Profiles:** person at the terminal, terminal administrator
- **Fact:** The author proposed that the terminal check whether the target is reachable, show a message while it is not, and move on to the remote session when it is. The architect reports this is feasible and cheap — roughly twenty lines of shell, no new package and no new window — provided the message is not drawn as a window at all. The same mechanism delivers R-17's "plain message, then stop" with no additional component.
- **Why:** The record has twice deferred work on the grounds that a message "requires adding a component". The architect reports that premise was wrong — it assumed the message had to be drawn inside the session. This removes the main cost argument against both R-17 and telling a waiting person what is happening, and it is the reason the earlier recommendation to defer the waiting screen no longer holds.
- **Source:** the architect, asked by the product manager, 2026-09-21. An opinion from a colleague, not a decision.
- **Touches:** solution.md R-17, R-18, R-6, BACKLOG.md items 11, 12, 13; docs/architecture/debt.md D-A1

## 2026-09-21 — OPEN QUESTION: does a waiting terminal explain itself, and with a countdown or not?
- **Kind:** question
- **Profiles:** person at the terminal
- **Fact:** If a terminal shows a message while it cannot reach its target, that message is a second thing the product puts on screen that is not the remote session, after R-17's. Two things are unsettled: whether explaining the wait is a promise the product makes at all, and whether the message counts down to the next attempt or simply states that the terminal is waiting.
- **Why:** R-6 says the terminal shows the remote session and nothing else; R-17 carved out one exception for a broken configuration, and this widens the carve-out to "whenever we are not yet connected". That is defensible and should be explicit rather than implied. On the countdown: the architect recommends cutting it from a first version and says whether a timer helps or frightens a child is a product judgement, not theirs. Under D-026 an outage can run for hours, so a timer that expires and restarts indefinitely may read as a broken machine rather than a patient one.
- **Source:** the author's proposal and the architect's read, 2026-09-21
- **Touches:** solution.md R-6, R-17, R-18

## 2026-09-21 — OPEN QUESTION: the R-6 / D-017 console trade is one character in a unit file
- **Kind:** question
- **Profiles:** person at the terminal, terminal administrator
- **Fact:** The architect reports that the compositor is currently started with a flag that explicitly permits console switching, and that removing it closes the person at the terminal's route out of the session from inside it. The record has treated this as an expensive open conflict; it is not.
- **Why:** Half the conflict already dissolved when R-10 was narrowed on 2026-09-21 to reaching the terminal from another machine — console switching is no longer something R-10 promises anybody. What remains is only D-017's reason for keeping consoles open: a terminal whose network has died would otherwise be unreachable for good. Both reasons still hold, so this is a genuine conflict and the author must pick; it is recorded here rather than decided.
- **Source:** the architect, 2026-09-21; D-017, R-6, R-10
- **Touches:** solution.md R-6, decisions.md D-017, docs/architecture/00-index.md

## 2026-09-21 — Corrected: downtime is not exposure, overlap is
- **Kind:** decision
- **Profiles:** person at the terminal
- **Fact:** D-026's costs line was first drafted as though one per cent downtime meant a terminal is useless one per cent of the time a person wants it. The author corrected it: nobody sits at a terminal all day, and outages are expected to arrive in occasional blocks rather than spread thinly, so the overlap between an outage and somebody wanting to use a terminal is small and rare. The costs line was rewritten the same day; the decision itself did not change.
- **Why:** Worth recording because the wrong framing was about to justify building something. A black screen during an outage looked like a frequent, user-facing failure and therefore an argument for a "waiting, not broken" screen; under the correct framing it is rarely met by anyone, which makes that component deferrable rather than urgent. The cost that survives the correction is the other one — a broken terminal is indistinguishable from an ordinary outage, and that one does not shrink, because a fault is permanent and therefore always overlaps with use.
- **Source:** the author, 2026-09-21
- **Touches:** decisions.md D-026, solution.md R-18, BACKLOG.md item 13

## 2026-09-21 — R-10 was two promises in one sentence, and the confusion had already spread
- **Kind:** solution
- **Profiles:** terminal administrator
- **Fact:** R-10 promises that an administrator can reach an *active terminal from another machine*. It never promised anything about a person standing at the terminal getting to a text login prompt on it — that is D-017's subject. The requirement was reworded to say so, and its state stays `real` with the 2026-09-14 network observation as evidence.
- **Why:** The old wording said "a text console **and** remote access still work", which welded the two together. That reading had already reached the 2026-09-14 entry below, which recorded the frozen console as "the first evidence against" R-10 and D-006 — it was not. The same welding is what the architect's Q-1 rests on, so the entry is worth keeping as a record of how far a single ambiguous sentence travelled.
- **Source:** the author, 2026-09-21
- **Touches:** solution.md R-10, decisions.md D-006 and D-017, docs/architecture/NOTES.md Q-1

## 2026-09-21 — R-8 split: surviving a restart and surviving a drop are different promises
- **Kind:** solution
- **Profiles:** person at the terminal, terminal administrator
- **Fact:** R-8 now covers only this: once deployed and active, a terminal survives a restart and reactivates by itself, so the person sitting at it can reach the machine at the other end. The dropped-connection half became R-18. Both are `intended`; the old combined R-8 was marked `real` on a code read.
- **Why:** The author's point: a terminal that has been switched on must stay switched on across restarts, and that is a property of being active, not of how it was activated. The two halves have different mechanisms behind them and very different confidence — bundling them let the unestablished half borrow the sound half's credibility under one `real` marker.
- **Source:** the author, 2026-09-21
- **Touches:** solution.md R-8, R-18, R-17, decisions.md D-005, D-020, BACKLOG.md items 10, 12, 13

## 2026-09-21 — HANDOFF: an activation must outlast a restart
- **Kind:** handoff
- **Profiles:** terminal administrator
- **Fact:** R-8 requires that an active terminal comes back by itself after a restart. How an activation is made to last is the architect's to decide; the product record states only that a way of switching the capability on which lasts only until the next restart does not satisfy R-8.
- **Why:** Raised in conversation as a product question and it is not one — it was a statement about the startup system wearing a requirement's clothes. Recorded here so the constraint reaches the architect without mechanism entering `solution.md`.
- **Source:** the author, 2026-09-21
- **Touches:** docs/architecture/, solution.md R-8

## 2026-09-14 — Reliability and recovery parked for a dedicated pass
- **Kind:** decision
- **Fact:** The author has parked error handling, retry and recovery as a subject to be investigated properly later, on the view that relying on the startup system alone has serious limitations. The parts of the recovery work that do not depend on unobserved behaviour stay available to do now.
- **Why:** The positive path comes first, and designing failure handling against a connection nobody has watched drop produces guesses. Recorded so the position is not mistaken later for a rejection of the architect's answer.
- **Source:** the author, 2026-09-14
- **Touches:** BACKLOG.md items 12 and 13

## 2026-09-23 — No package: installing is a clone and a script
- **Kind:** decision
- **Profiles:** terminal administrator, prospective adopter
- **Fact:** The product will not be distributed as a distribution package. A machine is converted by taking a copy of the repository onto it and running an install script, and given back by running the matching uninstall script. Closed as D-027.
- **Why:** A package solves problems this project does not have — dependency resolution, fleet upgrades, archive distribution — while R-4 only promises that a machine becomes a terminal in minutes, the same way every time. A script delivers that now instead of after packaging machinery exists, and an adopter can read every step before running it.
- **Source:** the author, 2026-09-23
- **Touches:** decisions.md D-027, solution.md R-4 and R-11, BACKLOG.md item 4, README.md

## 2026-09-23 — R-11 was relying on somebody's memory
- **Kind:** solution
- **Profiles:** terminal administrator
- **Fact:** R-11 promises the old machine back, but nothing recorded what the machine booted into before conversion, so restoring it depended on whoever ran the uninstall remembering. The installer now records the previous default target at install time and the uninstaller reads it, asking only if there is no usable record.
- **Why:** An uninstall can happen years and several administrators after an install. A promise that depends on human memory across that gap is not a promise the product keeps — it is one the administrator keeps on the product's behalf, which is a different and weaker thing.
- **Source:** the author, 2026-09-23
- **Touches:** solution.md R-11, docs/tests.md Test 4

## 2026-09-23 — A shipped artifact must be a true copy of something observed working
- **Kind:** decision
- **Profiles:** terminal administrator, prospective adopter
- **Fact:** The connection profile template was a hand-tidied, commented version of the profile observed working on 2026-09-14, and had silently lost a setting that suppresses the certificate dialog — 18 keys against the working profile's 103. It is now generated from that profile verbatim, with only the host, account, password and label blanked, and its header forbids hand-curation.
- **Why:** The template's own header claimed the settings were the ones observed working. They were not, and the claim is what made the gap invisible — everyone downstream trusted it. A curated artifact that asserts provenance it does not have is worse than an untidy one that is a true copy.
- **Source:** the author, 2026-09-23, after the template cost a debugging session
- **Touches:** encore-kiosk.remmina.template, solution.md R-6, BACKLOG.md items 5 and 7

## 2026-09-23 — The template no longer asserts decisions the product has not delivered
- **Kind:** solution
- **Profiles:** person at the terminal, terminal administrator
- **Fact:** Regenerating the template from the working profile means it now carries an open clipboard and no audio, which contradicts D-019, D-009 and D-014. The old template asserted those decisions in a file nobody had tested against a working connection.
- **Why:** Policy and baseline had been bundled together. Separating them makes both decisions visibly undelivered rather than invisibly claimed, and each must now be proved on a connection that works before it goes back in.
- **Source:** the author, 2026-09-23
- **Touches:** decisions.md D-009, D-014, D-019; BACKLOG.md items 5 and 7

## 2026-09-23 — A failed connection leaves no trace anywhere but the screen
- **Kind:** question
- **Profiles:** terminal administrator, person at the terminal
- **Fact:** Watched on a VM: the connection failed, a clickable dialog appeared on the terminal's screen, and the journal recorded only that the service started and a session opened. Every channel available to an administrator said the terminal was healthy.
- **Why:** This is the argued-about failure mode observed rather than reasoned about, and it lands on two promises at once — R-6, because a person at the terminal was shown something they could act on, and R-18, because an administrator has no way to tell a broken terminal from an ordinary outage. It also means the product's only diagnostic surface is the one screen the troubleshooting guide tells you not to use.
- **Source:** observed on a virtual machine, 2026-09-23
- **Touches:** solution.md R-6 and R-18, BACKLOG.md items 12 and 13, docs/architecture/debt.md D-A2

## 2026-09-23 — R-10 has a precondition nothing stated and nothing checked
- **Kind:** solution
- **Profiles:** terminal administrator, prospective adopter
- **Fact:** R-10 promises an active terminal can be administered from another machine. That is easiest if remote access already exists before the machine is converted — after conversion the screen shows the remote session and nothing else, so there is no desktop from which to set it up. The qualifying conditions now list it, and the installer prints a reminder when no SSH server is running. It does not block the install.
- **Why:** The requirement reads as a property the product delivers, and it is partly a property of the machine that the product depends on. The author's position, 2026-09-23: a text console is a genuine way in, so a machine without SSH is inconvenient rather than unreachable, and blocking an install over something recoverable only teaches people to click through warnings. What the product owes is that the way back in is never removed — not that it is set up for you.
- **Source:** the author, 2026-09-23
- **Touches:** solution.md R-10 and R-1, decisions.md D-017, README.md, encore-install.sh

## 2026-09-23 — The solution document was still selling a package
- **Kind:** solution
- **Profiles:** prospective adopter, terminal administrator
- **Fact:** `solution.md` opened with "Install a package on an old Linux machine" and described the product as "installable — a package, a short configuration step…", a day after D-027 ruled out ever building one. Both sentences now say install rather than package, which is what R-4 promises and what the scripts deliver.
- **Why:** Found in a record-wide consistency audit. It is the worst kind of staleness: the first sentence a stranger reads, contradicting the newest decision in the log. A decision is not landed until the documents that repeat it have been corrected.
- **Source:** the author, 2026-09-23
- **Touches:** solution.md, decisions.md D-027, R-4

## 2026-09-23 — OPEN QUESTION: publishing makes the README the document a stranger meets
- **Kind:** question
- **Profiles:** prospective adopter
- **Fact:** The README was written as a lab procedure for the author, and ADR-0006 deliberately held back the reader-facing explanation as separate later work. With the prototype warning removed and the project published on GitHub, the README is now the first and only thing a stranger meets — which is R-13's job.
- **Why:** Either R-13 is now partly satisfied by the README and the separate document is a smaller job than it was, or the README has quietly taken on an audience it was not written for. The two documents have different readers: one is for somebody debugging a machine they already own, the other is for somebody deciding whether to spend an evening at all. The current README serves the first well and assumes a reader comfortable being told that a failed connection reports itself healthy.
- **Source:** found by the product manager during the 2026-09-23 audit
- **Touches:** solution.md R-13, decisions.md D-010, docs/architecture/adr/ADR-0006, BACKLOG.md item 15

## 2026-09-23 — Nothing in the record covers the credential while it is being set
- **Kind:** question
- **Profiles:** terminal administrator, owner of the machine being connected to
- **Fact:** R-14 promises the connection credential is kept encrypted and not readable by anyone who picks the machine up. That covers the credential at rest. Setting it is a different moment: the password reaches a command line, so it is briefly visible in the process list and can be written to the machine's logs. The installer detects this afterwards and tells the operator to rotate the password, which is honest, but no requirement admits the exposure exists.
- **Why:** An adopter reading R-14 would reasonably conclude the product protects the credential throughout. It protects it afterwards. The gap is small in duration and permanent in the logs, and it is the kind of thing that should be stated rather than discovered — particularly since the same credential opens a door on the machine the whole household uses.
- **Source:** found by the architect, 2026-09-23, recorded as D-A12
- **Touches:** solution.md R-14, decisions.md D-011 and D-025, BACKLOG.md item 8

## 2026-09-23 — Two handoffs taken by the architect, and two deferrals expired
- **Kind:** handoff
- **Profiles:** terminal administrator
- **Fact:** The architect has taken both outstanding handoffs — the exact installed names, raised 2026-09-13, and that an activation must outlast a restart, raised 2026-09-21. Separately, two architecture items were deferred "into the configuration design" and that design has now shipped without them, so what the stored credential can honestly promise and what pinning the connection means are both waiting on the author rather than on any work.
- **Why:** Recorded so the deferrals do not keep reading as blocked. A reason to wait that has quietly expired is worse than no reason, because it keeps a decision off the table without anyone deciding to keep it there.
- **Source:** the architect's report, 2026-09-23
- **Touches:** solution.md R-8, R-14, R-16; BACKLOG.md items 7 and 8

## 2026-09-23 — R-16 holds at install time and is never checked again
- **Kind:** solution
- **Profiles:** terminal administrator, owner of the machine being connected to
- **Fact:** R-16 promises a terminal reaches the machine it was configured to connect to. The installer writes one connection profile under a pinned name and confirms there is exactly one; from then on the terminal takes whichever profile it finds first, in no defined order. A second profile arriving later — a backup, a half-finished edit, a restore — silently changes which machine the terminal connects to, and nothing reports it.
- **Why:** A promise checked once at setup and never again is a weaker promise than the wording suggests, and this one decides where a household's credential gets sent. It is the same shape as the reversibility gap found earlier today: the product was relying on nothing else ever changing, rather than on anything it does itself.
- **Source:** found by the architect, 2026-09-23, recorded as D-A13
- **Touches:** solution.md R-16 and R-5, BACKLOG.md item 3

## 2026-09-23 — Pinning the target's identity is possible, and it shrinks what R-14 must promise
- **Kind:** solution
- **Profiles:** terminal administrator, owner of the machine being connected to, person at the terminal
- **Fact:** The architect established that a terminal can be made to accept exactly one certificate and refuse everything else, with nobody asked and nothing drawn on the screen. R-16's promise — the machine it was configured to connect to, not something answering to its name — is therefore deliverable rather than aspirational.
- **Why:** It changes what R-14 can honestly say. Today the stored credential's weakness is reachable from anywhere on the household network: anything that answers to the configured name is handed the credential. With the target's identity pinned, the remaining exposure is somebody physically holding the terminal. That is a much smaller sentence than R-14 currently implies, and it is the half of the credential problem that can actually be delivered.
- **Source:** the architect, investigating at the author's request, 2026-09-23
- **Touches:** solution.md R-14 and R-16, decisions.md D-011 and D-012, BACKLOG.md item 7

## 2026-09-23 — Pinning puts a file outside the product's own footprint, and R-11 has to cover it
- **Kind:** solution
- **Profiles:** terminal administrator, prospective adopter
- **Fact:** The identity pin lives in a machine-wide location, not in the product's own home directory, and it changes the behaviour of every remote desktop client on that machine rather than only ours. Removing the capability has to remove it too.
- **Why:** R-11 promises the old machine back with no repair by hand. A file left behind that silently changes how unrelated software on that machine trusts connections is exactly the kind of residue that breaks the promise while looking like nothing. This is the third thing the installer now establishes once and the uninstaller has to know about, after the previous startup mode and the connection profile.
- **Source:** the architect, 2026-09-23
- **Touches:** solution.md R-11, decisions.md D-007, docs/tests.md Test 4

## 2026-09-23 — OPEN QUESTION: does the install make the administrator check the fingerprint by hand?
- **Kind:** question
- **Profiles:** terminal administrator, prospective adopter
- **Fact:** Capturing whatever answers at install time protects against every later impostor, and against nothing that is already in position during the install. Turning that into genuine identity needs the administrator to read the fingerprint off the target machine itself and compare it — an out-of-band step the product cannot do for them. Whether the install demands that comparison, offers it, or stays silent is unsettled.
- **Why:** It is the difference between "this terminal trusts the machine you told it to trust" and "this terminal trusts whatever was there when you set it up". Demanding it costs a manual step against R-4's promise of minutes; skipping it means R-16's guarantee quietly rests on the install moment being clean. With two or three terminals in one household the step is cheap, which is an argument for asking — but it is the author's call and nobody else's.
- **Source:** raised by the architect, 2026-09-23
- **Touches:** solution.md R-16 and R-4, decisions.md D-002, BACKLOG.md item 7

## 2026-09-23 — Pinning adds a package to every terminal, permanently
- **Kind:** solution
- **Profiles:** terminal administrator, prospective adopter
- **Fact:** Capturing the target's certificate at setup needs a command-line tool the product does not currently install — about 0.8 MB, one extra name in the install step. It is needed at setup to capture, and again by the runner if the terminal is to tell a refused certificate apart from an unreachable machine. It therefore stays on the terminal for good.
- **Why:** R-11 promises the old machine back, so the uninstaller has to remove it. More honestly, it widens what converting a machine costs: the record's claim has been that the product adds a capability rather than reshaping the system, and every package added is a little less true. Cheap at this size, and worth noticing rather than absorbing — the alternative was writing our own protocol code, which is worse.
- **Source:** the architect, 2026-09-23
- **Touches:** solution.md R-11 and R-4, decisions.md D-007 and D-024, BACKLOG.md item 7

## 2026-09-23 — OPEN QUESTION: what do we owe an adopter whose target offers no certificate?
- **Kind:** question
- **Profiles:** prospective adopter, terminal administrator
- **Fact:** Capturing and pinning the target's identity has only ever been tried against one machine — the author's, which is Windows-like and requires network-level authentication. Two other common ways of serving remote desktop on Linux have never been spoken to, and one of them can be configured to offer no certificate at all. There is nothing to capture and nothing to pin on such a machine.
- **Why:** R-16 promises the terminal reaches the machine it was configured to connect to and not something answering to its name. On a target with no certificate that promise cannot be kept by any means, so the product must either refuse to set such a terminal up, set it up while saying plainly that the guarantee does not apply, or narrow what qualifies. D-002 forbids us from fixing the target, so this is about what we say, not what we do.
- **Why it matters now:** the record currently states the qualifying conditions in terms of the terminal only. This is the first requirement that depends on a property of the machine we declared out of scope.
- **Source:** raised by the architect, 2026-09-23
- **Touches:** solution.md R-16, R-1 and R-13, decisions.md D-002, BACKLOG.md item 7

## 2026-09-23 — Pinning is L, not M — the pin is the cheap part
- **Kind:** solution
- **Profiles:** terminal administrator
- **Fact:** Capturing the target's certificate is small. Making the captured value actually govern the connection is not: the accept-anything setting has to leave the profile in the same change, a second permissive setting in a file we generate but have never read has to be asserted, a machine-wide file has to be written and later removed, the administrator's confirmation step has to exist, and the runner needs a new way to stop permanently.
- **Why:** Recorded because the first estimate was wrong in the direction that causes trouble. A pin shipped without the rest is a file that changes nothing while the record claims the terminal is pinned — the same shape as the template that had silently lost a setting and was trusted for nine days.
- **Source:** the architect, 2026-09-23
- **Touches:** BACKLOG.md item 7, solution.md R-16

## 2026-09-23 — A permanently broken target now hides behind an ordinary outage
- **Kind:** solution
- **Profiles:** person at the terminal, terminal administrator
- **Fact:** When the target answers and proves it speaks the right protocol but the encrypted handshake then fails, the terminal retries rather than stopping. If that condition is permanent — a broken or misconfigured target — the terminal waits for ever, showing nothing, exactly as it would during an ordinary outage.
- **Why:** It follows from the rule D-020 sets: stop only when the evidence is about the target and retrying cannot change it. Here the far end has already proved it is the right kind of machine, so the plausible causes are transient or ours, and stopping on our own strictness is the direction D-020 names as worse. The cost is real and was recorded rather than traded silently — it is the same blind spot D-026 already accepts, reached by a different road.
- **Source:** the architect, applying D-020, 2026-09-23
- **Touches:** decisions.md D-020 and D-026, solution.md R-18, BACKLOG.md item 13

## 2026-09-23 — The product now depends on a language runtime, and nothing says which version
- **Kind:** solution
- **Profiles:** prospective adopter, terminal administrator
- **Fact:** Capturing the target's identity is done by a script the project owns, written in a language that ships with the supported distributions. Review found a real behavioural difference between versions of that runtime, which the script's error handling depends on. Nothing in the record states a minimum, and nothing on a terminal checks one.
- **Why:** R-1 lets a reader decide in ten seconds whether their machine qualifies, and the qualifying conditions no longer describe everything the product actually needs. This is the second unstated floor found today — the first was the startup system's — and both are the accepted cost of D-024 arriving in a specific form: an adopter on an older release gets behaviour the record does not describe, with nothing to tell them.
- **Why it matters for a promise rather than a build:** the failure it produces is the one this design is most careful about. On an older runtime the capture step can fail in a way the terminal cannot classify, and anything unclassified is retried for ever — the harm D-028 exists to prevent.
- **Source:** found in review, 2026-09-23
- **Touches:** solution.md R-1 and R-4, decisions.md D-003 and D-024, BACKLOG.md item 4

## 2026-09-23 — OPEN QUESTION: do we exclude an adopter loudly or silently?
- **Kind:** question
- **Profiles:** prospective adopter, terminal administrator
- **Fact:** Two version floors are now known — one in the startup system, one in the language runtime — and neither is checked. An adopter below either gets a terminal that behaves in ways the record does not describe, with nothing to tell them. Both would close with a few lines in the setup step.
- **Why:** R-1 exists so a reader can rule themselves out in ten seconds, and it currently describes less than the product needs. The choice is between refusing to convert a machine that cannot work — losing an adopter at the door, loudly — and converting it anyway, which loses them later and more confusingly. D-024 already accepted excluding older releases; what was never decided is whether the exclusion should be visible.
- **Why it matters beyond tidiness:** the failures these floors produce are the silent kind this project keeps being bitten by. Below the runtime floor the capture step fails in a way the terminal cannot classify, and anything unclassified is retried for ever.
- **Source:** raised by the architect, 2026-09-23
- **Touches:** solution.md R-1 and R-4, decisions.md D-003 and D-024, BACKLOG.md item 4

## 2026-09-23 — Correction: the runtime floor was recorded from a defect, and the defect is fixed
- **Kind:** solution
- **Profiles:** prospective adopter, terminal administrator
- **Fact:** Two entries earlier today say the product depends on a language runtime version and that two floors are known. The runtime half was wrong by the time it was written down: the behaviour it rested on was a bug in our own script, which was fixed the same afternoon, and the capture step now runs identically on three versions. Whether any floor remains is being established from the code rather than from the old reasoning. The startup system's floor is unaffected and still real.
- **Why:** Worth recording rather than quietly amending, because it is a good example of a constraint invented by a defect. A floor derived from something we got wrong would have excluded adopters for no reason, and R-1 exists to let a reader rule themselves out accurately — being wrong in the strict direction costs real people.
- **Source:** the product manager, on re-checking a claim before repeating it to the author, 2026-09-23
- **Touches:** solution.md R-1, decisions.md D-024, BACKLOG.md item 4, and the two entries above it

## 2026-09-23 — The startup-system floor excludes the Raspberry Pi generation this product was aimed at
- **Kind:** solution
- **Profiles:** prospective adopter, terminal administrator
- **Fact:** The floor the recovery design depends on arrived in July 2023. Debian 12 and every Raspberry Pi OS built on it ship a version below it; only the 2025 generation, built on Debian 13, clears it. A machine below the floor does not fail — it silently retries at a flat interval instead of backing off, which nothing reports.
- **Why:** D-024 accepted this cost in the abstract — "a distribution whose repositories carry an older release is excluded even though it satisfies D-003, which cuts into exactly the old, long-lived machines this product exists to reuse". This is that sentence arriving with a name on it. The installed base below the floor is not an edge case; it is most of the Raspberry Pis in cupboards, which is the machine the problem statement is written about.
- **Why it sharpens the open question:** whether to exclude loudly or silently is no longer abstract. Silently means an adopter converts a Pi, watches it appear to work, and inherits recovery behaviour the record does not describe.
- **Source:** the author asked when the floor was released; established 2026-09-23 from the release announcement and the distributions' own package listings
- **Touches:** solution.md R-1 and R-2, decisions.md D-003 and D-024, BACKLOG.md items 4 and 14

## 2026-09-23 — The two floors are not one question, and only one of them matters
- **Kind:** solution
- **Profiles:** prospective adopter
- **Fact:** The runtime floor resolved to a four-year-old version that every distribution in scope already exceeds, and a machine below it fails visibly and immediately rather than misbehaving. The startup-system floor is the opposite: recent enough to exclude most Raspberry Pis in use, and it fails silently, with the terminal appearing to work while recovering differently from what the record describes.
- **Why:** They were logged together earlier today as "two version floors" and that framing is wrong. Only one of them turns adopters away, and it is the one nobody would notice. Any decision about checking versions at setup should be made about that one alone; bundling them would spend effort on the harmless case and dilute the argument about the harmful one.
- **Source:** established by the architect from the code, 2026-09-23
- **Touches:** solution.md R-1, decisions.md D-024, BACKLOG.md items 4 and 14

## 2026-09-27 — the project has a licence
- **Kind:** decision
- **Fact:** The project is released under the Apache License 2.0 (D-032).
- **Why:** The author's choice. The repository was published with no licence at all, which means nobody who cloned it had permission to use it — the opposite of what the project is for.
- **Source:** the author, 2026-09-27
- **Touches:** `decisions.md` (D-032, written), `README.md` (a License section, written), `LICENSE` and `NOTICE` at the root

## 2026-09-27 — per-file copyright headers are not applied
- **Kind:** question
- **Fact:** Apache 2.0's appendix recommends a boilerplate header in each source file. The project has none, and this was not decided either way.
- **Why:** The licence does not require it; a root `LICENSE` is enough to grant the rights. Headers matter when single files travel away from the repository on their own, which for a five-file project is plausible rather than certain.
- **Source:** assumed — nobody has ruled on it
- **Touches:** `decisions.md` if it is settled; otherwise `BACKLOG.md` as a small task

## 2026-09-27 — the audio mechanism is pulse-or-alsa, not pipewire-or-alsa
- **Kind:** solution
- **Profiles:** person at the terminal
- **Fact:** The client library carries no PipeWire backend. It has `pulse`, `alsa` and `oss` only, so PipeWire is reached through its PulseAudio-protocol socket rather than directly.
- **Why:** It changes only the mechanism, not the promise. R-12 still says sound both ways with nobody picking a device; the author's steer of "prefer PipeWire, else ALSA" is correct as policy and unavailable as written.
- **Source:** the architect, 2026-09-27, from the library installed on the author's own machine — **not** from either target platform, and no client was installed there to check against.
- **Touches:** solution.md R-12

## 2026-09-27 — whether the terminal has any audio server at all is unknown
- **Kind:** question
- **Profiles:** person at the terminal
- **Fact:** The identity the terminal runs as is a system account with no login shell. Audio on the target platforms is normally served per-user, started by that user's own service manager. Nothing in this project has ever observed such a manager running for that account, and setup does not arrange one.
- **Why:** This decides the size of the audio work. If a server is already there, audio is three keys in one file. If it is not, audio is the first requirement that forces the long-standing question of a background service doing a logged-in user's job — a new concept, a changed contract, and a re-test of the one thing that has been observed working.
- **Source:** the architect, 2026-09-27
- **Touches:** BACKLOG.md item 5, solution.md R-12

## 2026-09-27 — the D-009 failure is a single-word mistake in a generated file
- **Kind:** decision
- **Fact:** The profile key that sends sound to the terminal and the key that sends it to the machine being connected to differ by one word. The second is exactly the outcome D-009 exists to prevent — a child's noise coming out of an adult's room.
- **Why:** The record treated that failure as an edge case. It is one token in a file this project generates, and the file is already under a rule that says it should be copied from a working machine rather than written by hand.
- **Source:** the architect, 2026-09-27, from the client's public source rather than an installed build
- **Touches:** decisions.md D-009, BACKLOG.md item 5

## 2026-09-27 — "usable without a microphone" has a plausible failure behind it
- **Kind:** question
- **Profiles:** person at the terminal, administrator
- **Fact:** D-014 promises a terminal with no microphone is still fully usable. If the input channel fails on such a machine and takes the connection down with it, the terminal's indefinite retry presents that as an unreachable machine and it waits for ever.
- **Why:** The promise is currently a claim with an untested failure under it, and the failure is the shape this project keeps being bitten by — everything reports healthy while nothing works. What the terminal should do instead is a product call, not a technical one.
- **Source:** the architect, 2026-09-27
- **Touches:** solution.md R-12 and R-18, decisions.md D-014, BACKLOG.md item 5

## 2026-09-27 — audio is missing a permission, not a service
- **Kind:** solution
- **Profiles:** person at the terminal
- **Fact:** The sound server is very likely already running for the terminal's identity, started on demand. What is missing is permission to open the sound hardware: the terminal's session is registered without a seat, and the operating system only grants device access to a session that holds one.
- **Why:** It moves this from "build a missing thing" to "grant an access we already grant elsewhere". The installer already hands the same identity access to the screen and the input devices for exactly this reason; sound was left out of that list. Not yet observed — one command on a converted machine confirms or refutes it.
- **Source:** the architect, 2026-09-27
- **Touches:** BACKLOG.md item 5, solution.md R-12

## 2026-09-27 — "nobody picks a device from a list" has two readings
- **Kind:** question
- **Profiles:** person at the terminal, administrator
- **Fact:** R-12 can mean no choice is put to the person sitting at the terminal, or it can mean no audio choice is made per machine at all, by anyone. The fallback path satisfies the first and breaks the second, because it would have the installer pick an output on each machine.
- **Why:** `problem.md` argues the stricter reading: audio set up machine by machine is audio that ends up missing on one of them. If that is what R-12 means, a fallback that configures per machine is not a fallback, it is a quiet breach. **This may not need answering** — it only matters if the ordinary path turns out to be unavailable on some machine.
- **Source:** raised by the architect, 2026-09-27; the reading of `problem.md` is the architect's inference, not a ruling
- **Touches:** solution.md R-12, problem.md

## 2026-09-27 — the protocol was chosen for audio, and audio ships switched off
- **Kind:** problem
- **Fact:** ADR-0004 gives two-way audio as a reason for choosing this remote-desktop protocol. The connection profile the installer writes sets sound off and leaves the microphone empty.
- **Why:** A reason given for a decision is not delivered by the thing the decision produced. Worth recording as a contradiction in its own right rather than only as an unbuilt requirement.
- **Source:** the architect, 2026-09-27
- **Touches:** solution.md R-12, BACKLOG.md item 5
