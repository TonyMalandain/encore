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

### D-034 — Audio may need a restart to come back after someone uses a text console — 2026-09-28
**Decision:** The terminal's sound follows the active session on the seat. If an administrator switches to a text console, the terminal may lose its sound and not regain it by itself; restarting the terminal is the supported way to get it back. The product does not track session activation on the sound path in order to avoid this.
**Why:** The author's call, on the grounds that console use on a terminal is rare — D-017 keeps consoles open for an administrator who has lost the network, not for the person sitting at it. The alternative is to keep the part of the sound server that watches login sessions, and that is what pulls in the session message bus, and with it the credential keyring, the file broker and the package-prompt client that D-012 and R-16 exclude. Paying for a rare recovery with a permanent widening of the machine is the wrong trade.
**Costs accepted:** A terminal that has had a console switch can be silent afterwards, and **nothing tells anyone why** — it looks identical to audio never having worked. That is one more entry in this project's longest-running problem, things that report healthy while not working. It also means an administrator diagnosing a terminal at its own console can destroy the evidence they came to collect, and will not be warned.
**Source:** the author, 2026-09-28

### D-035 — The supported Ubuntu is 26.04 or newer — 2026-09-28
**Decision:** The Ubuntu the product claims to support is 26.04 or newer. The earlier long-term release, previously named in the README, is no longer claimed. The other two platforms are unchanged.
**Why:** Two reasons, and the weaker one came first. The audio work needs a sound stack that the earlier release does not carry, so the feature could never work there. But the stronger reason stands on its own: **26.04 is the only Ubuntu this product has ever been run on**, and the earlier release was named from reasoning about version numbers rather than from anything anyone watched. The record's rule is to claim what has been observed.
**Costs accepted:** The release being dropped is a long-term one that many people are actually running, so this turns away real machines — and it turns them away **today**, for a feature that is not built yet, since everything except audio works there as far as anyone knows. Narrowing the claimed set also makes the product less useful for its own stated purpose, which is reusing old machines that people already have. Nobody has tested the dropped release either, so this is an untested exclusion replacing an untested inclusion.
**Source:** the author, 2026-09-28

### D-036 — The product supports two package managers, apt and dnf — 2026-10-04
**Decision:** A terminal may be converted on a Linux using either the apt family or the dnf family. Fedora joins Raspberry Pi OS, Ubuntu and Debian as a claimed platform. **The capabilities are identical on both** — nothing is offered on one family and withheld on the other, and no requirement is weakened for either. Only the step that installs software differs, and it differs by package manager rather than by distribution name. Everything else the product writes — the identity, the service, the profile, the undo — is already written in terms that both families carry, and stays one implementation.

This replaces the apt-only limit previously stated in `solution.md` under *What this is not*, and amends `R-1`.

**Why:** The limit it replaces was never about apt. The out-of-scope entry gave the reason plainly — supporting one combination is what makes the product assessable in one sitting — and it named its own condition for being revisited. The cost turns out to be much smaller than that entry assumed. **Only four lines of `encore-install.sh` mention apt at all**, and two of the seven package names differ: `remmina-plugin-rdp` is `remmina-plugins-rdp`, and `pipewire-pulse` is `pipewire-pulseaudio`. Everything else the product depends on is present on Fedora under the same name, at a version at or above the stated floor — `wireplumber` is 0.5.17 against a floor of 0.5, `/usr/sbin/nologin` is at the same path, and the `video`, `input` and `render` groups all exist. The product was built out of parts already present on any systemd-and-Wayland Linux, and that choice is now paying out: the breadth was already there, and only the installer was narrow.

The second reason is that the author's own main machine is Fedora, so a second family is testable here in a way a second apt distribution is not. The record's rule is to claim what has been observed, and this is the one direction where observation is actually available.

**Costs accepted:** **Fedora has never been booted as a terminal.** Every entry in `docs/tests.md` is unrun there, so the claim arrives as `intended` and stays that way until somebody watches a Fedora terminal work end to end — this decision widens what is *claimed* ahead of what is *watched*, which is the thing this project's rules exist to prevent. It is accepted here only because the alternative is to build it and not say so.

