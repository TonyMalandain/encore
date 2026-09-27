# Decisions

Closed decisions only. Superseded entries stay, marked in the heading.
Four fields, always.

---

### D-001 — This is a non-commercial project — 2026-09-13
**Decision:** The project is a personal side project, published for others to reuse, with no buyer, no price and no go-to-market.
**Why:** It was started to solve the author's own household problem, and publishing it costs little more than solving it privately.
**Costs accepted:** No revenue justifies the effort, so the only budget is the author's evenings; nobody is obliged to maintain it for anyone.
**Source:** the author, 2026-09-13

### D-002 — The machine being connected to is out of scope — 2026-09-13
**Decision:** The product covers only the old machine being converted; it neither configures nor makes claims about the machine hosting the sessions.
**Why:** The two ends are different environments — the author's own host runs a distribution the product does not support — and owning both would double the surface.
**Costs accepted:** An adopter must already have a machine that accepts remote sessions, and getting that working is on them; the product cannot promise an end-to-end result.
**Source:** the author, 2026-09-13

### D-003 — Supported terminals are apt-family Linux with Wayland and systemd — 2026-09-13
**Decision:** A terminal must run a Linux with the apt package manager, Wayland as the display server, and systemd; no hardware is assumed.
**Why:** One named combination is something a stranger can check against their own machine in seconds, and something the author can actually keep working.
**Costs accepted:** Machines outside that combination are excluded even where they would probably work, which rules out part of anyone's cupboard.
**Source:** the author, 2026-09-13

### D-004 — The terminal is a kiosk with no local graphical use — 2026-09-13
**Decision:** While the capability is active, the screen shows the remote session and nothing else; local graphical use of the machine is impossible.
**Why:** The people using terminals are children, and anything clickable that is not the remote session is a way out of the arrangement.
**Costs accepted:** The machine cannot be used locally for anything at all while active, so a household loses the option of dual use.
**Source:** the author, 2026-09-13

### D-005 — The terminal never falls back to a local desktop — 2026-09-13
**Decision:** After a reboot or a dropped connection, the terminal returns to the remote login screen; there is no state in which it becomes an ordinary computer.
**Why:** A half-converted machine is worse than an unconverted one, because the household believes it is under control.
**Costs accepted:** A terminal that cannot reach its target is useless rather than degraded, and offers the person sitting at it no local fallback whatsoever.
**Source:** the author, 2026-09-13

### D-006 — Only root can deactivate the capability — 2026-09-13
**Decision:** Turning the capability off is reserved to the machine's root administrator, reached over a text console or the network; ordinary users cannot do it.
**Why:** A child who can turn the kiosk off has been handed an unsupervised computer by another route.
**Costs accepted:** The administrator needs a second way into the machine, and a household with no such access can lock itself out of its own hardware.
**Source:** the author, 2026-09-13

### D-007 — Activation is reversible — 2026-09-13
**Decision:** Deactivating the capability returns the machine to the state it was in before, with no manual repair.
**Why:** Without a clean undo, converting a machine is a one-way bet and the sensible choice is not to try at all.
**Costs accepted:** The product must restrain what it changes on the machine, which rules out any approach that reshapes the system to suit itself.
**Source:** the author, 2026-09-13

### D-008 — The terminal holds no identity and no credentials — 2026-09-13  [SUPERSEDED by D-011 on 2026-09-13]
**Decision:** The person at the terminal authenticates against the machine they are connecting to; anyone with valid credentials can use any terminal.
**Why:** Terminals are furniture. Tying one to a person means one machine per person, which is the cost the project exists to avoid.
**Costs accepted:** Nobody gets an automatic session, so every use starts with typing a password — including small children.
**Source:** the author, 2026-09-13

### D-009 — Sound belongs to the terminal — 2026-09-13
**Decision:** The audio devices of the machine a person is sitting at become the default output for their remote session, with no device chosen by hand.
**Why:** A terminal with no sound is half a computer, and audio arriving on the wrong machine puts a child's noise into an adult's room.
**Costs accepted:** Audio hardware on old machines varies widely, so this is a promise the project has to keep across machines it has never seen.
**Source:** the author, 2026-09-13

