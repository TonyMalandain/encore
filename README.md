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

- **An apt-family Linux.** Raspberry Pi OS "trixie" (October 2025), Ubuntu
  26.04, or Debian 13 — or newer. Other package managers are not supported.
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

### Then set up the other machine

**[`docs/other-machine.md`](docs/other-machine.md)** — three things to do on the
machine your terminals connect to. None of them is part of Encore, and none runs
on a terminal, but converting a machine creates all three and none announces
itself:

1. Take the power controls away from the session, so nobody at a terminal
   switches off the machine every terminal depends on.
2. Stop the software updater asking for a password nobody there can answer.
3. **Check that machine can encode video.** Without it each terminal costs
   about 130 Mbps instead of a few — and nothing tells you which you have.

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

If the repository is no longer on the machine, the manual sequence is in
*Undoing it by hand* below.

---

## What the installer does, step by step

`encore-install.sh` does all of this for you. It is written out because a lab
procedure has to be readable when something fails, and because every one of
these steps has bitten at least once.

Everything below runs as root on the machine being converted.

### 1. Packages

```sh
apt update
apt install remmina remmina-plugin-rdp cage kbd
```

`kbd` provides `chvt`, which the unit uses to bring the kiosk's console to the
front. Without it the service starts and nothing appears.

### 2. The user the terminal runs as

```sh
useradd --system --create-home --home-dir /var/lib/encore \
        --shell /usr/sbin/nologin encore
usermod -aG video,input,render encore
```

> **One note.** Nobody has checked which of those group memberships are
> actually needed — narrow them once it works (item 7).

### 3. Directories

```sh
install -d -o encore -g encore -m 700 /var/lib/encore/.local/share/remmina
install -d -o encore -g encore -m 700 /var/lib/encore/.config/remmina
```

### 4. The connection profile

Start from the template in this repository, which carries no host, no account
and no password:

```sh
install -o encore -g encore -m 600 encore-kiosk.remmina.template \
        /var/lib/encore/.local/share/remmina/encore-kiosk.remmina
```

Edit the two `CHANGEME` lines — `server` and `username`. The `name` field is
prefilled: it is the connection's label inside the client and nobody at the
terminal ever sees it.

Confirm nothing was missed. This must print `0`:

```sh
grep -c CHANGEME /var/lib/encore/.local/share/remmina/encore-kiosk.remmina
```

**Put exactly one profile in that directory.** The runner takes the first file
it finds in no defined order, so two profiles mean an unpredictable target.

### 5. The password, and the key that protects it

```sh
 systemd-run --pty --uid=encore \
  -p InaccessiblePaths=/usr/lib/x86_64-linux-gnu/remmina/plugins/remmina-plugin-secret.so \
  -E HOME=/var/lib/encore \
  remmina --update-profile /var/lib/encore/.local/share/remmina/encore-kiosk.remmina \
          --set-option password='<password>'
```

Only the password is set here. `server` and `username` were set in the file at
step 4 and survive this command untouched — setting the username again on the
command line would mean two sources for one value, and the command line wins
silently when they disagree.

Note the leading space, which keeps the password out of your shell history.

> **The leading space is not enough on its own.** It protects Bash history and
> nothing else. If you reach for `sudo` rather than already being root, `sudo`
> writes the whole command line to the auth log; and `systemd-run` creates a
> transient unit whose command line systemd records in the journal. Check both
> afterwards, and rotate the password on your main machine if either matches:
>
> ```sh
> grep -c 'set-option' /var/log/auth.log 2>/dev/null
> journalctl --no-pager -q | grep -c 'set-option'
> ```

Three things about this step, all learned the hard way:

- **The keyring plugin must be out of reach.** If Remmina can see
  `remmina-plugin-secret.so` it insists on a keyring, and an unattended
  terminal has nobody to unlock one. The `InaccessiblePaths` above hides it for
  that one command; the service unit does the same permanently. Check the path
  matches your architecture.
- **A `remmina.pref` must exist for the password to be readable**, because the
  key lives in it. Confirm afterwards:
  ```sh
  grep '^secret=' /var/lib/encore/.config/remmina/remmina.pref
  ```