**The specific untested risk is SELinux**, which Fedora enforces by default and which the apt platforms do not. The product gives a system identity a home under `/var/lib/encore` and starts a graphical session as it. Nothing in the record mentions SELinux anywhere, so nobody has established whether that arrangement is permitted, and an SELinux refusal is characteristically silent — which is this project's recurring failure shape, now with a new cause. If a policy module turns out to be needed, the product gains a Fedora-only component and this decision's "one implementation" claim weakens.

Finally, the claimed surface doubles while the author count does not. A defect reported on Fedora cannot be reproduced on an apt terminal and the reverse, so every future failure report now carries a question it did not carry before.

**Corrected 2026-10-05 — three of the statements above have moved. The decision itself stands unchanged.**

**1. The untested risk named above turned out to cost nothing, and a different one did the damage.** SELinux was identified here as "the specific untested risk" and was measured on 2026-10-04 against the live kernel: `/var/lib/encore` carries `var_lib_t`, both candidate domains carry `files_unconfined_type`, and the `NoNewPrivileges=` transition is permitted. **No policy module is needed and the installer gains no SELinux step, so this decision's "one implementation" claim holds.** What actually blocked a Fedora conversion was not on this list at all: a Debian multiarch path computed from `uname -m` and handed to the step that writes the RDP password (`D-A19`, second site). **The risk register named the exotic hazard and missed the one that was already in the code** — worth recording, because the same reasoning will be applied to the next family.

**2. "Two of the seven package names differ" is now three differences, and the two lists are no longer the same length.** `openh264` was added to the dnf arm on 2026-10-05 and has no apt counterpart, because Debian and Ubuntu ship the real `libopenh264` in main with no stub beside it. So apt asks for seven packages and dnf for eight. The underlying reason matters more than the count: a fresh Fedora satisfies the client's dependency on `libopenh264.so.8` with **`noopenh264`, a stub that provides the library and decodes nothing** — the install is clean and H.264 silently does not work. Naming the real package swaps the stub out, from a repository Fedora enables by default. **This is a case where identical capabilities required a *different number* of packages, not a different name**, which the original cost estimate had no category for.

**A package name correction, 2026-10-05, inside this correction.** The paragraph above first said a fresh Fedora satisfies **`libfreerdp3`**'s dependency. **There is no `libfreerdp3` package on Fedora.** `rpm -q libfreerdp3` returns "not installed"; the library is `/usr/lib64/libfreerdp3.so.3` and the package that ships it is **`freerdp-libs`** (`freerdp-libs-3.31.1-1.fc44`, carrying the auto-generated `Requires: libopenh264.so.8()(64bit)`). `libfreerdp3` is a Debian-style name, written here while reasoning about a Fedora machine. The architect caught it the same day and measured the replacement. The *soname* claim was always right; only the package name sent a reader looking for something that does not exist. **The same wrong name is still in the comment on the dnf arm of the family block in `encore-install.sh`** — a comment, not behaviour, so it changes nothing a machine does, and it is filed rather than hot-fixed. Recorded because this is the third time this week a Debian-shaped fact was written into a Fedora explanation, after the multiarch path (`D-A19`, twice).

**3. "Every entry in `docs/tests.md` is unrun there" is no longer true.** The **install half** of test 14b passed on a Fedora 44 VM on 2026-10-05: the family detection, the dnf install path and the keyring suppression were watched working on a real dnf machine. **"Fedora has never been booted as a terminal" remains exactly true** — no Fedora machine has shown a session, so `R-1` stays `intended` for dnf and this decision still claims more than has been watched. Note that the `openh264` line was added *after* that run, so the eighth package is unwatched code.

**Source:** the author, 2026-10-04

### D-037 — ~~A terminal must be able to decode its session's video, and the installer checks rather than supplies it~~ — **WITHDRAWN 2026-10-05, the same day it was taken** — 2026-10-05
**Withdrawn because its central factual premise is false.** The decision assumed a terminal could *use* hardware H.264 decoding. It cannot. Measured from the shipped binary on the author's Fedora 44 machine, hours after this decision was written:

```
WITH_VAAPI=OFF
WITH_VAAPI_AVAILABLE=0      <- not even buildable there
WITH_FFMPEG=OFF
WITH_VIDEO_FFMPEG=OFF
WITH_OPENH264=TRUE
```

