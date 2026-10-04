# Troubleshooting

Every failure seen on this project so far, with the check that identifies it
and what turned out to be wrong. Written on 2026-09-14, the day the prototype
first reached a remote session — all of these were hit that day, in roughly
this order.

The pattern worth learning from it: **nearly every failure here was silent.**
No error, no log line, no dialog. A thing that is stuck says nothing, and a
thing that is broken usually does. When there is no message at all, suspect
waiting rather than crashing.

---

## Before anything else

**Get in over SSH.** When the kiosk wedges, the screen is the one thing you
cannot use, and console switching may be frozen. Debugging a terminal through
its own screen wastes hours.

**`systemctl status` will lie to you.** The runner loops forever, so the
service reports `active (running)` no matter how badly it is going, and the
restart policy can never fire. Read the journal instead:

```sh
journalctl -t encore-kiosk -b --no-pager
journalctl -b --no-pager | tail -80          # everything, not just this capability
journalctl -b -u systemd-logind --no-pager   # seats and sessions
```

**`-t encore-kiosk`, and not `-u encore-kiosk.service`.** Asking by unit returns
only systemd's own start and stop lines — never the compositor, the client or
the runner's markers — and it returns them without complaint, so it reads like a
capability that logs nothing. The reason is `PAMName=login`: logind opens a
login session and moves the processes into a session scope under the user's
slice, and `journalctl -u` matches the cgroup a line was logged from, which by
then is `session-N.scope`. `PAMName=login` is what grants the seat, the runtime
directory and the device access that let the compositor take the screen at all,
so it is not going anywhere. `SyslogIdentifier=encore-kiosk` in the unit stamps
the identifier on the journal stream instead, which the processes keep across
the move — and it names the capability rather than the compositor, so it still
works if `cage` is ever replaced.

If a line you expect is missing from `-t` output, fall back to
`journalctl -b _COMM=cage --no-pager`, which catches anything writing through
the compositor's stream. Use it to confirm a suspicion, not as the everyday
query: it names an implementation detail that will one day be wrong.

---

## The session takes a very long time to appear at boot

**Symptom:** the machine boots, the screen sits on a text console or a blank
colour for a long time — minutes, not seconds — and then the remote login
screen appears on its own with nobody touching it. It is not broken. It is
late.

**The distinguishing fact:** during the wait, `journalctl -t encore-kiosk`
returns *nothing at all*. Not an error — nothing. The capability has not
started yet, so it has written nothing. A slow capability logs slowly; a
capability that has not started logs not at all, and that is what tells the two
apart.

**Check.** The delay is upstream of Encore, so ask the startup system what it
was doing:

```sh
systemd-analyze blame | head -20
systemd-analyze critical-chain encore-kiosk.service
```

The first ranks every unit by how long it took. The second shows what Encore
was queued behind, with the time each unit became active after the `@`.

**Read `critical-chain` with care: it prints one path only.** Where several
units must finish before the same target, it shows one of them and says nothing
about the others — so the unit that actually cost the time can be absent from
the output entirely. Trust `blame` for *what was slow* and `critical-chain` for
*what Encore waited on*; neither answers both.

**Cause:** whatever `blame` puts at the top. `encore-kiosk.service` is ordered
after `network-online.target`, so anything holding that target back holds the
terminal back with it, second for second.

**Fix:** correct the slow unit. There is no general answer, because the cause is
a property of the machine rather than of this product.

### The one instance seen so far

Observed on a converted Mac Mini, 2026-09-30. Boot at 09:40:02, capability
started at 09:42:10 — **two minutes and eight seconds of nothing**, then a
session on screen 4.5 seconds later. The capability itself was never slow.

```
2min 197ms systemd-networkd-wait-online.service
   49.168s NetworkManager-wait-online.service
```

Both network stacks were installed and enabled. `systemd-networkd` managed no
interface on that machine — NetworkManager owned the WiFi — and its wait service
requires *at least one* link it manages to come online. Zero can never satisfy
one, so it waited out its built-in 120-second timeout, failed, and boot carried
on regardless.

**A suspiciously round number is the clue.** Software does not wait 120.197
seconds by accident; that is a timeout, not a hang.

Establish it with:

```sh
systemctl is-enabled systemd-networkd-wait-online.service NetworkManager-wait-online.service
networkctl list
```

Two `enabled` lines and a `SETUP` column reading `unmanaged` on every row is the
proof: one stack is waiting on interfaces the other one owns.