### D-010 — Written explanation is part of the product — 2026-09-13
**Decision:** The documentation that lets a stranger judge the project before installing it is treated as part of the product, not as something around it.
**Why:** A prospective adopter decides whether to spend an evening on this by reading; if they cannot, the project only ever works in one house.
**Costs accepted:** Every change carries a writing cost, and capability that cannot be explained plainly is worth less than capability that can.
**Source:** the author, 2026-09-13

### D-011 — The terminal holds a connection credential, never a person's — 2026-09-13
**Decision:** The terminal stores one credential, set during configuration and kept encrypted, whose only job is to establish the remote connection; the person then signs in to their own account at the remote login screen, and that second credential is never known to the product. Supersedes D-008, which failed to separate the two.
**Why:** Reaching the remote login screen is the product's whole job — who signs in there, and whether they succeed, belongs to the machine being connected to.
**Costs accepted:** A secret now lives on every terminal and must be protected and rotated; anyone who extracts it can reach the login screen of the machine being connected to, and every person still types a second password to get anywhere.
**Source:** the author, 2026-09-13

### D-012 — The capability runs with the least privilege that lets it work — 2026-09-13
**Decision:** The running capability holds no administrative privilege and reaches nothing beyond the machine it is configured to connect to, the screen, the keyboard, the mouse and the audio devices.
**Why:** A terminal is an unattended machine in a child's room; what it can reach if it is compromised or misused is the honest measure of what it costs to install.
**Costs accepted:** Anything the product might later want to do on the terminal — managing the machine, touching storage, reaching other hosts — is ruled out by default and would have to be argued for individually.
**Source:** the author, 2026-09-13

### D-013 — Rotating the connection credential is not the product's job — 2026-09-13
**Decision:** The product sets the connection credential during configuration and never rotates, expires or reminds anyone about it; changing it means configuring the terminal again. This narrows the cost accepted in D-011, which assumed rotation would be handled.
**Why:** The credential only reaches a login screen, and a household running a handful of terminals is not going to operate a rotation routine it did not ask for.
**Costs accepted:** A credential that leaks stays valid until a human notices and reconfigures every terminal by hand; the product will not tell them, because it does not manage terminals at all.
**Source:** the author, 2026-09-13

### D-014 — Audio is two-way, and works without being set up — 2026-09-13
**Decision:** A terminal's microphone, where the machine has one, is available to the remote session as its default input, on the same terms as the speakers are its default output; both work on first use with nothing chosen by hand. This widens D-009, which addressed output only.
**Why:** A terminal with sound in only one direction cannot be used for a call, and a household that has to configure audio per machine will end up with machines where it was never done.
**Costs accepted:** Every terminal becomes a live microphone in whichever room it sits in, reachable by anyone signed in to a session on it; the household accepts that in exchange for calls working. Terminals with no microphone must still be fully usable, so the product cannot depend on one being there.
**Source:** the author, 2026-09-13

### D-015 — The job ends when the connection is established — 2026-09-13
**Decision:** The product is responsible for opening a connection to the configured machine and putting whatever that machine sends on the screen. Everything inside the connection — who signs in, whether they get their own account and files, how many people work at once, what the session contains — belongs to the machine at the other end. R-7 was withdrawn under this decision.
**Why:** The same reason a tunnel is not responsible for what travels through it: the product cannot promise behaviour it neither controls nor observes, and claiming it would make every adopter's remote machine our problem.
**Costs accepted:** The product can be working perfectly while the person at the terminal cannot do anything useful, and the record cannot promise a household the thing it actually wants — a working computer for each child — only the connection that makes one possible.
**Source:** the author, 2026-09-13