and `objdump -p /usr/lib64/libfreerdp3.so.3` lists exactly one relevant library, `libopenh264.so.8` — **no `libva`, no `libva-drm`, no `libavcodec`.** The client decodes H.264 on the processor, in software, always. Debian's own packaging sets `-DWITH_VAAPI=OFF` too, so this is every distribution rather than a Fedora quirk, and FreeRDP's `WITH_VAAPI` is an *encoding* feature for its shadow server in any case — its paired option is literally `WITH_VAAPI_H264_ENCODING`. **There is no client-side hardware decode path to switch on.** So the `vainfo` check this decision ordered would have gated conversion on a capability nothing on the machine consumes, and the driver packages it named would have changed nothing on a terminal.

**A second, independent reason, which would have withdrawn it alone: the check refuses every Raspberry Pi.** There is no VA-API driver for VideoCore, so `vainfo` fails outright. Pi 4 and earlier decode H.264 in hardware through a different interface entirely (V4L2, `bcm2835-codec`), and Pi 5 has no H.264 decoder at all. Raspberry Pi OS is the first platform this product names. This decision priced neither fact.

**How the error was made, because that is the part worth keeping.** The chain was: the author watched a Fedora session and found it unusable — true, and still unexplained. The product manager then noticed `openh264` absent from the install log's weak-dependency list and inferred a missing codec. **That inference was wrong about the *mechanism* and right about the *symptom* — and the correction below, written hours later on 2026-10-05, is the important part of this entry.**

The original withdrawal said: *`libopenh264.so.8` is a hard link in `libfreerdp3`, so rpm generates an automatic requirement and the package was installed all along, pulled in by `freerdp` rather than by `remmina`'s recommendation.* **That is true of the author's workstation and false of a fresh Fedora.** Two packages provide `libopenh264.so.8()(64bit)`: `openh264` from `fedora-cisco-openh264`, which decodes, and **`noopenh264` from Fedora's own repositories, which provides the library and decodes nothing**. A fresh Fedora satisfies the requirement with the stub. The link resolves, the install is clean, and H.264 decoding silently does not work. **So the author was right from the first report and a working decoder genuinely was missing** — it was simply not missing in the way either of us first said, and not at the layer the withdrawn decision addressed.

The error was made the same way as the one this entry withdraws: `rpm -q --whatprovides` was run on a machine that already had the real package, it answered `openh264`, and that was read as what a fresh machine would get. **Twice in one afternoon, on the same question, by reading a configured machine instead of the one being converted.** `CONTRIBUTING.md` names this exactly.

**The fix is one package on the dnf side and it is cheap:** `openh264` obsoletes `noopenh264 < 1:0`, so installing it swaps the stub out with no extra flags, and `fedora-cisco-openh264` is enabled by default — **no third-party repository, which is what the author refused**. The apt family is unaffected; Debian and Ubuntu ship the real library in main with no stub. Shipped in `encore-install.sh`'s package list.

**This does not revive the withdrawn decision.** Hardware decoding remains something a terminal cannot use at all, so requiring it and refusing machines over it was wrong on its own terms. What changed is that the slow session is **no longer unexplained** — the sentence below claiming otherwise is superseded by this paragraph. The author's instruction — detect and refuse rather than install a third-party repository — was sound and was followed; it was applied to a cause that did not exist. **Nobody ran the one command that would have settled it**, which is the failure `CONTRIBUTING.md` names by name: do not reason from configuration to runtime. It was committed here while writing a product decision, which is the most expensive place in this repository to commit it.

**What survives.** The author's refusal to have the installer enable RPM Fusion stands on its own and is worth keeping for whenever a third-party repository is next proposed: adding one is a machine-wide, persistent change that `R-11` and `D-007` would oblige the undo to remove, and removing a repository strands every package installed from it. Also measured and worth keeping: on Fedora 44 **no package named `mesa-va-drivers` exists at all**, and `libva-nvidia-driver` is in Fedora's own repositories rather than RPM Fusion — this decision's original text overstated the Nvidia case by one package.

**What replaces it: nothing, and that is deliberate.** The slow session is real and its cause is now openly unknown. The strongest remaining candidate is that the terminal is being sent H.264 at all and decoding it in software on a weak processor — which points at the connection profile's never-examined settings (`network`, `glyph-cache`, colour depth) under backlog item 13c, not at any package. That costs no packages and refuses no machines. `R-20` is removed and backlog item 18 is withdrawn.