The fix is to remove the stack that manages nothing — not to mute its
complaint:

```sh
sudo systemctl disable --now systemd-networkd.service systemd-networkd.socket
```

Reverse it with `systemctl enable --now` on the same two units, then
`netplan apply`.

**Never `mask` `systemd-networkd.service`.** `netplan apply` crashes on a masked
unit and can take the network down with it; `disable` is recoverable and `mask`
is not. Masking `systemd-networkd-wait-online.service` alone is harmless, but it
silences a symptom and leaves the wrong stack running.

**Which stack owns the machine decides which one to remove**, so check before
acting. Files named `90-NM-*.yaml` in `/etc/netplan/` are written by
NetworkManager and mean it is the one in charge. A `renderer:` line names it
explicitly — but read every file, because netplan defaults to `networkd` where
none is given, and a `.dpkg-backup` suffix means the file is ignored entirely.

**Two things this is not.** It is not a defect in Encore, and nothing here is
changed by installing or removing it. And it has nothing to do with the screen
being off at boot, which is what it was mistaken for — see the note under
*Nothing on screen, nothing in the log*.

---

## Nothing on screen, nothing in the log

**Symptom:** the service starts, the journal shows the unit started and a PAM
session opened, and then nothing. No picture. Switching consoles freezes.
Stopping the service hangs.

**Check:**

```sh
loginctl list-sessions
loginctl show-session <id> -p Active -p VTNr -p Seat
```

**Cause:** `Active=no`. The capability opened its session on a console that is
not the one in the foreground. A compositor is only granted the screen and
input devices when its session is the active one on the seat, so it waits — for
ever, and silently. It has already claimed the console by then, which is why
switching away freezes and stopping hangs.

**Fix:** make the capability's console the foreground one before the compositor
starts, or put the capability on the console that is already in front. The unit
currently does the first with `ExecStartPre=+/usr/bin/chvt 7`. Which console it
should use, and whether hardcoding one is right at all, is an open handoff to
the architect.

**Note:** a seat has exactly one active session. If you are logged in at the
console yourself, the kiosk's session cannot be active. This is easy to cause
accidentally while debugging.

## Service fails at startup, complains about a runtime directory

**Check:** with the service running,

```sh
PID=$(pgrep -f 'cage -s')
sudo ls -l /proc/$PID/root/run/user/    # what the service can see
ls -l /run/user/                        # what is really there
```

**Cause:** `ProtectHome=true` hides `/home`, `/root` **and `/run/user`** — and
`/run/user` is where the Wayland socket lives. The directory exists and is
invisible to the service.

**Fix:** currently the line is commented out, which costs confinement the
design intends to have (see backlog item 7). The likely replacement is to hide
only what matters, which does not touch the runtime directory:

```ini
InaccessiblePaths=-/home
InaccessiblePaths=-/root
```

## Stopping or restarting takes 90 seconds

**Cause:** the compositor does not answer the first, polite request to stop, so
systemd waits the full default timeout — with the console frozen for the whole
of it.

**Fix:** in the unit, under `[Service]` — **not `[Unit]`**, where it is
silently ignored:

```ini
TimeoutStopSec=10s
KillMode=mixed
```

Confirm it took:

```sh
systemctl show encore-kiosk.service -p TimeoutStopUSec
```

**To get out of a hang now:** Ctrl+C only stops you waiting, not the job.

```sh
sudo systemctl kill -s KILL encore-kiosk.service
sudo systemctl reset-failed encore-kiosk.service
sudo chvt 1
sudo kbd_mode -a -C /dev/tty1        # if the console is left in graphics mode
```

In a VM, rebooting is usually faster than fighting a wedged console.

## "XDG_RUNTIME_DIR is not set" when running the compositor by hand

**Cause:** an artefact of how it was run, not a fault in the product. `sudo`
does not open a login session, so nothing creates `/run/user/<uid>` or sets the
variable. The service is different — it opens a session and normally gets one.

**Fix:** supply one. Note the `env`, because `sudo -u user VAR=value cmd` makes
sudo treat `VAR=value` as the command name:

```sh
sudo env XDG_RUNTIME_DIR=/run/user/0 cage -d -s -- /usr/local/bin/encore-kiosk.sh
```

Or sidestep it entirely — the compositor only needs a private writable
directory:

