# The envisioned solution

## In one sentence
Install this on an old Linux machine, point it at a computer, switch it on, and
that machine becomes a kiosk terminal — and switching it off gives you the old
machine back.

## What we are building

A capability you add to a machine you already have, rather than an operating
system you install over it. The machine keeps being itself. What changes is
that, while the capability is active, the screen is given over entirely to a
remote session and nothing local can take it back.

Three things follow from that, and they are the whole product. **It is
installable** — an install, a short configuration step naming the machine to
connect to, and an activation. **It is a kiosk** — the person sitting at the
terminal is shown whatever the machine at the other end puts on the screen,
and nothing else. There is no local desktop to escape to, no settings to
reach, and no way for that person to switch the capability off. **It is
reversible** — the administrator, working from a text console or over the
network because the screen is no longer available to them, can turn the
capability off and find the machine as it was.

A terminal is an unattended machine sitting in someone's room, so what it can
reach is part of what it is. It runs with no administrative privilege and
reaches nothing beyond the machine it was pointed at, the screen, the input
devices and the audio devices. The single credential it needs to open that
connection is set during configuration and kept encrypted; it opens a door to
a login screen and nothing more.

The terminal's own hardware is what the session should feel like it is running
on. Sound in particular belongs to the machine the person is sitting at: the
terminal's audio devices become the session's defaults in both directions,
without anyone choosing them from a list, so a call works from the machine a
person is actually sitting at.

The machine being connected to is not part of this product. It is the
adopter's own machine, set up their own way, and we make no claim about it and
change nothing on it. The product's whole surface is the old computer.

Because a stranger decides whether to spend an evening on this by reading it,
the written explanation of what it does, what it changes on their machine, and
how to undo it is part of the product rather than something around it.

## Requirements

Environment first, so a reader can rule themselves out quickly.

`real` and `intended` are truth markers, not a schedule. Where a `real`
requirement carries an **Evidence** line, that line says how strongly it is
known. Some of this record was read in the prototype's code and never watched;
a little of it has been watched on a virtual machine — first on 2026-09-14, and
again on 2026-09-23 on a machine converted from nothing by following the
written procedure. Nothing here has been watched working on an old machine.
`read in code` therefore means read, not observed.

### R-1 — The terminal runs a Linux with the apt or dnf package manager, Wayland, and systemd
- **Serves:** the adopter reusing "old computers sitting in a cupboard" — this
  is the machine we can actually work with.
- **Who it serves:** terminal administrator, prospective adopter.
- **What they get:** they can tell in ten seconds whether their old machine
  qualifies.
- **State:** `real` for the apt family; `intended` for dnf.
- **Evidence:** apt family claimed only. **The dnf family is claimed and not
  watched** — no terminal has ever been converted on Fedora, so every entry in
  `docs/tests.md` is unrun there. D-036 widened this requirement on 2026-10-04
  and recorded that it widened the claim ahead of the observation.
- **Identical either way:** every other requirement in this document applies
  unchanged on both families. Nothing is offered on one and withheld on the
  other. Only the step that installs software differs.

### R-2 — No particular hardware is required
- **Serves:** the cupboard of mismatched old machines the problem describes.
- **Who it serves:** prospective adopter.
- **What they get:** whatever they have lying around is a candidate, as long
  as it satisfies R-1.
- **State:** `real`
- **Evidence:** claimed only
- **A refusal that contradicted this was found on 2026-10-04 and is being
  removed.** `encore-install.sh` listed three processor names and refused every
  other machine — `die "unsupported architecture"`. That was never a product
  limit. It existed only because the script had to build a Debian multiarch
  directory name to hide Remmina's keyring plugin, so a mechanism's need leaked
  out as a policy and turned away machines this requirement claims. Fedora also
  builds for `ppc64le`, `s390x` and `riscv64`, and that line would have refused
  two of them. The repair finds the plugin instead of computing its path, so the
  product no longer refuses a machine for its processor, **and still refuses a
  machine whose library layout the unit does not name.** `R-2`'s cost is reduced,
  not eliminated — this note first claimed the product now "says nothing about
  unusual processors in either direction", which was too strong and is corrected
  here on 2026-10-04, the same day it was written. The refusal was relocated, not
  ended: a Debian machine on a fourth processor has a fourth multiarch directory,
  so the path the installer finds is one the unit does not list, and the
  conversion still stops. What changed is that the refusal is now **conditional
  and true** rather than unconditional and wrong — it rests on whether the
  keyring plugin can actually be hidden on that machine, which is a fact that
  bears on whether the product works there, instead of on a processor name, which
  is not. The message changed with it, from `unsupported architecture` — which
  this requirement authorises nobody to say — to the exact path and the line that
  would fix it. The honest reading of this requirement was always the weaker one:
  nothing is assumed, and nothing is tested beyond the one Mac Mini and a virtual
  machine.