**Superseded-by:** nothing yet.

---

*The original decision follows, unedited, because a decision that was wrong is part of the record.*

### D-037 (original text, withdrawn) — A terminal must be able to decode its session's video, and the installer checks rather than supplies it — 2026-10-05
**Decision:** Hardware H.264 decoding becomes a **requirement** of the machine being converted, recorded as `R-20`. The installer **detects whether the machine can decode, and refuses to convert it when it cannot**, printing the exact commands for that machine's graphics hardware. **The installer does not install the driver and does not enable any third-party repository.**

**Why:** The author's call on 2026-10-05, during the first Fedora conversion ever performed. Treating it as a requirement is sound for the reason the author gave: hardware H.264 decoding has been in Intel graphics since 2011 and in AMD's for as long, so by 2026 the *silicon* is a safe assumption on anything this product would be installed on. What is not a safe assumption is the *driver*, and that is a packaging fact rather than a hardware one.

The refusal is the installer's job because **the failure is silent and expensive**. A terminal with no hardware decoding still works — it just spends its processor doing in software what the chip does for free, on exactly the old, weak machines this product exists to reuse. Nothing reports it. It was found only because a human watched a session and thought it felt wrong, which is not a diagnostic anyone should depend on.

The reason the installer stops rather than fixes is that **on Fedora every usable driver lives in RPM Fusion**, measured on 2026-10-05: `mesa-va-drivers-freeworld` for AMD and `libva-intel-driver` for older Intel in RPM Fusion Free, `intel-media-driver` for Intel Gen8 and later in RPM Fusion Nonfree, and Nvidia needing a proprietary driver plus a translation layer. Fedora's own repositories carry `libva`, the interface, and no driver behind it. So "install it if missing" would mean this project adding a third-party repository to a stranger's machine — a machine-wide, persistent change that `R-11` and `D-007` would then require `encore-uninstall.sh` to remove, and removing a repository strands every package installed from it. The author rejected that, and the rejection is the right way round: the product asks for one capability and declines to acquire it on the adopter's behalf.

This also keeps the product consistent with how it already treats a machine that does not qualify. `D-024` excludes older releases; the systemd floor refuses rather than works around. A missing driver now behaves the same way.

**Costs accepted:** **This turns away working machines.** A terminal with no hardware decoding is slow, not broken, and the product will now refuse to convert it — so an adopter whose machine would have produced a usable, if warm, terminal is stopped and asked to install something first. That is a real narrowing of `R-1` and `R-2`, and it is the second refusal added in two days: `D-A20` removed one and this adds another, which is worth noticing rather than filing as unrelated.

The refusal also lands on the adopter least able to act on it. Someone converting an old machine in a household now meets a message about graphics drivers and third-party repositories, which is a harder thing to be told than "install a newer Debian". The message must therefore name the exact commands for the hardware in front of them, and a generic message would make this decision worse than no check at all.

**Detection is itself unproven.** The reliable test is `vainfo`, which ships in `libva-utils` — present in Fedora's own repositories and in the apt families, so the check costs no third-party anything. But nobody has established whether the apt family needs this check at all; Debian does not strip codecs from Mesa the way Fedora does, so the one converted apt machine may have had hardware decoding all along and nobody measured it. The check is therefore written as a capability test on both families rather than as a Fedora special case, and the record must not claim the apt family was verified until somebody looks.

**A correction belongs with this decision.** `docs/other-machine.md` recipe 3 checks `VAEntrypointEncSlice` — *encoding*, which is what the machine being connected to must do. A terminal must *decode*, which is `VAEntrypointVLD`. These are different capabilities with different drivers, and conflating them would produce a check that passes on a terminal that cannot decode. The existing recipe is correct for its own machine and must not be copied for this one.

**What is deliberately not decided here:** whether a machine that fails the check may be converted anyway on the adopter's insistence. There is a real case for it — a virtual machine has no GPU passthrough at all and can never satisfy this, yet converting one is exactly how this product is developed and tested. Left open rather than guessed.

**Source:** the author, 2026-10-05, on the first Fedora conversion ever performed