```sh
sudo mkdir -m 700 /tmp/cagerun
sudo env XDG_RUNTIME_DIR=/tmp/cagerun cage -d -s -- /usr/local/bin/encore-kiosk.sh
```

## "libseat: could not take control of session: only owner of session may take control"

**Cause:** also an artefact of running by hand. The console's session belongs to
your login; a process running as another user is inside someone else's session,
and logind refuses. The two permission errors that follow it have the same
cause.

**Fix:** run the manual test as **yourself**, in **your own** session, on the
console you are logged into:

```sh
env XDG_RUNTIME_DIR=/run/user/$(id -u) cage -d -s -- remmina -k
```

Only the service opens a session owned by the service user, so a manual run can
clear the compositor of suspicion but can never reproduce the service's session.

## The compositor runs but prints nothing

**Cause:** if you started it from the same console you are reading, it switched
that console into graphics mode and wiped the text.

**Fix:** capture it, then read it over SSH:

```sh
sudo env XDG_RUNTIME_DIR=/tmp/cagerun cage -d -s -- /usr/local/bin/encore-kiosk.sh \
  > /tmp/cage.log 2>&1
```

## "unable to get secret service", or a prompt about a keyring

**Check:**

```sh
find /usr/lib /usr/lib64 -name 'remmina-plugin-secret.so' 2>/dev/null
```

**Cause:** the client's keyring plugin is installed, so it insists on a secret
service. A keyring needs a human to unlock it at login, and a terminal has
none. This blocks both storing and reading the password.

**Fix:** hide the plugin rather than uninstalling it, so the machine is left
unchanged and the capability is still reversible (R-11, D-007). The unit does
this permanently; a one-off command needs it too, because the unit's hardening
does not apply to a separate process:

```ini
InaccessiblePaths=-/usr/lib/x86_64-linux-gnu/remmina/plugins/remmina-plugin-secret.so
InaccessiblePaths=-/usr/lib/aarch64-linux-gnu/remmina/plugins/remmina-plugin-secret.so
InaccessiblePaths=-/usr/lib/arm-linux-gnueabihf/remmina/plugins/remmina-plugin-secret.so
```

### On Fedora this suppression does not work, and says nothing

**Known defect, found 2026-10-04, recorded as `D-A19`.** All three paths above
are Debian multiarch paths. Fedora puts the file at
**`/usr/lib64/remmina/plugins/remmina-plugin-secret.so`** — verified in
`remmina-plugins-secret-1.4.41-2.fc44`, where it is a separate package rather
than part of `remmina-plugins-rdp`.

**No path matches, and nothing reports it.** The leading `-` on each line tells
systemd to tolerate a missing path, which is correct for the two architectures a
given machine does not have — and is also what hides the case where *every* path
is wrong. The unit starts clean. The plugin loads. The keyring prompt comes
back, and the terminal waits for somebody to unlock a keyring.

**The check that was printed above this section had the same fault**, which is
why it is now a `find` over both directories. `ls /usr/lib/*/remmina/plugins/`
cannot match `/usr/lib64/...` — the glob needs a directory *inside* `/usr/lib`.
Tested against a mock tree holding both layouts on 2026-10-04: the old form
found the Debian file only and exited as though it had looked everywhere. **So
on Fedora the fix missed and the diagnostic agreed with it.**

Until `D-A19` is fixed, add the Fedora path by hand on a Fedora terminal:

```sh
sudo systemctl edit encore-kiosk.service
```

```ini
[Service]
InaccessiblePaths=-/usr/lib64/remmina/plugins/remmina-plugin-secret.so
```

Then `sudo systemctl daemon-reload` and restart the terminal.

## It prompts for a password even though one is stored

**Check:**

```sh
sudo grep '^secret=' /var/lib/encore/.config/remmina/remmina.pref
sudo grep -c '^password=' /var/lib/encore/.local/share/remmina/*.remmina
```

**Cause, one of two.** Either there is no `remmina.pref`, so there is no key and
the stored password cannot be decrypted. Or the key does not match the one the
password was encrypted with — which happens when a profile is copied from
another machine and its key is left behind.

There is **no error that names this.** A wrong key produces a garbage password,
which is sent and rejected like an ordinary wrong password.

**Fix:** set the password on the terminal itself rather than copying a profile
into place. See `README.md`, step 5.

## The prompt is behind the session window and cannot be reached

**Cause:** the compositor shows one window and offers no way to raise, move or
switch between them. Anything the client puts on screen — a credential prompt,
a certificate warning, a disconnect notice — can land behind the session and be
unreachable.