### D-016 — The product is built for two or three terminals in one household — 2026-09-13
**Decision:** The product is sized for a handful of terminals belonging to a single household. It is not a fleet tool, has no central place to configure or change terminals together, and does not claim to scale.
**Why:** This is the reason the product assembles parts an ordinary Linux machine already has rather than adopting a thin-client platform: at two or three machines, running the infrastructure such a platform needs costs more than the problem is worth. It was assumed everywhere in the record and stated nowhere, which is the kind of assumption that gets violated without anyone noticing.
**Costs accepted:** Every terminal is configured on its own, so the same change has to be made by hand as many times as there are terminals, and nothing tells anyone when one was missed. That is the single largest hole in the design, and it is the one thing the rejected platforms would have provided for free — the project is not avoiding that work, it is choosing to do a small local version of it.
**Source:** the author, in conversation with the architect, 2026-09-13

### D-017 — The lock is on the screen, not on the machine — 2026-09-13
**Decision:** The kiosk stops the person sitting at the terminal from running anything other than the remote session; it does not close the machine's text consoles, and reaching one is not treated as an escape. A terminal is expected to carry no ordinary user accounts, only an administrator whose password the household controls.
**Why:** The people the lock exists for are children in front of a screen. A text console asking for a password it will not be given is not a way past that, and closing it would leave a terminal with a dead network unreachable for good.
**Costs accepted:** Anyone who can sit at a terminal can reach a login prompt, so the whole arrangement rests on the administrator's password being strong and on no other account existing on the machine; a household that adds a user account to a terminal has quietly weakened it, and nothing will tell them.
**Source:** the author, 2026-09-13

### D-018 — A terminal is the machine; the kiosk is what we give it — 2026-09-13
**Decision:** "Terminal" names the old computer the product is installed on. "Kiosk" names the capability the product provides. A piece of hardware is never called a kiosk.
**Why:** These are two different things and a reader who meets one word doing both jobs has to carry a translation, which is what R-13 exists to prevent. The words become public the first time a stranger follows an instruction containing one.
**Costs accepted:** The code uses "kiosk" for the machine, the user, the group and the home directory, so agreeing this makes the existing names wrong and creates a rename that has to happen before packaging rather than after.
**Source:** the author, 2026-09-13

### D-019 — The clipboard is not shared with the remote session — 2026-09-13
**Decision:** A terminal does not share a clipboard with the session it displays. It is not one of the things the capability may reach.
**Why:** There is nothing local to copy from or paste into — that is what the kiosk means — so a shared clipboard is a two-way data channel bought for no benefit.
**Costs accepted:** Anyone who later wants to move text between a terminal and something local cannot, and the answer will be that there is no local anything, which is correct but unhelpful to the person asking.
**Source:** the author, 2026-09-13

### D-020 — A broken configuration stops; an unreachable machine keeps trying — 2026-09-13
**Decision:** These are different failures and the product treats them differently. A terminal that cannot reach the machine it was pointed at keeps trying, indefinitely and unattended. A terminal whose configuration is missing or invalid stops, says so on the screen, and does not try again until the configuration has been repaired.
**Why:** Retrying fixes the first and cannot fix the second, and a terminal that retries a broken configuration for ever hides the one fault a person could actually repair. Neither failure may ever be answered by handing the person at the terminal a local application.
**Costs accepted:** The product must be able to tell the two apart, and getting it wrong in either direction is worse than not trying — a terminal that stops on a fault it could have retried is a machine somebody has to walk over to.
**Source:** the author, 2026-09-13

### D-021 — The product is called Encore — 2026-09-13
**Decision:** The project's name is Encore: an old machine gets a second performance rather than a second life as landfill. The name says nothing about children, because the product does not.
**Why:** The household reason for building it is children, but the product itself converts an old computer for whoever is sitting at it — a name that says "for kids" would make a stranger converting machines for an elderly parent, a workshop or a study room rule themselves out, which is the opposite of what R-13 is for. The alternative considered, Kidiosk, was unclaimed but narrowed the audience and reads two ways aloud.
**Costs accepted:** The name says nothing about what the product does, so every place it appears needs a sentence beside it; and a well-known infrastructure platform already publishes an `encore` command, so the installed command and package cannot simply be `encore` without colliding on machines that have both.
**Source:** the author, 2026-09-13

