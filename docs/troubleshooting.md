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
ls /usr/lib/*/remmina/plugins/ | grep -i secret
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
| `/usr/bin/… is missing` | the sound packages are not installed. `apt install pipewire pipewire-pulse wireplumber` |
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

## The shape of a good debugging session here

1. SSH in. Never debug through the terminal's own screen.
2. Read the journal by identifier — `-t encore-kiosk`, not `-u`, and not
   `systemctl status`.
3. If there is no output at all, suspect waiting, not crashing.
4. Check whether the session is active before anything else.
5. Change one thing, and write down whether it mattered — including when it
   did not. `ProtectHome` was commented out early and nobody remembered
   whether it had mattered until it was tested again hours later.