This is the cost of the single-window choice (ADR-0002) and it has no fix in
the unit. It is a design question recorded in `docs/product/NOTES.md`.

**What helps now:** launch flags that stop the client opening its own windows
at all:

```sh
remmina --enable-fullscreen --disable-toolbar --enable-extra-hardening -c "$PROFILE"
```

Check the spelling. A mistyped flag fails quietly and you get the plain client
back with no explanation.

## Nothing renders at all, and the machine is a VM

**Check:**

```sh
ls -l /dev/dri/
```

**Cause:** no graphics device. The compositor cannot run without one, and
nothing else you test means anything until it is there.

**Fix:** give the VM virtio-gpu. In GNOME Boxes, also note that console
switching hotkeys are handled by your host desktop and may never reach the
guest — send them through the Boxes menu, or switch from inside with `chvt`.

## A terminal with no sound

**Check, and it is one command:**

```sh
journalctl -t encore-kiosk -b | grep 'SOUND UNAVAILABLE'
```

**No output is an answer, not an absence of one.** The runner writes one of
`encore: sound: …` or `encore: SOUND UNAVAILABLE: …` on every path through its
sound code, so an empty result means the sound server came up and the fault is
further along: the client, the channel, the far end, or the speakers. Then:

```sh
journalctl -t encore-kiosk -b --no-pager | grep -iE 'rdpsnd|audin|pulse|sound'
```

**Any output from the first command is the cause, in one line.** The usual ones:

| The line says | Cause |
|---|---|
| `wireplumber … is too old` | below 0.5 there is no profile support, so the sound server cannot be run without a session bus. The terminal works and is silent. |
| `/usr/bin/… is missing` | the sound packages are not installed. On an apt machine `apt install pipewire pipewire-pulse wireplumber`; on a dnf machine `dnf install pipewire pipewire-pulseaudio wireplumber` — the PulseAudio shim is the one of the three whose name differs, and [`stack.md`](architecture/stack.md) keeps the full two-name table. |
| `no PulseAudio-protocol socket` | the server started and did not finish coming up. The helpers' own complaints are above the line, in the same journal. |
| `has no output device` | the server is running and the machine presented no sound output at all. Suspect the hardware or its driver. |
| `XDG_RUNTIME_DIR is not set` | the session did not get a runtime directory. That contradicts how the unit is understood to work and is worth reporting rather than working around. |
| `whether a sound server is listening … could not be established` | a socket is there and the check could not ask it anything, so no server was started beside one that may be working. Almost always a missing `python3`: run `command -v python3`. Without it, a restarted terminal is silent — which is what it did before this check existed, now said out loud. |
| `a PipeWire server is already listening … but nothing is listening on … pulse/native` | half a sound server, started by something that is not this capability. The helpers were deliberately not started beside it. Nobody has ever seen this state; it is worth reporting with `pgrep -u encore -a pipewire` and `ls -la /run/user/$(id -u encore)`. |
| `a dead socket … could not be removed` | the runtime directory is not writable by the terminal's own identity, which should be impossible. Check `ls -la /run/user/$(id -u encore)/pulse`. |

**One `sound:` line is informational and not a fault**, though it reads like
one: `the socket at … was left by a session that has ended and nothing is
listening on it; removing it`. It means the terminal restarted, found the
previous session's socket, established that nothing was behind it, and cleared
the way. Expect it on every restart, and expect `sound: server ready` right
after. Before backlog item 5c that path reported success and started no server,
so the terminal was silent while the journal looked healthy — if you see the
removal line **without** `server ready` following it, that is the fault, not the
removal.

**Expected noise, and it is not a fault.** With no session message bus — which
is deliberate (R-16, D-012) — the sound server complains on every start about
rtkit, the desktop portal, mpris, bluez and libcamera. Those lines are the
normal shape of running without a bus. One real consequence hides among them:
realtime scheduling is unavailable without the system bus, which may mean audio
that stutters on old hardware. That is the first thing to suspect if sound works
but is rough.

**Sound was there and stopped.** Sound follows the active session on the seat,
so switching to a text console and back leaves the terminal's session without
it. Restart the terminal. This is known and accepted (D-034), and nothing
watches for it afterwards — every check above runs at startup only.

---

## Which certificate is the target presenting?

**Check:**

```sh
python3 ~/encore-probe.py <host>
```

