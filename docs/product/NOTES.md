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
