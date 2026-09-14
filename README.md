# Encore — turn an old Linux machine into a kiosk terminal

Install this on an old computer and it becomes a terminal: the screen shows a
remote desktop session and nothing else. Switch it off and you get the old
machine back.

> ## ⚠️ Prototype. Read this before installing.
>
> **First observed working on 2026-09-14, on a virtual machine.** One session,
> once. It has never run on real old hardware, and nothing has been observed
> surviving a reboot, a dropped connection, or a switch-off.
>
> There is no package and no configuration tool. Installation is copying files
> by hand and running one command.
>
> **Known defects, all documented in `docs/architecture/debt.md`:**
>
> 1. With no connection profile, the terminal starts the remote desktop
>    client's own application — a connection editor and a file chooser.
>    **Do not put this in front of a child yet.**
> 2. A terminal that has stopped working reports itself healthy.
> 3. Any dialog the client raises can end up behind the session window, where
>    nothing can reach it. The compositor has no way to switch windows.
> 4. A sandboxing protection had to be turned off to make it start at all, so
>    the terminal reaches more of its own filesystem than the design intends.
>
> This document is a lab procedure for the author, not an install guide for
> strangers. The reader-facing version is separate, later work (ADR-0006).

---

## Does your machine qualify?

| Needs | Why |
|---|---|
| **apt-family Linux** (Debian, Ubuntu, Raspberry Pi OS…) | The only package family supported |
| **Wayland** | `cage` is a Wayland compositor; there is no X11 path |
| **systemd** | The on/off switch is a systemd target |
| **A current release of the packages below** | No compatibility handling for older ones (D-024) |

No particular hardware is required — but "has a working Wayland driver" is the
part that actually decides it, and that has not been tested on anything old.

**You also need a second machine that already accepts RDP connections.** This
project does nothing to that machine and makes no claims about it (D-002).

**For a VM:** give it virtio-gpu, or Wayland will not start and you will debug
the wrong problem. Keep SSH access — when the kiosk wedges, the screen is the
one thing you cannot use.

---

## Install

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

Edit the three `CHANGEME` lines — `name`, `server`, `username`.

**Put exactly one profile in that directory.** The runner takes the first file
it finds in no defined order, so two profiles mean an unpredictable target.

### 5. The password, and the key that protects it

```sh
 systemd-run --pty --uid=encore \
  -p InaccessiblePaths=/usr/lib/x86_64-linux-gnu/remmina/plugins/remmina-plugin-secret.so \
  -E HOME=/var/lib/encore \
  remmina --update-profile /var/lib/encore/.local/share/remmina/encore-kiosk.remmina \
          --set-option username=<user> --set-option password='<password>'
```

Note the leading space, which keeps the password out of your shell history.

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
- **The key is never shipped and never shared** (D-025). Whether it can be
  created on the terminal, or has to come from the machine where the profile
  was built, is still open — see Test 6.

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

---

## Switch it off, and get the machine back

From a text console (`Ctrl+Alt+F2`) or over SSH, as root:

```sh
systemctl set-default graphical.target   # or multi-user.target
reboot
```

To remove it completely:

```sh
systemctl disable encore-kiosk.service
rm /etc/systemd/system/encore-kiosk.service /etc/systemd/system/encore-kiosk.target
rm /usr/local/bin/encore-kiosk.sh
systemctl daemon-reload
userdel -r encore          # deletes the profile, the key and the stored password
```

Nothing else on the machine was modified. **This has never been demonstrated —
confirming it is Test 4.**

---

## What to test, and what to write down

### Test 1 — does a session appear?

```sh
systemctl status encore-kiosk.service
journalctl -u encore-kiosk.service -b --no-pager
```

Observed working on 2026-09-14 in a VM. If nothing appears, check in this
order — each of these cost an evening once:

| Symptom | Check | Cause |
|---|---|---|
| No output at all, screen black, console switching freezes | `loginctl show-session <id> -p Active` | The kiosk's console is not in the foreground, so the compositor waits forever for a screen it is never given |
| Fails at startup, complains about a runtime directory | `ProtectHome` in the unit | It hides `/run/user`, where the Wayland socket lives. Currently commented out for this reason |
| Starts, then asks about a keyring | `ls /usr/lib/*/remmina/plugins/ \| grep secret` | The secret plugin is reachable |
| Connects, then prompts for a password | `grep '^secret=' …/remmina.pref` | No key, so the stored password cannot be decrypted |

### Test 2 — what happens when the connection drops?

With a session running, stop RDP on the other machine, or pull the network.

**Does the client disappear and retry, or stay on screen with its own error
dialog?** Upstream reports it does not exit on disconnect by default. If it
sits there, self-recovery does not happen at all and the person at the terminal
is looking at an application they should never see. **This answer decides how
defect 2 gets fixed — do not write that fix before running this.**

### Test 3 — what happens with no profile?

```sh
mv /var/lib/encore/.local/share/remmina/*.remmina /root/
systemctl restart encore-kiosk.service
```

Expect the client's own interface. **This is defect 1, confirmed by observation
on 2026-09-14.** Put the profile back afterwards.

### Test 4 — does the off-switch really give the machine back?

Follow *Switch it off* above and confirm you get your normal desktop with
nothing to repair by hand. Reversibility is still only a claim.

### Test 5 — is there any sound?

There will not be. The template sets `sound=off`. Two-way audio is decided
(D-009, D-014) and unbuilt.

### Test 6 — must the encryption key travel?

Delete `remmina.pref` on the terminal, re-run step 5, and see whether a working
key is created locally. If it is, nothing secret ever has to be copied between
machines. If it is not, every terminal shares one key and the promise in R-14
shrinks. **Open question — see `docs/product/NOTES.md`.**

---

## Where everything is written down

| Where | What |
|---|---|
| `docs/product/` | What the product is for, who it serves, what was decided |
| `docs/product/alternatives.md` | Why not one of the existing thin-client projects |
| `docs/architecture/` | How it is built, and why it is shaped this way |
| `docs/architecture/debt.md` | Everything known to be wrong, worst first |
| `BACKLOG.md` | What order it gets fixed in |

---

*This file documents the prototype as it stands, for someone debugging it. The
version aimed at a stranger deciding whether to spend an evening on this is
separate, later work.*
