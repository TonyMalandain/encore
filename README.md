# Encore — turn an old Linux machine into a kiosk terminal

Install this on an old computer and it becomes a terminal: the screen shows a
remote desktop session and nothing else. Switch it off and you get the old
machine back.

You need a second machine that already accepts remote desktop connections —
the one the terminal will show. This project does nothing to that machine.

**Known issues are at the bottom.** Read them before you put a terminal in
front of anybody.

---

## Requirements

On the machine you are converting:

- **A Linux using `apt` or `dnf`.** Watched working on Raspberry Pi OS
  "trixie" (October 2025), Ubuntu 26.04 and Debian 13 — or newer — and on
  Fedora 44. A Fedora terminal has shown a session, kept it across a reboot,
  and behaved the same with SELinux enforcing and not enforcing. **Sound and
  the off-switch have not been watched on Fedora**, so if you want either,
  expect to be the first to try. No other package manager is supported.
- **systemd 254 or newer** — `systemctl --version | head -1`
- **Wayland**
- **wireplumber 0.5 or newer** — `wireplumber --version`. Sound only; below it
  the terminal works and is silent.
- **An SSH server you can already log into**
- **`git`** — or a second machine with `scp`

And separately:

- **A second machine that already accepts RDP connections.** This project does
  nothing to it and makes no claims about it.

---

## Install

**Set up SSH first, not after.** Once the terminal is on, its screen shows the
remote session and nothing else — no desktop, no terminal window, no menu. If
the service fails to start, SSH is how you get in to look. Check from another
machine:

```sh
ssh <user>@<terminal> true && echo "reachable"
```

A text console remains as a last resort — `Ctrl+Alt+F1` through `F6`, and which
one answers varies by machine — but it means being at the machine and knowing to
reach for it, which is a lot to ask of whoever lives with the terminal.

**On a VM:** give it virtio-gpu, or Wayland will not start and you will debug
the wrong problem.

On the old machine, as root:

```sh
git clone https://github.com/TonyMalandain/encore.git
cd encore
sudo ./encore-install.sh
```

It asks three things — which machine to connect to, the account to use, and
that account's password. The password is not echoed and never reaches your
shell history. Nothing is switched on yet.

### If the old machine cannot reach GitHub

Copy the files across from a machine that can, instead of cloning:

```sh
./encore-push.sh <user>@<terminal>     # then, on the old machine:
sudo ~/encore-install.sh
```

### Switch it on

Then turn it into a terminal:

```sh
sudo systemctl set-default encore-kiosk.target
sudo reboot
```

It comes back up showing the remote login screen and nothing else.

The first line is safe to run from a desktop: it only decides what the machine
boots into next time, and changes nothing about the session you are sitting in.
Your desktop stays until you reboot. (`systemctl isolate encore-kiosk.target`
is the one that switches over immediately, tearing down the desktop under you.
It is useful for a quick try, but it does not reproduce boot conditions.)

### Then tune the other machine

Read **[`docs/other-machine.md`](docs/other-machine.md)** for recommendations on
how to tune the machine your terminals connect to.

---

## Uninstall

**You cannot do this from the terminal's own screen.** That screen belongs to
the remote session now — there is no local desktop, no terminal window, no
menu. Get a local shell one of two ways:

- **Over SSH from another machine**, which is the easy one:
  ```sh
  ssh <user>@<terminal>
  ```
- **At the machine itself**, on a text console: `Ctrl+Alt+F1` through `F6`,
  whichever one gives you a login prompt. Log in as your ordinary account.

Either way, you land in a normal shell on the old machine. Then go to wherever
you cloned the repository and run:

```sh
cd ~/encore
sudo ./encore-uninstall.sh
```

It puts back the startup mode the machine had before, removes the service, the
account it created, the connection profile and the stored password, then tells
you if anything survived. `remmina`, `cage` and `kbd` are left installed —
they are ordinary software and removing them could break something else.

Reboot afterwards to come back up as an ordinary machine.

### If the repository is gone from the machine

`encore-uninstall.sh` is the supported route and checks its own work. This is
the sequence by hand, for a converted machine that no longer has the clone on
it:

