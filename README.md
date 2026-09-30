# Encore — turn an old Linux machine into a kiosk terminal

Install this on an old computer and it becomes a terminal: the screen shows a
remote desktop session and nothing else. Switch it off and you get the old
machine back.

You need a second machine that already accepts remote desktop connections —
the one the terminal will show. This project does nothing to that machine.

**Known issues are at the bottom.** Read them before you put a terminal in
front of anybody.

---

## Does your machine qualify?

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

## Recommended after it is working — on the *other* machine

**None of this is part of Encore, and none of it runs on the terminal.** It goes
on the machine the terminals connect to. Encore changes nothing there and makes
no claims about it — but converting a machine creates these problems, so they
are listed here rather than left for you to discover.

### Take the power controls away from the session

A terminal fills its screen with the other machine's session, so that session's
**Power Off** and **Restart** end up in front of whoever is sitting at the
terminal. They belong to the machine every terminal depends on.

Someone finishing at a terminal reaches for Power Off, because that is what you
do when you have finished with a computer. **Log Out** is the action they
actually want: it returns the terminal to the remote login screen, which is
where a terminal should sit.

**First, look for a rule you already have.** This is the step that will waste
your evening if you skip it:

```sh
sudo grep -rl "login1" /etc/polkit-1/rules.d/
```

Rules are read in filename order and **the first one to answer wins**. A rule
you wrote months ago will silently beat one you add today — the symptom is "I
added the rule and nothing changed", and nothing in any log says why, because a
rule that is never reached looks exactly like a rule that is broken. If that
command prints a file, edit that file rather than adding another.

Then, as root — using the filename that command found, or this one if it found
nothing:

```sh
cat > /etc/polkit-1/rules.d/20-no-poweroff.rules <<'EOF'
// Deny power-off, reboot, suspend and hibernate to everyone but admins.
//
// NO, not AUTH_ADMIN: asking for a password leaves the button on screen and
// offers a box they cannot answer, which is the trap rather than the cure.
// NO makes the session hide the entry, leaving Log Out — the action they want.
//
// Prefix match, so the -multiple-sessions and -ignore-inhibit variants are
// covered. Naming actions one by one misses four of them.
polkit.addRule(function(action, subject) {
    if (/^org\.freedesktop\.login1\.(reboot|power-off|halt|suspend|hibernate)/.test(action.id)
        && !subject.isInGroup("wheel")) {
        return polkit.Result.NO;
    }
});
EOF
```

`wheel` is the administrators' group on Fedora and RHEL. On Debian and Ubuntu it
is `sudo` — change it, or the rule locks you out of your own machine's power
menu. Check with `getent group wheel sudo`.

No restart is needed; polkit picks the file up by itself. Verify against a
non-admin account:

```sh
sudo -u <someone> busctl call org.freedesktop.login1 /org/freedesktop/login1 \
  org.freedesktop.login1.Manager CanPowerOff
```

`"no"` means it worked. `"challenge"` means the rule is not firing — go back to
the `grep` above. **Do not judge this by looking at the menu:** the session asks
once and remembers the answer, so an open session shows the old state until the
person logs out and back in.

### Stop the software updater asking for an administrator password

The same quirk causes a second, noisier problem. A session arriving over the
network is not a *local* session as far as the authorisation service is
concerned — the system's own rules test for that explicitly — so things that
happen silently for someone sitting at the keyboard stop and ask for an
administrator password instead.

The software catalogue refreshes itself in the background. In a terminal's
session that turns into a password box, repeatedly, in front of somebody who
cannot answer it. Observed here six times over three days before anyone noticed.

As root on the machine being connected to:

```sh
cat > /etc/polkit-1/rules.d/20-no-update-prompt.rules <<'EOF'
// A session over the network has subject.local == false, so actions that are
// free at the keyboard ask for an admin password instead. This restores the
// at-the-keyboard answer for the refresh actions only — every one of these
// already defaults to `yes` for a local session, so nothing extra is granted.
//
// Installing, uninstalling and configuring still need an administrator, exactly
// as they do locally. Parental-control actions are deliberately absent.
polkit.addRule(function(action, subject) {
    if (action.id == "org.freedesktop.Flatpak.metadata-update" ||
        action.id == "org.freedesktop.Flatpak.appstream-update" ||
        action.id == "org.freedesktop.Flatpak.app-update" ||
        action.id == "org.freedesktop.Flatpak.runtime-update" ||
        action.id == "org.freedesktop.Flatpak.update-remote") {
        return polkit.Result.YES;
    }
});
EOF
```

This one **grants** rather than refuses, which is the opposite of the rule above
and deliberate. Refusing would remove the password box and replace it with
failure messages. Granting restores what the person would have had at the
keyboard.

To check it, open the software application in that person's session and let it
refresh. No password box means it worked.

If you use parental controls on that machine, note that this rule does not touch
them, and the action that overrides them stays locked by the system's own rule.

### Check that machine can encode video — this one is worth a hundredfold

**A terminal's cost to your network is decided by the machine at the other end,
not by the terminal.** A remote session is a video stream. If the serving machine
can compress it in hardware, a busy terminal costs a few megabits per second. If
it cannot, the session falls back to sending pictures of the screen, and the same
terminal costs **about 130 megabits per second** — measured here on 2026-09-29.

That matters because a household is expected to run two or three terminals. At
the cheap rate they fit on anything. At the expensive rate three of them want
around 400 megabits per second at once, which a cable carries and household
wireless usually does not — and the machines being reused tend to end up in
bedrooms, which is where the wireless is.

**Nothing tells you which one you have.** Not the terminal, not the installer, not
any log an adopter would think to read. The word "encoder" appears nowhere.

Check it. On the machine being connected to:

```sh
vainfo | grep -iE 'H264.*EncSlice'
```

Install `libva-utils` first if that command is missing. You want to see
`VAProfileH264Main` or `VAProfileH264High` alongside `VAEntrypointEncSlice`.
**Nothing printed means your sessions are being sent as pictures.**

Also look at what the serving software says when a terminal connects:

```sh
journalctl --user -u gnome-remote-desktop -b | grep -i vaapi
```

A line about being unable to start hardware video is the same fault, stated
plainly.

**On Fedora this is one missing package, and it is not installed by default.**
Video encoding is stripped from the standard graphics stack for patent reasons:

```sh
sudo dnf install mesa-va-drivers-freeworld
systemctl --user restart gnome-remote-desktop
```

Restart the serving software **after** installing, or it keeps running without the
new driver and nothing changes. Other distributions ship encoding in their normal
graphics packages; the check above is what matters, not the package name.

**Honest note on the numbers.** The 130 megabits per second is measured. The
figure *after* fixing it is not — no session had been observed at the time of
writing. Expect a large improvement rather than a specific number, and measure
your own:

```sh
a=$(cat /sys/class/net/<interface>/statistics/tx_bytes); sleep 30
b=$(cat /sys/class/net/<interface>/statistics/tx_bytes)
awk -v d=$((b-a)) 'BEGIN{printf "%.1f Mbps\n", d*8/30/1e6}'
```

Play the same thing on the terminal before and after, for the same length of
time, or the two readings do not compare. And if that interface belongs to a
bridge, read the real one — a bridge and its member count the same bytes twice.

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

