# The other machine

**Nothing in this file is part of Encore, and nothing in it runs on a terminal.**
It all goes on the machine your terminals connect to.

Encore changes nothing there and makes no claims about it. But converting a
machine creates these three problems on the far end, and none of them announces
itself — so they are written down here rather than left for you to find.

Do these once, after your first terminal is working.

**If you set these up before 2026-10-05, redo number 2.** The rule published here until then granted updates to every user rather than refusing them, and it is still in effect wherever it was applied.

## Contents

| # | What | Symptom if you skip it | Effort |
|---|---|---|---|
| 1 | [Take the power controls away from the session](#1-take-the-power-controls-away-from-the-session) | Someone at a terminal switches off the machine every terminal depends on | One file |
| 2 | [Stop the software updater asking for a password](#2-stop-the-software-updater-asking-for-a-password) | A password box nobody at the terminal can answer, over and over. **And if you used the version of this rule from before 2026-10-05, every user can apply system updates with no password** | One file |
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

**Corrected 2026-10-05, and the correction matters.** The rule printed here
until that date returned `YES`, which **granted every user — not just
administrators — the right to apply system updates with no password.** The text
beside it said "nothing extra is granted", which was true in the authorisation
service's own terms and badly misleading in plain ones. Found by the author
asking the obvious question: *"updates will NOT be executed for regular users,
correct?"* The answer was no, and the old rule is the reason.

**If you applied the old version, replace the file.** It is a grant, not a
refusal, and it is still in effect on any machine that has it.

### What is wrong on an untouched machine

A session arriving over the network is **not a *local* session** as far as the
authorisation service is concerned — the system's own rules test for that
explicitly. So things that happen silently for somebody sitting at the keyboard
stop and ask for an administrator password instead.

Three separate update systems do this, and a desktop drives all three:

| Family | Updates what | Easy to forget? |
|---|---|---|
| `packagekit` | the system's own packages | no |
| `Flatpak` | applications | no |
| **`fwupd`** | **firmware** | **yes — this is the one that gets missed** |

The catalogue also refreshes itself on a timer. In a terminal's session that
becomes a password box, repeatedly, in front of somebody who cannot answer it.
**Observed here six times over three days before anyone noticed.**

### The rule

As root on the machine being connected to:

```sh
cat > /etc/polkit-1/rules.d/20-no-update-prompt.rules <<'EOF'
// Deny updates to everyone outside wheel, and say nothing about wheel.
//
// NO, not auth_admin: a password box leaves the button on screen and offers
// something they cannot answer, which is the trap rather than the cure. NO
// makes the session hide or grey the entry. Same reasoning as rule 1.
//
// wheel gets NO VERDICT AT ALL -- the function returns nothing, so the
// authorisation service uses each action's own default: silent at the
// keyboard, asks over the network. That is out-of-the-box behaviour.
// Returning YES for wheel would be wrong: it would make an administrator
// update silently over the network, which is not the default. The version of
// this rule shipped before 2026-10-05 returned YES for EVERYBODY.
//
// NOT LISTED, therefore still needing an administrator for everyone including
// wheel: install, reinstall, remove, uninstall, downgrade, repository
// configuration, signing keys, install-bundle, repair-system, and every
// org.rpm.dnf.v0.* action. Parental controls are deliberately absent.
// packagekit.upgrade-system is already allow_any=no, so nobody reaches it
// over the network and it needs no line here.
polkit.addRule(function(action, subject) {
    if ((action.id == "org.freedesktop.Flatpak.app-update" ||
         action.id == "org.freedesktop.Flatpak.appstream-update" ||
         action.id == "org.freedesktop.Flatpak.metadata-update" ||
         action.id == "org.freedesktop.Flatpak.runtime-update" ||
         action.id == "org.freedesktop.Flatpak.update-remote" ||
         action.id == "org.freedesktop.fwupd.refresh-remote" ||
         action.id == "org.freedesktop.fwupd.update-hotplug" ||
         action.id == "org.freedesktop.fwupd.update-hotplug-trusted" ||
         action.id == "org.freedesktop.fwupd.update-internal" ||
         action.id == "org.freedesktop.fwupd.update-internal-trusted" ||
         action.id == "org.freedesktop.packagekit.clear-offline-update" ||
         action.id == "org.freedesktop.packagekit.system-sources-refresh" ||
         action.id == "org.freedesktop.packagekit.system-update" ||
         action.id == "org.freedesktop.packagekit.trigger-offline-update" ||
         action.id == "org.freedesktop.packagekit.trigger-offline-upgrade") &&
        !subject.isInGroup("wheel")) {
        return polkit.Result.NO;
    }
});
EOF
```

**Check the group name before you run this.** `wheel` is the administrators'
group on Fedora and RHEL. On Debian and Ubuntu it is `sudo`:

```sh
getent group wheel sudo
```

### What this gives you

| | Outside `wheel` | In `wheel` |
|---|---|---|
| Apply updates | **refused, with nothing on screen** | the default — silent at the keyboard, asks over the network |
| Install, remove, configure repositories | needs an administrator | needs an administrator |

**Nobody updates that machine from a remote session.** You update it at its own
keyboard, or over SSH. For a machine every terminal in the house depends on,
that is the right way round.

### Then verify it

```sh
sudo -u <a-non-admin-user> busctl call org.freedesktop.PackageKit \
  /org/freedesktop/PackageKit org.freedesktop.PackageKit \
  CanAuthorize s org.freedesktop.packagekit.system-update
```

- `"no"` — it worked.
- `"challenge"` — the rule is not firing. See the `grep` in rule 1: files are
  read in filename order and **the first one to answer wins**, so an older rule
  of your own silently beats this one.

**Do not judge this by looking at the menu.** A session asks once and remembers
the answer, so log that person out and back in first.

### One thing to watch, which is genuinely unresolved

This rule **refuses the metadata refreshes too** — the background catalogue and
firmware checks, not just the act of updating. That is deliberate: somebody who
cannot update has no use for a refreshed list.

**But nobody has watched what the desktop does about it.** The earlier version of
this page argued that refusing a refresh would swap one password box for repeated
failure messages, which is no better. That argument may still be right.

So after applying this, log into that person's session, open the software
application, and wait:

- **Quiet, with no updates offered** — this is finished.
- **Error banners** — move the five refresh actions
  (`Flatpak.appstream-update`, `Flatpak.metadata-update`, `Flatpak.update-remote`,
  `fwupd.refresh-remote`, `packagekit.system-sources-refresh`) into a second rule
  that returns `YES` for everybody. They change nothing on the machine.

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