- **The key is never shipped and never shared.** It is created on the terminal
  during this step, confirmed on 2026-09-23. Nothing secret has to be copied
  between machines, and every terminal ends up with its own key rather than all
  of them sharing one.

> **Stated plainly:** the stored password is recoverable by anyone who can read
> these two files, because the key sits beside the secret. Use a connection
> account that can do nothing but reach a login screen.

### 6. The files from this repository

```sh
install -m 755 encore-kiosk.sh /usr/local/bin/encore-kiosk.sh
install -m 644 encore-kiosk.service encore-kiosk.target /etc/systemd/system/

systemctl daemon-reload
systemctl enable encore-kiosk.service
```

### 7. Switch it on

```sh
systemctl isolate encore-kiosk.target
```

Or permanently, from the next boot:

```sh
systemctl set-default encore-kiosk.target
reboot
```

### 8. Undoing it by hand

`encore-uninstall.sh` does all of this. Reach the machine over SSH, or from a
text console — `Ctrl+Alt+F1` through `F6`, whichever one answers on your
machine. The screen itself belongs to the session.

```sh
systemctl set-default graphical.target   # or multi-user.target
systemctl disable encore-kiosk.service
rm /etc/systemd/system/encore-kiosk.service /etc/systemd/system/encore-kiosk.target
rm /usr/local/bin/encore-kiosk.sh
systemctl daemon-reload
userdel -r encore          # deletes the profile, the key and the stored password
rm -rf /var/lib/encore
reboot
```

Confirming that this really gives the machine back is Test 4.

---

## What to test, and what to write down

The tests are in `docs/tests.md`, each with what has actually been watched and
what has only been assumed. Run them in order; the status column there is the
honest record and this file does not duplicate it.

Two have answers so far. A session appearing has been watched twice, most
recently on a clean machine built by `encore-install.sh`. And the encryption key
does **not** have to travel between machines — it is created on the terminal, so
nothing secret is copied and every terminal holds its own. The rest have never
been run, including the one that asks whether you really get the machine back.

If something fails, `docs/troubleshooting.md` lists every failure seen so far,
with the check that identifies it and what turned out to be wrong. Nearly all
of them were silent — no error, no log line — so the order of checks matters
more than usual.

Two things to know before you start:

- **`systemctl status` will lie.** The runner loops forever, so the service
  reports `active (running)` whatever is happening. Read the journal — and read
  it by identifier:

  ```sh
  journalctl -t encore-kiosk -b --no-pager
  ```

  **`-u encore-kiosk.service` does not work here** and fails quietly, returning
  systemd's own start and stop lines and nothing the capability wrote. The
  processes are moved into a login session's own cgroup, which is what `-u`
  matches on; `docs/troubleshooting.md` has the full reason.
- **Debug over SSH, not through the terminal's screen.** When the kiosk wedges,
  the screen is the one thing you cannot use.

---

## Known issues

Detail for every one of these is in `docs/architecture/debt.md`, and the order
they get fixed in is `BACKLOG.md`.

1. **A terminal that has stopped working reports itself healthy.** Watched on
   2026-09-23: the connection failed, a dialog went up on the terminal's
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
8. **It has barely run on real hardware.** One converted Mac Mini, since
   2026-09-27. Everything before that was a virtual machine, and nothing older
   or stranger than that Mac Mini has been tried.
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
    `docs/troubleshooting.md` finds the cause on your machine, under *The
    session takes a very long time to appear at boot*.

---

## Where everything is written down

| Where | What |
|---|---|
| `docs/product/` | What the product is for, who it serves, what was decided |
| `docs/product/alternatives.md` | Why not one of the existing thin-client projects |
| `docs/architecture/` | How it is built, and why it is shaped this way |
| `docs/architecture/debt.md` | Everything known to be wrong, worst first |
| `docs/other-machine.md` | What to set up on the machine terminals connect to |
| `docs/tests.md` | What to run on a converted machine, and what has been watched |
| `docs/troubleshooting.md` | Every failure seen so far, and what caused it |
| `BACKLOG.md` | What order it gets fixed in |
| `LICENSE` | Apache License 2.0 — the terms you get this under |

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