### R-3 — The machine being connected to is untouched and unconstrained
- **Serves:** the owner of the machine being connected to, who "asked for
  nothing and gets nothing from the product directly" and is "simply expected
  to absorb whatever the terminals do".
- **Who it serves:** owner of the machine being connected to.
- **What they get:** nothing is installed on, or changed on, the machine
  hosting the sessions.
- **State:** `real`
- **Evidence:** claimed only

### R-4 — Converting a machine is an install, a short configuration, and an activation
- **Serves:** "assembling them by hand is the actual problem… an afternoon of
  fiddling, repeated for every machine".
- **Who it serves:** terminal administrator.
- **What they get:** a machine becomes a terminal in minutes, the same way
  every time.
- **State:** `intended`

### R-5 — The configuration names the machine to connect to
- **Serves:** the project only being worth writing down if it works in houses
  other than the author's.
- **Who it serves:** terminal administrator, prospective adopter.
- **What they get:** they point a terminal at their own machine without
  editing anything that was shipped.
- **State:** `intended`

### R-6 — While active, the terminal shows only the remote machine's login screen
- **Serves:** "a person at the terminal who is shown a desktop, a settings
  panel, or an error dialog will click on it".
- **Who it serves:** person at the terminal, terminal administrator.
- **What they get:** local graphical use of the machine is impossible; the
  screen is the remote session and nothing else.
- **State:** `intended`
- **Note:** this is an absolute — it has to hold every time, not almost always.
  It covers the screen, not the machine: reaching a text console is not an
  escape from it, because a login prompt grants nothing to someone without the
  administrator's password (D-017). A read of the prototype by the architect
  found one real breach, which R-17 answers: a terminal that cannot find its
  configuration hands the person a local application for opening connections
  and browsing files.

### R-7 — [WITHDRAWN on 2026-09-13, see D-015]
Was: *"Nobody is signed in for you; anyone with valid credentials can use any
terminal."* Withdrawn because signing in happens inside the connection, and
everything inside the connection belongs to the machine being connected to.
The number is retired and is never reused.

### R-8 — An active terminal survives a restart and comes back by itself
- **Serves:** "if the machine ever drops back to its own local desktop — after a
  reboot… — then it has stopped being a terminal and quietly become an
  unmanaged computer in somebody's room".
- **Who it serves:** person at the terminal, terminal administrator.
- **What they get:** a terminal that has been switched on stays switched on. It
  comes back from a reboot or a power cut to the remote login screen with
  nobody touching it, ready for the person sitting at it to sign in to the
  machine at the other end.
- **State:** `intended`
- **Note:** this is a property of a terminal being active, not of how it was
  activated. A way of switching the capability on that lasts only until the
  next restart does not satisfy this requirement. Splitting this from R-18 on
  2026-09-21: surviving a restart and surviving a dropped connection are two
  different promises with two different mechanisms behind them, and one marker
  covering both let the weaker borrow the stronger's credibility.

### R-18 — A dropped connection is retried, and nothing local appears while it is down
- **Serves:** "if the machine ever drops back to its own local desktop — …after
  the connection dies, after any hiccup — then it has stopped being a
  terminal".
- **Who it serves:** person at the terminal, terminal administrator.
- **What they get:** a connection that fails or dies is retried indefinitely
  and unattended, and while it is down the person in front of the terminal is
  never handed a local application, an error dialog, or anything else they
  could act on. The terminal returns to the remote login screen by itself when
  the machine at the other end can be reached again.
- **State:** `intended`
- **Note:** indefinite retry is D-020, which separates this case from a broken
  configuration — a terminal whose configuration is missing or invalid stops
  instead (R-17). Waiting is the normal case, not the exceptional one: the
  machine at the other end is expected to be down about one per cent of the
  time (D-026), so a terminal must sit through an outage patiently and without
  complaint. What the person at the terminal sees while it waits, and for how
  long, is not settled — an open question in `NOTES.md`.

### R-9 — Only the machine's root administrator can deactivate the capability
- **Serves:** "someone who can turn the kiosk off has simply been given an
  unsupervised computer by another route".
- **Who it serves:** terminal administrator.
- **What they get:** the off-switch is out of reach of the person sitting at
  the terminal.
- **State:** `intended`

### R-10 — An active terminal can be administered from another machine
- **Serves:** "once the capability is on, the screen belongs to the remote
  session, so the administrator has to be able to reach the machine some other
  way".
- **Who it serves:** terminal administrator.
- **What they get:** they can reach an active terminal from elsewhere on the
  household network, manage it and switch it off, without its screen and
  without being in the room.
