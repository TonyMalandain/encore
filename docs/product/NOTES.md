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