### D-022 — Everything the product installs is called encore-kiosk — 2026-09-13
**Decision:** Everything the product installs on a machine is named `encore-kiosk` — the product's name, then the capability it provides. One name, chosen here so nobody downstream has to choose between several.
**Why:** The prefix is what lets a terminal administrator look at a list of things running on their machine and see which ones this product put there — the same reason D-007 promises a clean undo. It also settles the collision with an unrelated `encore` command without renaming the product, and it stops the installed names carrying the name of a component the architect may replace.
**Costs accepted:** The names become public at packaging and are awkward to change afterwards, so this has to be right the first time rather than adjusted once people are using it.
**Source:** the author, 2026-09-13

### D-023 — The identity the product runs as is called encore — 2026-09-13
**Decision:** The system user, group and home directory the capability runs as are called `encore`, not `kiosk`. This refines D-022: the units that provide the capability are `encore-kiosk`, and the identity that runs them is `encore`. Two names, each naming a different kind of thing.
**Why:** The user is the product's footprint on the machine rather than one capability of it — it is what a terminal administrator sees in the account list and what they remove to undo the install, so it should carry the product's name plainly. Calling it `kiosk` also breaks D-018 twice over: it is a bare word with no product prefix, and it uses "kiosk" for something that is not the capability.
**Costs accepted:** The record now holds two installed names rather than one, so anyone adding a new installed thing has to decide which kind it is; and every existing reference — the units, the home directory, the documented install and removal steps — is wrong until the rename happens.
**Source:** the author, 2026-09-13

### D-024 — The product tracks current versions of what it depends on — 2026-09-14
**Decision:** The product targets the current release of the software it installs, and carries no compatibility handling for older releases. Where a setting has been renamed between versions, only the current name is used.
**Why:** Supporting two spellings of every setting doubles what has to be tested on a project with one author and no way to test the old versions, and a household converting a machine can install a current release as easily as an old one.
**Costs accepted:** A distribution whose repositories carry an older release is excluded even though it satisfies D-003 — which cuts into exactly the old, long-lived machines this product exists to reuse. Nothing detects this: an adopter on an older release gets a terminal that fails in ways the record does not describe.
**Source:** the author, 2026-09-14

### D-025 — The encryption key is established per deployment and never shipped — 2026-09-14
**Decision:** The key that protects a terminal's stored connection credential is established when that terminal is set up, and is never included in anything the project distributes.
**Why:** A key shipped in a template is the same key on every installation, so it protects nothing while still reading as protection — which is worse than storing the credential in the open, because a reader would believe it was safe.
**Costs accepted:** Setting up a terminal now has a step that cannot be automated away by copying files, and an adopter who gets it wrong gets a terminal that fails to authenticate with no error that names the cause.
**Note, 2026-09-23:** established by experiment that the key is created on the terminal during configuration, so nothing secret has to travel between machines and every terminal holds its own key. This is the favourable reading of the decision and it costs the install nothing.
**Source:** the author, 2026-09-14

### D-026 — The machine being connected to goes down, and that is normal — 2026-09-21
**Decision:** The product assumes the machine being connected to is available about 99% of the time, not always. A terminal that cannot reach it is therefore experiencing an expected condition, not a fault, and must wait through it quietly — retrying indefinitely, showing the person at the terminal nothing they could act on, and raising no alarm.
**Why:** The premise had been leaned on everywhere and stated nowhere, and it was attributed to a decision that is actually about audio. It decides whether an outage is an incident or a Tuesday, and therefore how patiently a terminal must behave. Ninety-nine per cent is the author's own expectation of their household machine, not a measurement.
**Costs accepted:** A terminal will sometimes be a machine showing nothing useful while being entirely healthy, and the product has no way to tell the person sitting at it the difference between that and a broken terminal. How often anybody actually meets that state is much rarer than one per cent, because the exposure is not the downtime — it is the overlap between an outage and somebody wanting to use a terminal, and outages are expected to arrive in occasional blocks rather than spread thinly through the day. The cost that does not shrink is the other one: the product can never treat "cannot connect" as evidence of a fault, so a genuinely broken terminal is indistinguishable from an ordinary outage for as long as an outage could plausibly last.
**Source:** the author, 2026-09-21

