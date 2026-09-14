# The envisioned solution

## In one sentence
Install a package on an old Linux machine, point it at a computer, switch it
on, and that machine becomes a kiosk terminal — and switching it off gives you
the old machine back.

## What we are building

A capability you add to a machine you already have, rather than an operating
system you install over it. The machine keeps being itself. What changes is
that, while the capability is active, the screen is given over entirely to a
remote session and nothing local can take it back.

Three things follow from that, and they are the whole product. **It is
installable** — a package, a short configuration step naming the machine to
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
known, and the strongest evidence this record holds is a careful read of the
prototype by the architect — nothing here has been watched working on an old
machine. `read in code` therefore means read, not observed.

### R-1 — The terminal runs a Linux with the apt package manager, Wayland, and systemd
- **Serves:** the adopter reusing "old computers sitting in a cupboard" — this
  is the machine we can actually work with.
- **Who it serves:** terminal administrator, prospective adopter.
- **What they get:** they can tell in ten seconds whether their old machine
  qualifies.
- **State:** `real`
- **Evidence:** claimed only

### R-2 — No particular hardware is required
- **Serves:** the cupboard of mismatched old machines the problem describes.
- **Who it serves:** prospective adopter.
- **What they get:** whatever they have lying around is a candidate, as long
  as it satisfies R-1.
- **State:** `real`
- **Evidence:** claimed only

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

### R-8 — A reboot or a dropped connection returns to the remote login screen, never to a local desktop
- **Serves:** "if the machine ever drops back to its own local desktop… it has
  quietly become an unmanaged computer in a child's room".
- **Who it serves:** person at the terminal, terminal administrator.
- **What they get:** the terminal recovers by itself, unattended, and there is
  no state in which it is an ordinary computer.
- **State:** `real`
- **Evidence:** read in code, never observed. Two qualifications, neither of
  which unmakes the requirement. Recovery is real but silent: a terminal that
  has been failing to reach the machine at the other end for days looks the
  same, to the administrator managing it without a screen, as one that is
  working — the open question Q-P3 in `NOTES.md`. And the second half of this
  requirement, that there is no state in which the machine is an ordinary
  computer, is R-6's promise borrowed; it is only as strong as R-6, which is
  now `intended`.

### R-9 — Only the machine's root administrator can deactivate the capability
- **Serves:** "a child who can turn the kiosk off has simply been given an
  unsupervised computer by another route".
- **Who it serves:** terminal administrator.
- **What they get:** the off-switch is out of reach of the person sitting at
  the terminal.
- **State:** `intended`

### R-10 — The administrator can reach the machine without the screen
- **Serves:** "once the capability is on, the screen belongs to the remote
  session".
- **Who it serves:** terminal administrator.
- **What they get:** a text console and remote access still work on an active
  terminal, so it can be managed and switched off.
- **State:** `real`
- **Evidence:** read in code, never observed. The text console half of this is
  the same arrangement that weakens R-6 — see Q-P1 in `NOTES.md`.

### R-11 — Deactivating returns the machine to what it was
- **Serves:** "if turning the capability on cannot be undone cleanly, then
  every old computer is a one-way bet".
- **Who it serves:** terminal administrator, prospective adopter.
- **What they get:** the old machine back, working as before, with no repair
  by hand.
- **State:** `real`
- **Evidence:** claimed only

### R-12 — The terminal's own audio devices are the session's defaults, in both directions
- **Serves:** "a terminal with no sound is half a computer, and audio on the
  wrong machine puts a child's noise into an adult's room".
- **Who it serves:** person at the terminal, owner of the machine being
  connected to.
- **What they get:** sound comes out of the speakers in front of them and, on
  a machine that has a microphone, goes in through that microphone — so a call
  works. Nobody picks a device from a list. A terminal with no microphone is
  still fully usable.
- **State:** `intended`

### R-13 — A stranger can judge the product before installing it
- **Serves:** "they will decide whether to spend an evening on it by reading,
  before they install anything".
- **Who it serves:** prospective adopter.
- **What they get:** they can tell whether their machine qualifies, what will
  change on it, and how to undo it, without installing anything.
- **State:** `intended`

### R-14 — The one credential the terminal holds is kept encrypted
- **Serves:** the terminal being "an unmanaged computer in a child's room" if
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
- **Serves:** the same commitment — what an unattended machine in a child's
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
  pointed at is a different case and keeps trying (R-8).
- **State:** `intended`

## What the solution is not

- **Not an operating system or a distribution.** It is a capability added to a
  machine that already boots. Anything that requires reimaging the old machine
  defeats the reuse this exists for.
- **Not responsible for the machine being connected to.** Setting that machine
  up to accept sessions is the adopter's own business. Taking it on would mean
  supporting a second, unrelated environment and would double the surface a
  stranger has to trust.
- **Not a Linux other than the apt family, and not a display stack other than
  Wayland, and not a startup system other than systemd.** Supporting one
  combination is what makes the product assessable in one sitting. Would be
  reconsidered if someone other than the author ran a second combination end
  to end.
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
