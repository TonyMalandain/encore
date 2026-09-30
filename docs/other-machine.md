# The other machine

**Nothing in this file is part of Encore, and nothing in it runs on a terminal.**
It all goes on the machine your terminals connect to.

Encore changes nothing there and makes no claims about it. But converting a
machine creates these three problems on the far end, and none of them announces
itself — so they are written down here rather than left for you to find.

Do these once, after your first terminal is working.

## Contents

| # | What | Symptom if you skip it | Effort |
|---|---|---|---|
| 1 | [Take the power controls away from the session](#1-take-the-power-controls-away-from-the-session) | Someone at a terminal switches off the machine every terminal depends on | One file |
| 2 | [Stop the software updater asking for a password](#2-stop-the-software-updater-asking-for-a-password) | A password box nobody at the terminal can answer, over and over | One file |
| 3 | [Check the machine can encode video](#3-check-the-machine-can-encode-video) | **Each terminal costs ~130 Mbps instead of a few** — and nothing tells you | One package |

**Number 3 is the one to do first if you only do one.** The other two are
visible the moment they happen. This one is invisible, costs a hundredfold, and
no log an adopter would think to read mentions it.

---

## 1. Take the power controls away from the session

A terminal fills its screen with the other machine's session — so that session's
**Power Off** and **Restart** end up in front of whoever is sitting at the
terminal. Those buttons belong to the machine every terminal in the house
depends on.

Someone finishing at a terminal reaches for Power Off, because that is what you
do when you have finished with a computer. **Log Out** is the action they
actually want: it returns the terminal to the remote login screen, which is
where a terminal should sit.

### First, look for a rule you already have

Skip this step and it will cost you an evening.

```sh
sudo grep -rl "login1" /etc/polkit-1/rules.d/
```

Rules are read in filename order and **the first one to answer wins**. A rule
you wrote months ago silently beats one you add today. The symptom is "I added
the rule and nothing changed", and nothing in any log says why — because a rule
that is never reached looks exactly like a rule that is broken.

**If that command prints a file, edit that file.** Do not add another.

### Then write the rule

As root, using the filename the command above found — or this one if it found
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

**Check the group name before you run this.** `wheel` is the administrators'
group on Fedora and RHEL. On Debian and Ubuntu it is `sudo`. Get it wrong and
the rule locks you out of your own machine's power menu:

```sh
getent group wheel sudo
```

### Then verify it

No restart is needed — polkit picks the file up by itself. Test against a
non-admin account:

```sh
sudo -u <someone> busctl call org.freedesktop.login1 /org/freedesktop/login1 \
  org.freedesktop.login1.Manager CanPowerOff
```

- `"no"` — it worked.
- `"challenge"` — the rule is not firing. Go back to the `grep` above.

**Do not judge this by looking at the menu.** A session asks once and remembers
the answer, so an open session shows the old state until the person logs out and
back in.

---

## 2. Stop the software updater asking for a password

The same quirk causes a second, noisier problem.

A session arriving over the network is **not a *local* session** as far as the
authorisation service is concerned — the system's own rules test for that
explicitly. So things that happen silently for somebody sitting at the keyboard
stop and ask for an administrator password instead.

The software catalogue refreshes itself in the background. In a terminal's
session that becomes a password box, repeatedly, in front of somebody who cannot
answer it. **Observed here six times over three days before anyone noticed.**

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

**This rule grants, where the one above refuses. That is deliberate.** Refusing
here would swap the password box for failure messages, which is no better.
Granting restores exactly what the person would have had sitting at the keyboard
— every action listed already defaults to `yes` for a local session, so nothing
extra is given away.

Installing, removing and configuring software still need an administrator, just
as they do locally.

**To check it:** open the software application in that person's session and let
it refresh. No password box means it worked.

**On parental controls:** this rule does not touch them, and the action that
overrides them stays locked by the system's own rule.

---

## 3. Check the machine can encode video

**A terminal's cost to your network is decided by the machine at the other end,
not by the terminal.**

A remote session is a video stream. If the serving machine can compress it in
hardware, a busy terminal costs a few megabits per second. If it cannot, the
session falls back to sending pictures of the screen — and the same terminal
costs **about 130 megabits per second**, measured here on 2026-09-29.

That matters because a household is expected to run two or three terminals:

| | One terminal | Three terminals |
|---|---|---|
| With hardware encoding | a few Mbps | fits on anything |
| Without | ~130 Mbps | **~400 Mbps at once** |

A cable carries 400 Mbps. Household wireless usually does not — and reused
machines tend to end up in bedrooms, which is exactly where the wireless is.

**Nothing tells you which one you have.** Not the terminal, not the installer,
not any log an adopter would think to read. The word "encoder" appears nowhere.

### Check it

On the machine being connected to:

```sh
vainfo | grep -iE 'H264.*EncSlice'
```

Install `libva-utils` first if that command is missing.

- You want `VAProfileH264Main` or `VAProfileH264High` alongside
  `VAEntrypointEncSlice`.
- **Nothing printed means your sessions are being sent as pictures.**

The serving software says the same thing in its own words when a terminal
connects:

```sh
journalctl --user -u gnome-remote-desktop -b | grep -i vaapi
```

A line about being unable to start hardware video is this fault, stated plainly.

### Fix it

**On Fedora this is one missing package, and it is not installed by default** —
video encoding is stripped from the standard graphics stack for patent reasons:

```sh
sudo dnf install mesa-va-drivers-freeworld
systemctl --user restart gnome-remote-desktop
```

**Restart the serving software after installing**, or it keeps running without
the new driver and nothing changes.

Other distributions ship encoding in their normal graphics packages. The check
above is what matters, not the package name.

### Measure your own

**Honest note on the numbers.** The 130 megabits per second is measured. The
figure *after* fixing it is not — no session had been observed at the time of
writing. Expect a large improvement rather than a specific number.

```sh
a=$(cat /sys/class/net/<interface>/statistics/tx_bytes); sleep 30
b=$(cat /sys/class/net/<interface>/statistics/tx_bytes)
awk -v d=$((b-a)) 'BEGIN{printf "%.1f Mbps\n", d*8/30/1e6}'
```

Two things or the readings do not compare:

- Play **the same thing** on the terminal before and after, for the same length
  of time.
- If that interface belongs to a bridge, read the real one. **A bridge and its
  member count the same bytes twice.**