- **State:** `real`
- **Evidence:** observed on a virtual machine, 2026-09-14 — reaching the
  terminal from another machine kept working while its screen was unusable and
  its own controls were wedged. One machine, once.
- **Note:** this is about reaching the terminal *from somewhere else*. Whether
  a person sitting physically at the terminal can get to a text login prompt on
  it is a separate matter, settled by D-017, and it neither strengthens nor
  weakens this requirement. The two were worded as one until 2026-09-21, which
  caused a local failure to be read as evidence against this requirement when
  it was not.

### R-11 — Deactivating returns the machine to what it was
- **Serves:** "if turning the capability on cannot be undone cleanly, then
  every old computer is a one-way bet".
- **Who it serves:** terminal administrator, prospective adopter.
- **What they get:** the old machine back, working as before, with no repair
  by hand.
- **State:** `real`
- **Evidence:** claimed only

### R-12 — Sound comes out of the speakers in front of the person using the terminal
- **Serves:** "a terminal with no sound is half a computer, and audio on the
  wrong machine puts one person's noise into another person's room".
- **Who it serves:** person at the terminal, owner of the machine being
  connected to.
- **What they get:** sound from the session plays on the terminal, on whatever
  output that machine already uses. Nobody picks a device from a list, at either
  end.
- **State:** `real`
- **Evidence:** observed on a virtual machine and on a converted Mac Mini,
  2026-09-29. A terminal that cannot produce sound says so in one line and still
  connects — a silent terminal is a terminal, an unreachable one is not. Sound
  follows the active session on the seat, so using a text console on the terminal
  can silence it until it restarts (D-034).

### R-20 — A terminal can decode its session's video without software fallback
- **Serves:** the adopter reusing an old machine, which is the machine least
  able to spend its processor on work its graphics chip does for free.
- **Who it serves:** terminal administrator, prospective adopter, and the person
  sitting at the terminal, who experiences this as the session feeling wrong.
- **What they get:** a terminal that is refused at conversion time if it cannot
  decode, rather than one that works slowly and never says why.
- **State:** `intended`
- **Evidence:** nothing is built. Observed in the negative on 2026-10-05, on a
  Fedora 44 virtual machine on AMD: the session was unusable and nothing in any
  log named the cause. Found because a human watched the screen and thought it
  felt wrong.
- **Why it is a requirement and not a defect:** hardware H.264 decoding has been
  in Intel and AMD graphics since about 2011, so the capability is a safe
  assumption on anything this product would be installed on. The **driver** is
  not. On Fedora every usable one lives in RPM Fusion and Fedora's own
  repositories carry only `libva`, the interface — measured 2026-10-05.
- **The product checks and refuses; it does not supply.** `D-037` gives the
  reasoning: installing the driver would mean adding a third-party repository to
  somebody's machine, which `R-11` would then oblige the undo to remove, and
  removing a repository strands what was installed from it.
- **Decode, not encode.** This is `VAEntrypointVLD`. The machine being connected
  to needs the opposite capability, `VAEntrypointEncSlice`, and
  `docs/other-machine.md` recipe 3 checks for that one. Different capability,
  different driver — a check copied from there would pass on a terminal that
  cannot decode.
- **Untested on the apt family.** Debian does not strip codecs from Mesa the way
  Fedora does, so the one converted apt machine may have satisfied this all
  along. Nobody has measured it, and this requirement must not be read as
  evidence either way.

### R-19 — A terminal with a microphone can be spoken into
- **Serves:** "a terminal with no sound is half a computer" — the half of it
  that makes a call possible rather than only audible.
- **Who it serves:** person at the terminal.
- **What they get:** on a machine that has a microphone, the session hears it,
  with nobody choosing a device. **A terminal with no microphone stays fully
  usable** — this is the half that matters most, because most old machines have
  no microphone at all.
- **State:** `intended`
- **Note:** untested in both directions of the word. Nobody has spoken into a
  terminal, and nobody has watched what a terminal with no microphone does. The
  named risk is that a failing input channel takes the connection down with it,
  which the indefinite retry (R-18) would then present for ever as an
  unreachable machine — the promise above would fail in the most confusing way
  available. Whether the single setting that switches sound on can be limited to
  one direction is also unknown.

### R-13 — A stranger can judge the product before installing it
- **Serves:** "they will decide whether to spend an evening on it by reading,
  before they install anything".
- **Who it serves:** prospective adopter.
- **What they get:** they can tell whether their machine qualifies, what will
  change on it, and how to undo it, without installing anything.
- **State:** `intended`

### R-14 — The one credential the terminal holds is kept encrypted
- **Serves:** the terminal being "an unmanaged computer in somebody's room" if
  anything about it is left casually open.
