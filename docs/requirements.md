# What a machine must have, and why

`README.md` lists the requirements. This file says why each one is there and
what happens on a machine that misses it — which is the part worth reading
before converting hardware you cannot easily re-image.

**The general shape: most of these fail silently.** A machine that misses one
usually installs, connects and looks correct, and behaves differently from
everything written here without saying so. That is why they are stated as
requirements rather than left to be discovered.

---

## systemd 254 or newer

```sh
systemctl --version | head -1
```

**The real requirement.** The distributions named in `README.md` are simply the
ones that carry it; 254 or higher qualifies whatever the distribution, and
anything older does not.

**What breaks:** the recovery behaviour. When a connection drops, the terminal
is meant to retry on a delay that grows — quickly at first, then backing off,
so an outage on the other machine does not become a machine hammering the
network for hours. The settings that do that arrived in systemd 254. **Older
versions ignore them without complaining** and give flat retries instead.

**Why that matters more than it sounds:** nothing reports it. The terminal
installs, connects and works. You would have a terminal that recovers
differently from everything documented, and no log line, error or warning would
ever say so. Nothing in the installer checks this today either — that gap is
backlog item 4.

**This is the requirement that rules out the most otherwise-fine hardware.**
Raspberry Pi OS only crossed it in October 2025, so a Pi imaged before then
needs updating first. Debian 12 and Ubuntu 24.04 are both below it.

Recorded as D-024, which accepted excluding older releases as a cost.

## Wayland

`cage`, the compositor that gives the terminal its full-screen session, is
Wayland-only. **There is no X11 path and there is no fallback** — this is not a
version requirement that degrades, it is a yes or no.

**No particular hardware is required, but "has a working Wayland driver" is what
actually decides it**, and that has not been tested on anything genuinely old.
The oldest machine this has run on is a 2012 Mac Mini. Backlog item 14 is the
work of finding out where the real floor is.

**On a virtual machine, give it virtio-gpu.** Without it Wayland will not start
and the symptom looks like a fault in this software rather than a missing
display device.

## wireplumber 0.5 or newer

```sh
wireplumber --version
```

**The one soft requirement.** A machine below it still qualifies and still
works — it is silent.

The terminal starts its own sound server inside its session, using
`wireplumber -p main-embedded`. That profile is how a sound session manager runs
with no session message bus, which is exactly the situation a kiosk session is
in. **Profiles arrived in wireplumber 0.5.** In 0.4 the option does not exist at
all, so the process would exit immediately on an unknown option and nothing
would say why.

Rather than fail that way, the runner reads the version first and declines,
loudly, in one line. Ubuntu 24.04 LTS ships 0.4.17, which is why `README.md`
asks for 26.04.

**This is the one requirement you are told about rather than left to discover**
— at install, and again on every start. `docs/troubleshooting.md` has the check,
under *A terminal with no sound*.

Nothing about the sound stack is detected at install time and frozen. A later
package upgrade that brings 0.5 turns sound on by itself, with nothing to re-run.

## An apt-family Linux

Raspberry Pi OS, Ubuntu and Debian. `encore-install.sh` calls `apt-get`
directly, so **other package managers are not supported** — not "untested",
unsupported. Recorded as D-003.

## An SSH server you can already log into

**Set this up before converting the machine, not after.** Once the terminal is
on, its screen belongs to the remote session: no desktop, no terminal window,
no menu. If the service then fails to start, or the connection never comes up,
SSH is how anyone gets in to look.

```sh
ssh <user>@<terminal> true && echo "reachable"
```

A text console still exists as a last resort — `Ctrl+Alt+F1` through `F6`, and
which one gives a login prompt varies by machine. But it means being physically
at the machine and knowing to reach for it, which is a great deal to ask of
whoever ends up living with the terminal.

The installer warns when it finds no SSH server, but it does not refuse.

## `git`, or a second machine with `scp`

The install is a clone plus a script (D-027). There is no package. If the old
machine cannot reach GitHub, `encore-push.sh` copies the files to it from a
machine that can, which is what needs `scp`.

## A second machine that already accepts RDP connections

Not a requirement on the terminal, and worth stating separately because it is
the one thing this project cannot help with: **Encore does nothing to that
machine and makes no claims about it** (D-002).

Two things about it nevertheless decide how well a terminal works, both covered
in `README.md` under *Recommended after it is working*:

- **Whether it can encode video in hardware.** A terminal costs a few megabits
  per second if it can, and about 130 if it cannot. Same terminal, same
  instructions, a hundredfold apart, and nothing tells an adopter which they
  have.
- **What its session offers a person who is not its administrator** — power
  controls, and password prompts they cannot answer.
