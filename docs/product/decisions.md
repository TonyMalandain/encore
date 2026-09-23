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