- **Who it serves:** terminal administrator, owner of the machine being
  connected to.
- **What they get:** the credential that opens the connection is set once
  during configuration and is not readable by anyone who picks the machine up.
- **State:** `intended`
- **Note:** what this sentence should promise is open — see Q-P2 in `NOTES.md`.
  The architect reports that no way of storing a secret on an unattended
  machine that must reconnect on its own, with nobody there to unlock
  anything, holds against someone who has the machine in their hands. A reader
  should take R-14 as an intention and not as a protection they can rely on.

### R-15 — The capability runs without administrative privilege
- **Serves:** "converting a machine is a commitment" — an adopter deciding
  what installing this actually costs them.
- **Who it serves:** terminal administrator, prospective adopter.
- **What they get:** nothing on the terminal runs with the run of the machine.
- **State:** `real`
- **Evidence:** read in code, never observed.

### R-16 — The capability reaches only what it needs
- **Serves:** the same commitment — what an unattended machine in somebody's
  room can touch is what the adopter is really agreeing to.
- **Who it serves:** terminal administrator, prospective adopter, owner of the
  machine being connected to.
- **What they get:** it can reach the machine it was configured to connect to,
  the screen, the keyboard, the mouse and the audio devices. Not the rest of
  the network, and not the rest of the machine.
- **State:** `intended`
- **Note:** "the machine it was configured to connect to" means that machine
  and not something else on the household network answering to its name. The
  architect reports the terminal accepts whatever answers, which is what makes
  R-14 and R-16 one question rather than two: a credential that can be handed
  to an impostor was not protected by being hard to read. The clipboard is not
  on the list, by D-019.

### R-17 — A terminal that is not properly configured stops, and says so
- **Serves:** "a person at the terminal who is shown a desktop, a settings
  panel, or an error dialog will click on it" — the one breach of R-6 that has
  actually been found.
- **Who it serves:** person at the terminal, terminal administrator.
- **What they get:** a terminal with a missing or invalid configuration shows a
  plain message saying it is not configured, and stops. It never offers a local
  application instead, and it does not keep trying until someone has repaired
  the configuration. A terminal that simply cannot reach the machine it was
  pointed at is a different case and keeps trying (R-18).
- **State:** `intended`

## What the solution is not

- **Not an operating system or a distribution.** It is a capability added to a
  machine that already boots. Anything that requires reimaging the old machine
  defeats the reuse this exists for.
- **Not responsible for the machine being connected to.** Setting that machine
  up to accept sessions is the adopter's own business. Taking it on would mean
  supporting a second, unrelated environment and would double the surface a
  stranger has to trust.
- **Not a Linux outside the apt and dnf families, and not a display stack other
  than Wayland, and not a startup system other than systemd.** **Amended
  2026-10-04 by D-036**, which added the dnf family — the apt-only form of this
  entry named its own condition for being revisited, and the cost turned out to
  be four lines of the installer and two package names. The display stack and
  the startup system are unchanged and are not up for reconsideration: they are
  what the product is built out of, not a packaging detail. A third package
  manager would be reconsidered if someone other than the author ran it end to
  end.
- **Not responsible for anything inside the connection.** Establishing the
  connection is the whole job. Who signs in, whether they succeed, what their
  session looks like, whether several people can work at once, what files they
  have — all of that belongs to the machine at the other end, in the same way
  that a tunnel is not responsible for what travels through it.
- **Not a credential store.** The terminal holds exactly one secret — the one
  that opens the connection. It holds no personal identity and signs nobody
  in; who a person is belongs to the machine they log into.
- **Not a manager of credentials.** The connection credential is set when a
  terminal is configured and is never rotated, expired or reminded about.
  Changing it means configuring the terminal again. Would be reconsidered if
  that credential ever granted more than reaching a login screen.
- **Not a fleet tool, and it does not scale.** It is built for the two or
  three terminals in one household, and that number is doing more work than
  its size suggests: it is the whole reason the product assembles parts an
  ordinary Linux machine already has instead of adopting a thin-client
  platform, and it is why every terminal is configured on its own with no
  central place to change them all. Would be reconsidered when a change has to
  be made on every terminal by hand and one of them gets missed — watch for
  that symptom rather than for a count. A household running a dozen machines,
  or terminals in more than one household, is better served by the platforms
  this project turned down.
- **Not a manager of the terminal.** It does not update, monitor, inventory or
  administer the machine it runs on. Every additional privilege has to be
  argued for individually, and none of these has been.
- **Not a user-facing application.** There is no interface for the person at
  the terminal to configure, choose, or escape. That is the point of a kiosk.
- **Not parental controls, session limits, or content filtering.** Whatever
  restrictions apply to a person belong to the accounts on the machine they
  log into, not to the furniture they sit at.