```sh
systemctl set-default graphical.target   # or whatever it was before
systemctl disable encore-kiosk.service
rm /etc/systemd/system/encore-kiosk.service /etc/systemd/system/encore-kiosk.target
rm /usr/local/bin/encore-kiosk.sh
systemctl daemon-reload
userdel -r encore          # deletes the profile, the key and the stored password
rm -rf /var/lib/encore
reboot
```

**What the machine booted into before conversion is recorded** in
`/var/lib/encore/encore-install.conf` — read it before that `rm -rf`, or you are
guessing at the first line.

Then confirm, rather than trusting the removal you just did:

```sh
id encore; ls -d /var/lib/encore; ls /etc/systemd/system/ | grep encore
systemctl get-default
```

---

## Known issues

Detail for every one of these is in
[`docs/architecture/debt.md`](docs/architecture/debt.md), and the order they get
fixed in is [`BACKLOG.md`](BACKLOG.md).

1. **A terminal that has stopped working reports itself healthy.** Watched: the
   connection failed, a dialog went up on the terminal's
   screen, and the journal recorded only that the service had started. The
   screen is the only place a failure appears, and it is the one place you are
   told not to debug through.
2. **A failed connection puts a clickable dialog in front of whoever is
   sitting there** — a certificate prompt, an error. That is precisely what the
   product exists to prevent.
3. **A missing or invalid profile still drops you into the client's own
   application**, a connection editor and a file chooser. The installer always
   writes a profile, so a freshly converted machine will not meet this — but a
   bad edit, an interrupted re-install or a half-finished upgrade can.
4. **A dialog can open behind the session window**, where nothing can reach it.
   The compositor has no way to switch between windows.
5. **A sandboxing protection is switched off** so the session can start, so a
   terminal reaches more of its own filesystem than the design intends.
6. **The clipboard is open.** The connection profile is a verbatim copy of one
   observed working, and the decision to close the clipboard is not delivered
   yet.
7. **The console may not switch by itself** when the capability is started on a
   machine that is already running a desktop. Whether a machine that boots
   straight into terminal mode has the same problem is untested.
8. **It has barely run on real hardware.** One converted Mac Mini. Everything
   before it was a virtual machine, and nothing older or stranger than that Mac
   Mini has been tried.
9. **Using a text console on the terminal can silence it until it is
   restarted.** Sound follows whichever session is active on the seat, so
   switching to a text console and back leaves the terminal's session without
   it. Nothing on the screen says why. Restarting the terminal brings sound
   back. This is a known and accepted cost, not a fault to report.
10. **A terminal can take minutes to show its session at boot.** It is waiting
    for something else on your machine, not failing. `encore-kiosk.service`
    starts after the network is up, so anything slow earlier in startup delays
    the terminal second for second — on the one machine measured, an unused
    second network stack cost two minutes every boot. Not a fault in this
    software, and it is not caused by the monitor being switched off.
    [**The session takes a very long time to appear at boot**](docs/troubleshooting.md#the-session-takes-a-very-long-time-to-appear-at-boot)
    finds the cause on your machine.

---

## Working on this

**Something not working?** [`docs/troubleshooting.md`](docs/troubleshooting.md) lists every failure seen so
far, with the check that identifies it. Nearly all of them were silent — no
error, no log line — so the order of the checks matters.

**Changing something, or just curious how it is put together?**
[`CONTRIBUTING.md`](CONTRIBUTING.md) has the map of where everything is written
down, what to test and what to write down, and the rules this project holds
itself to.

---

## License

Apache License 2.0. The full terms are in [`LICENSE`](LICENSE), and the
copyright notice is in [`NOTICE`](NOTICE).

You may use, change and redistribute this, including commercially. If you
redistribute it you must keep the licence and the notice, state what you
changed, and not use the project's name to endorse what you built. The licence
also grants you the patent rights needed to use it, and takes that grant away
from anyone who sues over patents in it.

It comes with no warranty of any kind. That is not boilerplate here: several of
this project's own promises have never been observed working, and `Known issues`
above says which.

