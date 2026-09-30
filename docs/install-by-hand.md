# What the installer does, step by step

`encore-install.sh` does all of this for you. **Follow the README instead unless
you have a reason not to.**

This file exists for two other readers: somebody debugging an install that
failed halfway, who needs to know what the script was trying to do; and somebody
deciding whether to trust this on their machine, who would rather read the steps
than the shell.

Every step here has gone wrong at least once, and the notes say how.

**Warning.** This is a second description of what one script already does, so it
can drift from the script without anything noticing — and it has. **When they
disagree, `encore-install.sh` is right and this file is stale.**

Everything below runs as root on the machine being converted.

## Contents

1. [Packages](#1-packages)
2. [The user the terminal runs as](#2-the-user-the-terminal-runs-as)
3. [Directories](#3-directories)
4. [The connection profile](#4-the-connection-profile)
5. [The password, and the key that protects it](#5-the-password-and-the-key-that-protects-it)
6. [The files from this repository](#6-the-files-from-this-repository)
7. [Switch it on](#7-switch-it-on)
8. [Undoing it by hand](#8-undoing-it-by-hand)

---

## 1. Packages

```sh
apt update
apt install remmina remmina-plugin-rdp cage kbd \
            pipewire pipewire-pulse wireplumber
```

**`kbd` provides `chvt`**, which the unit uses to bring the kiosk's console to
the front. Without it the service starts and nothing appears.

**The three sound packages are the sound server the runner starts for itself**
inside the kiosk session. A minimal install may not carry them, and without them
the terminal is silent.

## 2. The user the terminal runs as

```sh
useradd --system --create-home --home-dir /var/lib/encore \
        --shell /usr/sbin/nologin encore
usermod -aG video,input,render encore
```

> **One note.** Nobody has checked which of those group memberships are actually
> needed — narrow them once it works (backlog item 7).

## 3. Directories

**Every level is created explicitly, one at a time.** This looks redundant and
is not:

```sh
for d in /var/lib/encore/.local \
         /var/lib/encore/.local/share \
         /var/lib/encore/.local/state \
         /var/lib/encore/.local/share/remmina \
         /var/lib/encore/.config \
         /var/lib/encore/.config/remmina; do
    install -d -o encore -g encore -m 700 "$d"
done
```

**`install -d` applies `-o`, `-g` and `-m` to the last component only.** Any
ancestor it creates on the way is left root-owned and `0755`. Creating just the
two leaf directories therefore leaves the terminal unable to write into its own
home, and **the failure is silent** — a directory the terminal cannot write into
looks exactly like one it has not needed yet.

Check it, because nothing else will:

```sh
for d in /var/lib/encore/.local /var/lib/encore/.local/share \
         /var/lib/encore/.local/state /var/lib/encore/.config; do
    stat -c '%U %n' "$d"
done
```

Every line must say `encore`.

## 4. The connection profile

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

**Sound is one word away from going to the wrong house.** The profile must say
`sound=local`. `sound=remote` sends the terminal's session audio to the *other*
machine — one person's noise in another person's room. The installer refuses to
continue if this is wrong; by hand, nothing checks it but you:

```sh
grep '^sound=' /var/lib/encore/.local/share/remmina/encore-kiosk.remmina
```

**Put exactly one profile in that directory.** The runner takes the first file
it finds in no defined order, so two profiles mean an unpredictable target.

## 5. The password, and the key that protects it

```sh
 systemd-run --pty --uid=encore \
  -p InaccessiblePaths=/usr/lib/x86_64-linux-gnu/remmina/plugins/remmina-plugin-secret.so \
  -E HOME=/var/lib/encore \
  remmina --update-profile /var/lib/encore/.local/share/remmina/encore-kiosk.remmina \
          --set-option password='<password>'
```

**Check the plugin path matches your architecture.** It is
`aarch64-linux-gnu` on a 64-bit Pi and `arm-linux-gnueabihf` on a 32-bit one.

**Only the password is set here.** `server` and `username` were set in the file
at step 4 and survive this command untouched. Setting the username again on the
command line would mean two sources for one value, and the command line wins
silently when they disagree.

Note the **leading space**, which keeps the password out of your shell history.

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
  `remmina-plugin-secret.so` it insists on a keyring, and an unattended terminal
  has nobody to unlock one. The `InaccessiblePaths` above hides it for that one
  command; the service unit does the same permanently.
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
> those two files, because the key sits beside the secret. Use a connection
> account that can do nothing but reach a login screen.

## 6. The files from this repository

```sh
install -m 755 encore-kiosk.sh /usr/local/bin/encore-kiosk.sh
install -m 644 encore-kiosk.service encore-kiosk.target /etc/systemd/system/

systemctl daemon-reload
systemctl enable encore-kiosk.service
```

## 7. Switch it on

```sh
systemctl isolate encore-kiosk.target
```

Or permanently, from the next boot:

```sh
systemctl set-default encore-kiosk.target
reboot
```

**`isolate` is for a quick try and does not reproduce boot conditions** — it
switches over immediately, tearing down the desktop under you.

**One thing the script records and a hand install does not.**
`encore-install.sh` writes what the machine booted into *before* conversion, to
`/var/lib/encore/encore-install.conf`, so the uninstaller can put it back years
later without anyone having to remember. Doing this by hand, write down what
`systemctl get-default` says **before** you change it.

## 8. Undoing it by hand

`encore-uninstall.sh` does all of this. Reach the machine over SSH, or from a
text console — `Ctrl+Alt+F1` through `F6`, whichever one answers on your machine.
The screen itself belongs to the session.

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

`remmina`, `cage`, `kbd` and the sound packages are left installed. They are
ordinary software and removing them could break something else.

Confirm it independently, rather than trusting the removal you just did:

```sh
id encore; ls -d /var/lib/encore; ls /etc/systemd/system/ | grep encore
systemctl get-default
```

**Confirming that this really gives the machine back is Test 4**, in
`docs/tests.md`, and it has never been run to completion.