### D-027 — Installing means cloning the repository and running a script, never a distribution package — 2026-09-23
**Decision:** The product is installed by taking a copy of the repository onto the machine being converted and running a script there. No distribution package is built or published, and none is planned. Undoing an install is the matching script, not the package manager.
**Why:** A package exists to solve problems this project does not have: declaring dependencies for a resolver, upgrading many machines that are not in front of you, and distributing through an archive nobody here maintains. What R-4 actually promises is that a machine becomes a terminal in minutes, the same way every time — a script delivers that, and it delivers it today rather than after the packaging machinery exists. It also keeps the install readable: an adopter can see every step before running it.
**Costs accepted:** Nothing checks prerequisites for us, so D-024's minimum versions have to be enforced by the script or not at all. There is no upgrade path — a converted machine is updated by taking a newer copy and installing again, and nothing guarantees that leaves a working terminal. Removal depends on our own uninstall script being correct, where a package manager would have kept the file list itself; this is what makes R-11 a promise the project has to keep by hand. And an adopter must be willing to run a script from a repository rather than install from an archive they already trust, which is a higher bar for a stranger than for the author.
**Source:** the author, 2026-09-23

### D-028 — A certificate mismatch stops the terminal, and says why — 2026-09-23
**Decision:** When the target's certificate does not match the one captured at setup, the terminal stops rather than retrying, and the reason is readable by an administrator reaching the machine remotely — distinct from any other failure, and distinct from "not configured". This is the `invalid configuration` branch of D-020, not the `cannot reach` branch.
**Why:** Retrying cannot fix a changed certificate, so a terminal that retries hides the one fault a person could repair in two minutes. Stopping silently would be as bad: the record already shows a terminal that failed while every channel reported it healthy, so "stop" is only useful if the reason survives to somewhere an administrator can read it.
**Costs accepted:** A legitimate certificate change — a rebuild, a reinstalled service — takes the terminal down until an adult re-captures it, and the terminal cannot tell that apart from an impostor. The author's position, 2026-09-23: an administrator who has just rotated a certificate can spend the extra minutes confirming the terminals still trust it. Detecting the mismatch precisely enough to report it is the expensive half, and anything the terminal cannot classify falls back to retrying for ever, which is the failure this decision exists to prevent.
**Source:** the author, 2026-09-23

### D-029 — The administrator confirms the target's fingerprint at setup — 2026-09-23
**Decision:** Setting up a terminal shows the fingerprint of the machine it is about to trust and asks the administrator to confirm it, the way an SSH client does on a first connection. The comparison against the target machine itself is the administrator's to make; the product presents the fingerprint and records the answer.
**Why:** Capturing whatever answers at setup protects against every later impostor and against nothing already in position at that moment. The confirmation step is what turns first-use trust into identity, and it is the only part of that the product can offer without touching the machine being connected to, which D-002 forbids. A household converting two or three terminals can afford the seconds.
**Costs accepted:** Converting a machine is no longer unattended, and an administrator who confirms without looking gets the weaker guarantee while believing they have the stronger one — the same failure mode as every SSH prompt anyone has ever accepted blind. R-4's "in minutes" now includes a step that cannot be automated away without giving up what it buys.
**Source:** the author, 2026-09-23