It prints the SHA-256 fingerprint of the certificate that host presents for
RDP, in the exact form FreeRDP compares with, and says on stderr what it saw.

It needs **no credentials, no graphical session and no root** — the certificate
arrives during TLS, before authentication, so the probe never asks for a
password and never reads the profile. Run it over SSH while the terminal's own
screen is doing whatever it is doing.

If it cannot get a fingerprint it exits with a status saying why, so a script
can tell "nothing is listening" from "the certificate is not the one we
pinned". **`--help` is the authority on those statuses** — read it there rather
than trusting a copy:

```sh
python3 ~/encore-probe.py --help
```

Add `--port` if the target is not on 3389, and `--expect <fingerprint>` to ask
whether a particular fingerprint is the one being presented.

---

## Something is broken and the machine enforces SELinux

Mostly Fedora and its relatives. Debian, Ubuntu and Raspberry Pi OS do not
enforce SELinux, so this whole section is silent on those.

```sh
getenforce
```

**`Enforcing` on its own tells you nothing.** It is the normal state of a
healthy Fedora machine, and the product's arrangement is permitted there — see
below. Do not start changing policy because this printed `Enforcing`.

### Rule it in or out in one step

This is the only check here that cannot mislead you:

```sh
sudo setenforce 0        # reproduce the fault now
sudo setenforce 1        # put it back, always
```

- **Behaviour changes** — SELinux is involved. Go to the denial log.
- **Behaviour is identical** — SELinux is not your problem. Stop here and look
  elsewhere in this file.

Neither command edits policy and both are reversible. `setenforce 0` lasts until
reboot, so a forgotten `setenforce 1` is not permanent — but put it back anyway.

### Reading the denials

```sh
journalctl -b -g 'avc: *denied'
```

**This one needs no administrator** and was watched returning real denials on
2026-10-04. Prefer it.

The canonical tool needs root:

```sh
sudo ausearch -m AVC,USER_AVC,SELINUX_ERR,USER_SELINUX_ERR -ts boot
```

**Keep the `sudo`.** `/var/log/audit` is `0700 root:root`. Without it the
command prints `Error opening /var/log/audit/audit.log (Permission denied)` and
exits `1` — measured 2026-10-04 on Fedora 44 with `auditd` running. That is a
clear failure rather than a quiet one, so it will not fool you, but you learn
nothing about denials from it either.

**An empty denial log is not proof.** The policy carries `dontaudit` rules that
suppress denials with no log line at all — over a hundred reaching each of the
domains this product's session can land in. If `setenforce 0` changed the
behaviour but nothing is logged, that is the reason:

```sh
sudo semodule -DB        # turn the suppressions off
# reproduce, then read the log again
sudo semodule -B         # put them back
```

`journalctl -t setroubleshoot` is suggested by many guides and produces nothing
on a stock Fedora — `setroubleshoot-server` is not installed by default.

### What is already known

**The product's own arrangement is permitted under enforcing SELinux**, measured
against the live kernel on Fedora 44 on 2026-10-04: the identity's home under
`/var/lib/encore`, the `PAMName=login` session, the unit file, and the script in
`/usr/local/bin` all carry labels the policy accepts, and the transition is
allowed even with `NoNewPrivileges=`. **The installer needs no SELinux step.**
`docs/architecture/constraints.md` holds the measurements.

**Do not relabel `/var/lib/encore` to a home type.** Specifically, do not run
`semanage fcontext -a -t user_home_dir_t "/var/lib/encore(/.*)?"`. That is the
one change known to be able to break a working terminal: it hangs a home label
off a parent that is not a home root. The default label is already correct.

**Nothing has been watched on a Fedora terminal yet.** Everything above is
policy and labelling, not a running terminal. `R-1` is `intended` for the dnf
family for exactly this reason. If you are converting a Fedora machine, the
`setenforce 0` / `setenforce 1` comparison above on a first boot is the thing
that would settle it — and the record would like to hear the result.

## The shape of a good debugging session here

1. SSH in. Never debug through the terminal's own screen.
2. Read the journal by identifier — `-t encore-kiosk`, not `-u`, and not
   `systemctl status`.
3. If there is no output at all, suspect waiting, not crashing.
4. Check whether the session is active before anything else.
5. Change one thing, and write down whether it mattered — including when it
   did not. `ProtectHome` was commented out early and nobody remembered
   whether it had mattered until it was tested again hours later.