### D-030 — Capturing the target's identity is ours, not a borrowed client — 2026-09-23
**Decision:** The step that captures the target machine's certificate at setup is written by this project, using only what the terminal already has. No additional remote desktop client is installed to perform it.
**Why:** The alternative was installing a second, X11-based client on a machine the product declares to be Wayland-only, used exactly once per terminal and then left in place for ever. The author's reasoning, 2026-09-23: if this project evolves it will most likely drop the current client in favour of driving a library directly, so a dependency on that client's packaging is not future-proofing anything — it ties the setup step to a component already expected to be replaced.
**Costs accepted:** The project now owns a piece of protocol code and every bug in it, where the alternative was borrowed and maintained by somebody else. It must keep working across versions of what the target machine runs, and nothing warns us when it stops. Against that, it is small, it has no dependencies, and it survives replacing the remote desktop client — which the borrowed version would not have.
**Clarified 2026-09-23:** this rules out installing *any* additional remote desktop client for the purpose, not only an X11 one. A Wayland-based client package exists and slips past the original wording while falling squarely under the reason — it is still a second client, and it needs a running graphical session that setup does not have.
**Also considered and rejected, 2026-09-23:** driving the remote desktop library already present on the terminal, rather than installing anything or writing our own. It ships no executable and no headers, so calling it from a script would mean hand-writing a binding to a private interface, with every internal offset and constant copied into our own file from headers we do not ship and cannot check against. That is more machinery of our own than the protocol exchange it replaces, about something private and changeable, where the protocol exchange is fixed by published specification. Its failure mode is also worse: a wrong constant crashes rather than raising an error, and a crash is exactly the outcome the terminal cannot classify — which sends it back to retrying for ever, the harm D-028 exists to prevent.
**Source:** the author, 2026-09-23

### D-031 — Running setup again is how a terminal is changed — 2026-09-23
**Decision:** Capturing and confirming the target's identity happens inside the ordinary setup process, not as a separate step. Running setup again on a machine that is already a terminal is supported, and is the way an administrator updates what that terminal trusts when the target's certificate changes. It must leave a working terminal.
**Why:** A separate step is a step people skip, and the identity check is only worth having if every terminal gets it. Certificates change — a rebuild, a reinstalled service — and D-028 makes a mismatch stop the terminal, so there has to be a way back that an administrator can find without reading anything. The way they will reach for is the one they already know: run the install again.
**Costs accepted:** Setup must now be safe to run on a machine that already has a profile, a stored credential and a pin, which is a stronger promise than first-run-only. Anything it asks for again is a chance to enter it differently and quietly change what the terminal does. The record has no test for re-running setup and no observation of it, so this is a promise made before it has been watched.
**Source:** the author, 2026-09-23

### D-032 — The project is released under the Apache License 2.0 — 2026-09-27
**Decision:** Apache License 2.0, applied as a verbatim `LICENSE` file at the repository root with the copyright notice in `NOTICE`. Anyone may use, change and redistribute the work, including commercially, provided they keep the licence and notice, and state what they changed.
**Why:** The author's choice. The project exists to be reused by strangers on their own old hardware (D-001, D-010), and until now the repository carried no licence at all — which under copyright means nobody who cloned it had permission to use it, the opposite of the intent. Apache 2.0 delivers the permissive reuse the project wants while adding two things a bare permissive licence does not: an explicit patent grant, so an adopter is not relying on silence, and a requirement to state changes, so a modified terminal cannot be mistaken for this one.
**Costs accepted:** Permissive means someone may ship this commercially, closed, with no obligation to contribute anything back, and the author has no recourse. The change-statement and notice obligations make redistribution slightly heavier than the shortest permissive licences, which may deter the most casual copying. The licence is also irrevocable in practice: every version already published stays available under it, so this cannot be narrowed later, only widened.
**Source:** the author, 2026-09-27

### D-033 — No per-file copyright headers — 2026-09-27
**Decision:** Source files carry no copyright or licence header. The `LICENSE` file at the repository root, with the notice in `NOTICE`, is the whole of how the licence is applied.
**Why:** Apache 2.0 requires only that the licence be included with the work; per-file headers are a recommendation in its appendix, not an obligation, so the rights are fully granted without them. The author's instruction was to add them only if strictly necessary, and they are not.
**Costs accepted:** A single file copied out of the repository on its own — one script pasted into a forum answer, one unit file lifted onto a machine — carries no trace of its licence or its origin, and a reader of that copy has no way to know either. That is the case headers exist for, and this project has five files that are individually useful, so it is a plausible loss rather than a theoretical one.
**Source:** the author, 2026-09-27
