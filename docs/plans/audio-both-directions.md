# Plan — audio in both directions, out of the box (`BACKLOG.md` item 5)

**Rewritten 2026-09-28.** The previous version of this file designed around
declaring the session type in the unit so `logind` would stop reducing the
session class. **That approach works and has been rejected by the author.**
Lifting the class also starts a session message bus and, through it, a
credential keyring, a file-system broker, a document portal, an SSH agent, a
speech service and a package-prompt client, all under the terminal's identity —
which breaches R-16 and D-012, and the package-prompt client can draw on the
screen, which threatens R-6. The three narrower variants the architect priced
are also dead: blocking the unwanted services was shown to fail silently on
exactly the two that matter, and declaring the session class `background`
changes nothing. **None of those may be revived by this ticket.** Everything
below is the replacement approach.

**Sensitive: this ticket turns on a microphone.** D-014's accepted cost is that
"every terminal becomes a live microphone in whichever room it sits in,
reachable by anyone signed in to a session on it". That is a decided cost, not
a new one — but it is the reason the input half of this plan is a separate,
later, individually-provable phase rather than a line in the same edit as the
output half. No credential is read, written or logged anywhere in this ticket.
No new group, capability, device rule or loosened sandbox is needed: the access
list on the sound control device already names `encore` (observed 2026-09-27).
**Do not add `encore` to the `audio` group.**

**Status of the evidence.** Exactly one set of measurements about the chosen
approach exists: the author's, on the test VM, on 2026-09-28, quoted verbatim
under *What is proven* below. Two smaller facts were measured while writing
this plan and are marked as such. **Everything else in this file is marked
`unknown` or `inference` and carries the command that would settle it. Nothing
here may be called confirmed, verified or observed until somebody runs the
command and writes the output into `docs/tests.md`.**

---

## What changes, and for whom

For the person at the terminal — the owner's child: sound from the remote
session comes out of the speakers in front of them, and, where the machine has
a microphone, the session hears them, so a call works. Nobody chooses a device
at either end. A terminal with no microphone stays fully usable.

For whoever converts a machine: nothing new to answer and nothing new to pick.
On a machine whose sound software is too old, the install still completes and
the terminal still works — it says once, on the screen the administrator is
looking at, that this machine will have no sound, and says the same thing in
the journal on every start.

For whoever has to diagnose a silent terminal: one command answers it.

```sh
journalctl -t encore-kiosk -b | grep 'SOUND UNAVAILABLE'
```

No output means the sound path came up. Any output is the reason it did not,
in one line. **It is `-t encore-kiosk` and never `-u encore-kiosk.service`**:
`PAMName=login` moves these processes out of the unit's cgroup, so asking by
unit matches nothing the runner wrote — and it does so silently, which makes a
`-u` query piped into `grep` read as a pass on every machine. Every query in
this document was corrected to `-t` on 2026-09-29. **That command is a
deliverable of this ticket, not a convenience** — it is the first piece of this project's oldest defect (a
terminal that has stopped working reports itself healthy, `README.md` known
issue 1) to be repaid anywhere.

---

## What is proven

The author, on the test VM, 2026-09-28. Started by hand from a root shell, with
no per-user service manager running for the terminal's identity:

```sh
U=$(id -u encore)
setsid sudo -u encore env XDG_RUNTIME_DIR=/run/user/$U /usr/bin/pipewire        </dev/null >/root/pw.log  2>&1 &
setsid sudo -u encore env XDG_RUNTIME_DIR=/run/user/$U /usr/bin/pipewire-pulse  </dev/null >/dev/null    2>&1 &
setsid sudo -u encore env XDG_RUNTIME_DIR=/run/user/$U /usr/bin/wireplumber -p main-embedded </dev/null >/root/wp.log 2>&1 &
```

- `pactl info` answered: `Server String: /run/user/997/pulse/native`,
  `User Name: encore`.
- `pactl list short sinks` showed the machine's **real** output,
  `alsa_output.pci-0000_00_1b.0.analog-stereo` — not a placeholder.
- The runtime directory gained **only** `pipewire-0`, `pipewire-0-manager`,
  their lock files, and `pulse`. **No `bus`, no `keyring`, no `gvfs`, no snap
  sockets** — which is the whole point: this is the result the rejected
  approach could not give.
- Versions on that machine: pipewire 1.6.2, wireplumber 0.5.13.

That is the entire evidential base. It proves **a sound server can exist for
this identity with no session bus and no per-user service manager**. It proves
nothing about the client using it, nothing about running it from inside the
kiosk session, and nothing about the microphone.

---

## The component

Three parts are touched, and it matters which owns what.

### `encore-kiosk.sh` — the runner

- **Responsible for:** choosing what runs inside the cage, and starting it.
- **Has drifted by:** it carries a retry loop (`while true; … sleep 2`) that
  ADR-0007 says belongs to systemd and `BACKLOG.md` item 12 will remove. That
  drift is **not repaired here** — see *Out of scope*. This plan is shaped so
  that removing the loop later is still a one-line change.
- **This change belongs here because:** the architect's constraint puts the
  helpers inside the kiosk's own PAM session, and this file is the only code
  that runs inside it. `/run/user/<uid>` exists only while a session for that
  identity exists, and this unit restarts as a matter of routine (R-18, D-020,
  D-026). A sibling system unit would be racing the runtime directory's
  existence on every reconnect. Inside the session the helpers start with it,
  die with it, and share its cgroup and its runtime directory.

The runner therefore grows a second job: **start three long-lived children,
prove they came up, and say loudly when they did not.** It is still one
responsibility — "get the thing on the screen, with what it needs" — but the
file doubles in size, and that is the honest shape of this ticket.

### `encore-kiosk.remmina.template` — the shipped profile

- **Responsible for:** the connection settings every terminal starts from.
- **Has drifted by:** nothing, but it carries a value nobody chose.
  `sound=off` is a property of the machine the working profile was copied from
  on 2026-09-14, carried along verbatim (`constraints.md` C-5 says this in the
  architecture's own words). Turning it on is this ticket's only product-visible
  change.

### `encore-install.sh` — setup

- **Responsible for:** turning a machine into a terminal, once, with the
  administrator standing there.
- **Has drifted by:** one real defect, found on the way and repaired here —
  see *Repair first*.

---

## Repair first — the directory chain the sound server cannot write into

**Behaviour-preserving. This lands before anything about audio.**

`encore-install.sh` (section *3. directories*) has:

```sh
install -d -o encore -g encore -m 700 "$HOME_DIR/.local/share/remmina"
install -d -o encore -g encore -m 700 "$HOME_DIR/.config/remmina"
```

**This was verified, not assumed, while writing this plan.** Measured locally
on GNU coreutils 9.10, under `fakeroot` so the ownership half was visible:

```
$ install -d -o 997 -g 997 -m 700 a/.local/share/remmina && ls -ldn a/.local a/.local/share a/.local/share/remmina
drwxr-xr-x 3   0   0 a/.local
drwxr-xr-x 3   0   0 a/.local/share
drwx------ 2 997 997 a/.local/share/remmina
```

`install -d` applies `-o`, `-g` and `-m` **only to the last component**.
Ancestors are created with the default mode and the invoking user's ownership —
so on a real install `/var/lib/encore/.local`, `/var/lib/encore/.local/share`
and `/var/lib/encore/.config` are **root-owned, mode 0755**, inside a home
directory the terminal's identity otherwise owns.

Consequence for this ticket: `wireplumber` keeps its state under
`$XDG_STATE_HOME`, which defaults to `$HOME/.local/state`. With `.local`
root-owned and not group- or world-writable, the terminal's identity cannot
create it. That is `inference` from the ownership above, not something anybody
watched — but it is a defect whether or not it is *this* ticket's defect, and
it is three lines to close.

Repair: create each level explicitly, and assert it, in the style the rest of
the file already uses.

```sh
for d in "$HOME_DIR/.local" "$HOME_DIR/.local/share" "$HOME_DIR/.local/state" \
         "$HOME_DIR/.local/share/remmina" \
         "$HOME_DIR/.config" "$HOME_DIR/.config/remmina"; do
    install -d -o encore -g encore -m 700 "$d"
done

# install -d applies ownership only to the final component, so the chain above
# is built one level at a time on purpose. Checked here because the failure is
# silent: a directory the terminal cannot write into looks exactly like one it
# has not needed yet.
for d in "$HOME_DIR/.local" "$HOME_DIR/.local/share" "$HOME_DIR/.local/state" \
         "$HOME_DIR/.config"; do
    [ "$(stat -c %U "$d")" = encore ] || die "$d is owned by $(stat -c %U "$d"), not encore"
done
```

**Behaviour change: none.** Nothing today reads or writes those three
directories; the two leaf directories keep the ownership and mode they already
had. Land it as its own change so the audio diff does not contain it.

---

## Seams

### The runner's one new seam, and it is a log line

Every audio-related line the runner writes begins with one of exactly two
prefixes, and nothing else in the system writes either:

```
encore: sound: <what happened>
encore: SOUND UNAVAILABLE: <why there is no sound, in one line>
```

**The misuse this makes impossible:** a sound path that fails and says nothing.
Every early return from `start_sound` writes a `SOUND UNAVAILABLE` line, and
there is no path out of the function that does not write one of the two
prefixes. That is what makes the single documented `grep` a complete answer
rather than a hopeful one, and it is why the prefix is a fixed string and not
prose.

### `start_sound` — exact shape

Shell has no signatures, so the seam is the contract. `start_sound` takes no
arguments, reads only `XDG_RUNTIME_DIR`, **always returns 0**, and appends the
PIDs it started to `HELPER_PIDS`.

**`start_sound` never fails the runner.** A terminal with no sound is a
terminal; a terminal that will not connect is not. R-12 loses to R-6 and R-8
every time, and this is where that is decided rather than left to the engineer.

```sh
HELPER_PIDS=

log() { printf 'encore: %s\n' "$*" >&2; }

stop_helpers() {
    [ -n "$HELPER_PIDS" ] || return 0
    # Deliberately unquoted: HELPER_PIDS is a space-separated list.
    kill $HELPER_PIDS 2>/dev/null || true
    HELPER_PIDS=
}

# Wait up to $2 seconds for $1 to exist. Returns 1 on timeout.
wait_for() { ... }

start_sound() { ... }     # always returns 0
```

`trap stop_helpers INT TERM EXIT` is set once, before `start_sound` is called.
**This is belt and braces, not the mechanism:** the helpers live in the unit's
cgroup, so systemd tears them down on stop and on every restart without being
asked. The trap exists so that a runner which exits on its own does not leave
three processes behind for the seconds before systemd notices. `KillMode=` is
**not** changed — that is item 9's and ADR-0007's ground.

### How the proven recipe is translated, and every deviation named

The author's recipe ran from a root shell. Four things in it exist only because
of that, and each is dropped for a stated reason. **The engineer does not get to
re-add them.**

| In the recipe | In the runner | Why |
|---|---|---|
| `sudo -u encore` | dropped | the runner is already `encore` (`User=encore`, `encore-kiosk.service:7`) |
| `env XDG_RUNTIME_DIR=…` | dropped; the value is **checked** instead | `PAMName=login` opens the session, so `pam_systemd` sets it and systemd imports the PAM environment. `cage` already depends on this being right — it creates its Wayland socket there. If the check ever fails, that is a finding, not something to paper over |
| `setsid` | dropped | it existed so the helpers would survive the root shell's `SIGHUP`. We want the opposite: they must die with the session. `setsid` also makes `$!` unreliable, because a backgrounded command is already a process-group leader, so `setsid` forks and `$!` is the parent that exits immediately |
| `>/root/pw.log`, `>/root/wp.log` | `>&2`, into the journal | a file under `/root` is outside everything `encore-uninstall.sh` removes and would breach R-11 (see *The uninstaller*) |

`</dev/null` is **kept**. The unit sets `StandardInput=tty` for `libseat`, and a
helper inheriting that tty can be stopped by `SIGTTIN`.

### Ordering, and why it is not the recipe's order

The recipe started all three back to back, which races: `pipewire-pulse` and
`wireplumber` both need `pipewire`'s socket. The runner waits for it.

1. check `XDG_RUNTIME_DIR` is set → else `SOUND UNAVAILABLE`, return
2. if `$XDG_RUNTIME_DIR/pulse/native` already exists → log `sound: a
   PulseAudio-protocol socket already exists; leaving it alone`, return.
   **This is what makes the change safe on a platform where the fault does not
   exist** — see unknown 4. Starting a second sound server beside a working one
   is the one way this ticket could break a machine that was fine.
3. check `/usr/bin/pipewire`, `/usr/bin/pipewire-pulse`, `/usr/bin/wireplumber`
   are all executable → else `SOUND UNAVAILABLE: <path> is missing`, return
4. check `wireplumber` is 0.5 or newer (below) → else `SOUND UNAVAILABLE`, return
5. start `pipewire`; wait up to 5s for `$XDG_RUNTIME_DIR/pipewire-0` → on
   timeout, `SOUND UNAVAILABLE`, `stop_helpers`, return
6. start `pipewire-pulse` and `wireplumber -p main-embedded`
7. wait up to 5s for `$XDG_RUNTIME_DIR/pulse/native` → on timeout,
   `SOUND UNAVAILABLE`, return (leave the helpers running — their own output is
   already in the journal and is the evidence)
8. `log "sound: server ready at $XDG_RUNTIME_DIR/pulse/native"`
9. best effort, only if `pw-dump` is on the machine: count nodes whose media
   class is `Audio/Sink`. **Zero sinks is logged as `SOUND UNAVAILABLE: the
   sound server is running but has no output device`.** Nothing branches on
   this number; it is the line that will diagnose old hardware, which is the
   cost D-009 accepted.

Five seconds is a guess, not a measurement, and it is the only new number in
the system. It is bounded on purpose: this delay is a black screen in front of
a child (`constraints.md` C-6). If Phase 1 shows the socket taking longer, the
number changes and the reason is written down.

### The wireplumber version gate — and it excludes the product's own floor

`wireplumber -p main-embedded` is the upstream profile for running with no
session bus and no login-session integration. **Profiles arrived in wireplumber
0.5. There is no `-p` flag at all in 0.4**, so on 0.4 the process exits
immediately with an unknown-option error.

**Measured while writing this plan:** Ubuntu 24.04 LTS ships wireplumber
**0.4.17** (`0.4.17-1ubuntu4.1` in `noble-updates`). Ubuntu 24.04 is the
*oldest Ubuntu this product says it supports* (`README.md`, "Does your machine
qualify?"). **So the chosen approach delivers no audio on the lowest supported
Ubuntu release.** Debian 13 and Raspberry Pi OS trixie carry 0.5.

This is a real, permanent hole in R-12 on a supported platform, and this plan
does not close it. What it does instead:

- the runner refuses to start a 0.5-only invocation on 0.4, and says so in one
  line with the version in it;
- the installer says the same thing once, on the screen, to the administrator
  who is standing there;
- `README.md` gains the qualification note, so a prospective adopter learns it
  before they spend an evening.

**The gate lives in the runner, not only in the installer, and that is
deliberate:** `BACKLOG.md` item 5 says the audio stack must not be detected at
install time, because a package upgrade changes the answer later. An
administrator who backports 0.5 gets audio on the next restart with nothing to
re-run. The installer's line only informs a person; it decides nothing.

Version parsing, exactly, because "less than 0.5" invites a wrong glob:

```sh
# "Compiled with libwireplumber 0.5.13" -> "0.5.13"
WP=$(wireplumber --version 2>/dev/null | sed -n 's/^Compiled with libwireplumber //p' | head -n1)
WP_MAJOR=${WP%%.*}
WP_REST=${WP#*.}
WP_MINOR=${WP_REST%%.*}
```

Then: if `$WP` is empty, or either field is not a non-empty run of digits,
**refuse** and log the raw string. Otherwise refuse when
`WP_MAJOR -eq 0 && WP_MINOR -lt 5`. Refusing on an unparseable version is the
safe direction: the failure is a terminal with no sound and a loud line, while
the other direction is three processes failing in a way nothing reports.

### The profile's two keys, and the guard on the dangerous one

`sound=local` is the value. **`sound=remote` is one word away and sends the
session's audio to the *other* machine — the exact outcome D-009 forbids, in a
child's room, into an adult's.** It is guarded by name, in `encore-install.sh`,
immediately after the existing `CHANGEME` check:

```sh
if ! grep -q '^sound=local$' "$PROFILE"; then
    die "profile does not say sound=local — the terminal would be silent (D-009)"
fi
if grep -q '^sound=remote' "$PROFILE"; then
    die "profile says sound=remote — that sends the session's audio to the OTHER machine (D-009 forbids it)"
fi
```

**Write these as `if` statements, not as `grep … && die`.** The file runs under
`set -eu`, and a bare `grep … && die` at the top level exits the script when
the `grep` finds nothing — which is the *success* case here. That is a live
trap in this file's style.

**The guard cannot move into the runner.** `boundaries.md` part 2 says the
runner must not know anything in the profile, and ADR-0009 restates it as "may
know where, never who". The installer is the only place this check can live.

**The subsystem stays unnamed.** Remmina's value may carry a comma and a
backend (`local,sys:pulse`); this product ships the bare word, so the client
resolves the backend per connection. A package upgrade or a plugged-in headset
changes the right answer after install, and `BACKLOG.md` item 5 forbids
freezing it. `audio-output=` and `microphone=`'s device half stay empty for the
same reason — that is what "nobody picks a device from a list" (R-12) means
mechanically.

**The microphone key is `unknown` and is not guessed.** The template has a
separate `microphone=` key, empty. `BACKLOG.md` item 5 records the architect's
reading that `sound=local` "switches on both directions from one key". The
presence of a second, separate key is evidence against that reading, and
neither has been tested. **Step P1.0 settles it by reading what Remmina itself
writes, and no value for either key is typed into this repository until it
does.**

---

## The phases

Ordered. Nothing later may start before the phase above it has produced a
written result in `docs/tests.md`.

### Phase 1 — measure. Nothing is implemented until this is done.

| Step | Needs | Where |
|---|---|---|
| P1.0 read the two profile keys from Remmina itself | **mechanical**, no terminal, no remote host | any desktop machine with Remmina |
| P1.1 do the helpers come up inside the session | **mechanical**, over SSH | the test VM, converted |
| P1.2 do they survive routine restarts | **mechanical**, over SSH | the test VM |
| P1.3 does a broken sound path break the connection | **mechanical**, over SSH | the test VM |
| P1.4 does the client actually use the server | **a person, with ears, in the room** | a terminal with speakers |
| P1.5 does the microphone half work | **a person, in the room, speaking** | a terminal with a microphone |
| P1.6 does a terminal with no microphone still connect | **mechanical**, over SSH | the test VM (which has none) |

#### P1.0 — let Remmina write the values; do not guess them

On any desktop machine that has Remmina. Open any RDP profile, set audio output
to the local machine and turn the microphone redirection on, save, then read the
file it wrote:

```sh
grep -E '^(sound|microphone|audio-output)=' ~/.local/share/remmina/*.remmina
```

**This is the authority for both keys.** Whatever appears on the right-hand
side of `sound=` and `microphone=` is what the template gets, minus any device
name after a comma. Write the exact output into `docs/tests.md`.

- **If `microphone=` is still empty after turning the microphone on** — then
  the architect's one-key reading is right, and the input half needs no second
  key.
- **If it gained a value** — that value is the input lever, and the one-key
  reading in `BACKLOG.md` item 5 is wrong and needs correcting by the product
  manager. Say so; do not correct it yourself.

This step costs five minutes, needs no terminal and no remote host, and removes
every guess about the profile from the rest of the plan. **Do it first.**

#### P1.1 — do the helpers come up inside the kiosk session?

Apply the new `encore-kiosk.sh` by hand on the test VM (copy it to
`/usr/local/bin/encore-kiosk.sh`, mode 755), then, over SSH:

```sh
systemctl restart encore-kiosk.service
sleep 8
journalctl -t encore-kiosk -b --no-pager | tail -60
U=$(id -u encore); ls -la /run/user/$U; ls -la /run/user/$U/pulse
```

- **`encore: sound: server ready at /run/user/<uid>/pulse/native`, and `pulse/`
  exists** → the approach works from inside the session. This is unknown 2's
  first half.
- **A `SOUND UNAVAILABLE` line** → read it; it names which of the seven checks
  stopped. Fix and repeat.
- **`XDG_RUNTIME_DIR is not set`** → the contingency is one line at the top of
  the runner, `XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}; export
  XDG_RUNTIME_DIR`. Add it only if this line appears, and record that it was
  needed — it contradicts the current reading of the unit and is worth knowing.
- **Anything named `bus`, `keyring`, `gvfs`, `doc-*` or a snap socket appears in
  `/run/user/<uid>`** → **STOP.** The approach has the same leak as the rejected
  one and the whole ticket goes back to the architect.

Confirm nothing else was widened:

```sh
loginctl show-session "$(loginctl --no-legend list-sessions | awk '$3=="encore"{print $1}')" -p Class -p Type -p Active
```

The class must be exactly what it was before this change. **If this change
altered the session class, something in it is doing the thing the author
rejected.**

#### P1.2 — do they survive routine restarts?

A dropped connection is normal (R-18, D-026), so the unit restarts constantly.
This is unknown 2's second and harder half.

```sh
for i in 1 2 3 4 5; do
    systemctl restart encore-kiosk.service
    sleep 8
    printf 'run %s: unavailable=%s pipewire=%s pulse=%s wireplumber=%s\n' "$i" \
        "$(journalctl -t encore-kiosk --since '-8s' --no-pager | grep -c 'SOUND UNAVAILABLE')" \
        "$(pgrep -u encore -x -c pipewire || echo 0)" \
        "$(pgrep -u encore -x -c pipewire-pulse || echo 0)" \
        "$(pgrep -u encore -x -c wireplumber || echo 0)"
done
```

- **`unavailable=0 pipewire=1 pulse=1 wireplumber=1` on every run** → pass.
- **Any count above 1** → helpers are leaking across restarts. The cgroup
  teardown assumption is wrong. **Stop and escalate** — do not add a `pkill` to
  the runner to paper over it, because whatever is escaping the cgroup will
  escape a `pkill` race too.
- **`unavailable=1` only on later runs** → the second start is racing the first
  run's teardown. The fix is in the waits, not in the ordering, and the numbers
  need to come from this measurement rather than from a guess.

#### P1.3 — does a broken sound path break the connection?

**The most important measurement in this plan, and the cheapest.** It decides
whether `sound=local` can ship unconditionally.

Set `sound=local` on the live profile, then disable the helpers:

```sh
sed -i 's/^sound=.*/sound=local/' /var/lib/encore/.local/share/remmina/*.remmina
sed -i 's/^start_sound$/: # start_sound disabled for P1.3/' /usr/local/bin/encore-kiosk.sh
systemctl restart encore-kiosk.service
sleep 15
journalctl -t encore-kiosk -b --no-pager | tail -40
```

- **The remote login screen appears anyway** → a sound failure costs sound and
  nothing else. This is what the design above assumes, and it is why
  `start_sound` always returns 0.
- **The connection does not come up, or retries** → `sound=local` cannot ship
  unconditionally. **Stop and escalate**: R-12 has just collided with R-8, and
  choosing between them is the architect's and the author's, not the engineer's.
  This is the same shape of harm as the microphone risk `BACKLOG.md` item 5
  names — a failing audio channel presenting as an unreachable host, retried
  for ever under D-020.

Undo both `sed` lines afterwards.

#### P1.4 — does the client actually use the server? (unknown 1)

Needs a person with ears, a terminal with speakers, and the remote host up.
With the runner restored and `sound=local` on the live profile:

```sh
systemctl restart encore-kiosk.service
journalctl -t encore-kiosk -b --no-pager | grep -iE 'rdpsnd|audin|pulse|sound'
```

Then play something inside the remote session.

- **Pass:** it comes out of the terminal's speakers, and nobody chose a device.
- **Silent, but `rdpsnd` lines appear** → the channel opened and the far end or
  the device is the problem. `pactl list short sinks` on the terminal (install
  `pulseaudio-utils` on the test machine only — it is a diagnostic, **not** a
  package this product installs).
- **No FreeRDP lines in the journal at all** → that is the observability half of
  this ticket failing, not the audio half. See *Observability* below; the levers
  are `stdbuf` and `WLOG_LEVEL`, and this measurement is what proves whether
  they worked.

#### P1.5 — the microphone (unknown 3, first half)

Needs a person and a machine that has a microphone. Apply whatever P1.0 said
the input lever is, restart, speak, and check the remote session hears it.
Record the FreeRDP `audin` lines either way.

#### P1.6 — a terminal with no microphone must still be fully usable (D-014)

**The test VM has no microphone, which makes it the right machine for this.**
With the input lever applied, restart and confirm the remote login screen still
appears.

- **It connects** → input can ship.
- **It does not** → **input does not ship in this ticket.** Output ships alone,
  `microphone=` stays empty, and D-014's input half becomes a separate backlog
  item with this measurement attached. That is a scope cut and the product
  manager makes it — hand them the measurement, do not make the call.

This is the risk `BACKLOG.md` item 5 names in its own words, and it is the one
that costs most if it is missed: under D-020 the terminal would retry for ever
and present a healthy machine as an unreachable host.

### Phase 2 — implement. Mechanical, no hardware, no remote host.

File by file, in this order. Each file is a separate commit.

**There is no automated test harness for shell in this repository** — the only
suite is `encore-probe-test.py`, which covers the probe. So "test first" here
means: **write the `docs/tests.md` entry with its exact command and its pass
condition before writing the code it describes**, and the check is run on a
terminal in Phase 3. That is weaker than the probe's ticket had and this plan
says so rather than pretending otherwise. Building a shell test harness is a new
component and belongs to the architect — it is named in *For the architect*.

| # | File | What |
|---|---|---|
| 1 | `encore-install.sh` | **the repair only** — the directory chain and its assertion. Nothing about audio. Separate commit. |
| 2 | `encore-kiosk.sh` | `log`, `wait_for`, `stop_helpers`, `start_sound`, the trap, and `stdbuf -oL -eL` on the client. |
| 3 | `encore-kiosk.service` | `Environment=WLOG_LEVEL=INFO`. Nothing else. |
| 4 | `encore-install.sh` | the three packages; the `sound=` guards; the wireplumber-version notice at the end. |
| 5 | `encore-kiosk.remmina.template` | `sound=local`, and `microphone=` only if P1.5 and P1.6 both passed. |
| 6 | `encore-uninstall.sh` | **one message line.** See *The uninstaller*. |
| 7 | `docs/tests.md` | Test 5 rewritten. |
| 8 | `README.md` | known issue 6 split; D-034 added; the wireplumber note in the qualification table. |
| 9 | `docs/troubleshooting.md` | one entry: a silent terminal. |

#### Step 2 — the runner

Structure, exactly:

```sh
#!/bin/sh
export GDK_BACKEND=wayland
export HOME=/var/lib/encore

log() { ... }
wait_for() { ... }
stop_helpers() { ... }
start_sound() { ... }

trap stop_helpers INT TERM EXIT
start_sound

PROFILE=$(find "$HOME/.local/share/remmina" -maxdepth 1 -name "*.remmina" | head -n 1)

while true; do
    ...
done
```

`start_sound` is called **once, before the loop.** The helpers are long-lived
and must not be restarted per iteration. This placement is also what makes item
12 cheap later: deleting the loop leaves `start_sound` exactly where it is.

The comment above `start_sound` carries the reason, because the next person to
read this file will otherwise delete it as unrelated to remote desktops:

```sh
# The sound server is started here, inside the kiosk's own PAM session, rather
# than as a system unit beside it. /run/user/<uid> exists only while a session
# for this identity exists, and this unit restarts whenever a connection drops
# (R-18, D-020, D-026) — so a sibling unit would race the runtime directory on
# every reconnect. Started here, the helpers start with the session, die with
# it, and share its cgroup.
#
# `wireplumber -p main-embedded` is the upstream profile for running with no
# session bus and no login-session integration. That is the whole point: the
# alternative — letting the session class be lifted so the machine starts sound
# for us — also starts a session bus, a keyring, a file broker and a package
# prompt that can draw on the screen, which R-16, D-012 and R-6 exclude. See
# BACKLOG.md item 5 and D-034.
```

The client invocation gains `stdbuf -oL -eL` and nothing else:

```sh
stdbuf -oL -eL remmina --enable-fullscreen --disable-toolbar --enable-extra-hardening -c "$PROFILE"
```

`stdbuf` is in `coreutils`, which is on every machine in scope.

#### Step 4 — the installer

Packages: add `pipewire pipewire-pulse wireplumber` to the existing
`apt-get install` line. **This is not a new dependency decision** — the
architect has already chosen these three binaries as the mechanism; ensuring
they exist is the mechanical consequence, and a minimal Debian or Pi OS Lite
install may not carry them. It is flagged in *For the architect* anyway,
because it lengthens what an install puts on a machine.

The version notice goes with the other end-of-run warnings, in their style —
**it reports and gates nothing**:

```sh
# Said here because this is the only moment a person is standing at the machine.
# The runner decides for itself on every start, so a later backport of 0.5
# turns sound on with nothing to re-run — BACKLOG.md item 5 forbids freezing
# the audio stack at install time.
```

It must print the version it found, name 0.5 as what is needed, and say plainly
that the terminal will work and be silent.

#### Step 5 — the template, and the rule the template sets for itself

`encore-kiosk.remmina.template:1-10` says it is generated verbatim from a
profile observed working, and that if it needs to change, somebody must change
a working profile, prove it, and regenerate. **That rule is honoured, not
bypassed.** P1.0 obtains the value from Remmina's own writing; P1.4 proves it on
a terminal. Only then is it copied in, and the header block gains a short note
saying that `sound=` is the one field in this file that was changed
deliberately rather than carried across, with the date and the reason. Without
that note, the next person to regenerate the template from a machine whose
profile says `off` will silently turn audio back off.

### Phase 3 — verify on the terminal. A person at the hardware.

Run Test 5 as rewritten, in full, on the VM and then on a terminal with real
speakers. Write the results into `docs/tests.md`. Item 5 is not done until
Test 5 has a status other than "never run".

### Phase 4 — Raspberry Pi OS (unknown 4). A person at a Pi.

The fault this whole ticket answers may not exist there: the session class that
causes it arrived in a systemd newer than that platform ships. **Before
changing anything on a Pi**, with a converted Pi running:

```sh
U=$(id -u encore); ls -la /run/user/$U
```

- **`pulse/` is already there** → the Pi never had the fault. The runner's
  step 2 check already covers it: it finds the socket and leaves it alone. Test
  5 still has to be run there to confirm sound actually works, but no code
  changes.
- **`pulse/` is absent** → the Pi has the same fault and the same fix applies.
  Check `wireplumber --version` while you are there; trixie should be 0.5.

Either outcome is a result worth writing down. Neither blocks the ticket.

---

## The uninstaller — verified, and it needs one line

**The architect's finding is correct, and this was checked against the file
rather than assumed.** Everything this ticket creates at runtime lives in
places `encore-uninstall.sh` already removes or that outlive nothing:

| What | Where | Who removes it |
|---|---|---|
| the runner, with `start_sound` in it | `/usr/local/bin/encore-kiosk.sh` | `rm -f`, already there |
| `WLOG_LEVEL=` | `/etc/systemd/system/encore-kiosk.service` | `rm -f`, already there |
| `sound=local` | inside the profile, under `/var/lib/encore` | `userdel -r` + `rm -rf /var/lib/encore` |
| wireplumber's state | `/var/lib/encore/.local/state` | the same |
| every socket the helpers make | `/run/user/<uid>` | `logind`, when the session ends |
| helper log output | the journal | not a file |

**No `loginctl enable-linger`. No `/var/lib/systemd/linger/encore`.** The
rejected approach's R-11 trap — a root-owned flag file that `userdel` does not
remove — does not exist in this one at all. That is worth saying out loud,
because it is the single largest advantage this approach has over the one it
replaces, and it is invisible in the diff.

**The one change needed is a message, not removal logic.** The uninstaller
prints what it deliberately leaves behind:

```
echo "  remmina, remmina-plugin-rdp, cage, kbd  (ordinary packages)"
```

If step 4 adds three packages to the install, that line becomes wrong, and a
line that lists four of seven things left on the machine is worse than no line.
Add the three names. **Do not make the uninstaller remove them** — the file's
own comment gives the reason, and removing a machine's sound server because it
was once a terminal is exactly the "one step that could break something
unrelated" it refuses to take.

---

## Observability — making a silent failure loud

Three separate things are wrong today and this ticket fixes the first two.

1. **Our own code says nothing.** Closed by the two log prefixes and the seven
   checks. Every failure of the sound path now has a line with a reason in it.
2. **The client's output never reaches the journal.** The likely cause is
   buffering: output to a pipe is fully buffered, never flushed, and then the
   process is killed. `stdbuf -oL -eL` on the client is the lever, and
   `Environment=WLOG_LEVEL=INFO` in the unit is the second. **Note that the
   profile already asks for `freerdp_log_level=INFO`** — so the level is not
   the problem and the buffering explanation is the stronger one. `WLOG_LEVEL`
   is set anyway, because it also covers the phase before the profile is read.
3. **Nothing tells a person that the terminal is broken.** Not closed here.
   That is `README.md` known issue 1 and `BACKLOG.md` item 12, and it needs
   something that can draw beside the session, which does not exist.

**`G_MESSAGES_DEBUG` is deliberately NOT set in the shipped unit.** `all` floods
the journal with GTK and GLib chatter from the client, and the logging that
matters for audio is FreeRDP's WLog, which does not go through GLib. It is a
measurement-phase lever the author may add by hand during P1.4; it is not part
of the product. That is a decision, made here, so nobody adds it later as an
obvious improvement.

**Expected noise, and it is not a fault.** With no session bus, the helpers
complain about rtkit, the desktop portal, mpris, bluez and libcamera on every
start. Those lines are the normal shape of running without a bus and are named
in the troubleshooting entry so nobody spends an evening on them. One real
consequence hides among them: **realtime scheduling is unavailable without the
system bus, which may mean audio glitches on old hardware.** Not fatal, and it
is the first thing to suspect if sound works but stutters on a 2009 machine.

---

## Tests

`docs/tests.md` Test 5 is currently "there will not be [sound]". It is rewritten
as three checks under the same number, because they are three different
questions with three different answers and one of them can fail while the
others pass.

- **5a — does sound come out?** With a session up, play something in the remote
  session. Pass: it comes out of the terminal's speakers, with nobody having
  chosen a device. Include the `SOUND UNAVAILABLE` grep as the first thing to
  run on a failure, and say that an empty result means the server came up and
  the fault is further along.
- **5b — does the session hear the microphone?** On a machine that has one.
  Pass: the far end hears it. Recorded as **not applicable** on a machine with
  no microphone, never as a pass.
- **5c — does a terminal with no microphone still connect?** This is D-014's
  hard half and the one that can silently break the product. Pass: the remote
  login screen appears, and the journal shows no repeated restarts. **This
  check runs on every platform, including ones with a microphone, by testing on
  the VM.**

Add, in the table at the top of the file, the fact that Test 5 now has three
parts, and leave the status column honest: `never run` until somebody runs it.

**The one-command check gets its own line in `docs/troubleshooting.md`**, in
that file's existing check-and-cause style, with the expected-noise list beside
it.

---

## Callers to update

| Contract | Who consumes it | Action |
|---|---|---|
| `encore-kiosk.sh`'s behaviour | `encore-kiosk.service` `ExecStart` (via `cage`) | none — the file's path, mode and exit behaviour are unchanged |
| the `sound=` key | `encore-install.sh` (writes the profile), the client (reads it) | the installer gains the two guards; nothing else reads it |
| the profile's location and single-file rule | `encore-install.sh:…` count check, `encore-kiosk.sh`'s `find` | none — no new file is added to that directory |
| `/var/lib/encore/.local`, `.config` ownership | nothing reads it today; wireplumber will | the repair, and its assertion |
| the packages-left-behind list | `encore-uninstall.sh`'s closing message | three names added |
| `/run/user/<uid>` contents | `cage` (Wayland socket), now the helpers | none — different filenames, same directory |

No signature, exit status, status code or file format changes. **Nothing
outside this repository consumes anything this ticket touches.**

Three architecture records will describe a product that has changed. **The
engineer does not edit them** — they are listed under *For the architect*.

---

## Out of scope

The engineer must not touch any of these, however close they sit.

- **The retry loop in `encore-kiosk.sh`.** ADR-0007 and `BACKLOG.md` item 12
  own it. It is the most tempting thing in the file and removing it changes
  recovery behaviour nobody has measured (item 10 has to run first).
- **`KillMode=`, `RestartSec=`, `TimeoutStopSec=`.** Item 9 and ADR-0007.
- **`ProtectHome=`, `InaccessiblePaths=`, `IPAddressDeny=`.** Item 7 and
  `debt.md` D-A4. The helpers need `/run/user`, which is exactly the tangle
  D-A4 records; do not reopen it here.
- **Anything that lifts, sets or declares the session class or type.** That is
  the rejected approach. If it looks like the obvious fix for something in
  Phase 1, that is the trap this rewrite exists to avoid.
- **`loginctl enable-linger`.** Same reason, plus R-11.
- **Adding `encore` to the `audio` group.** There is nothing for the permission
  to apply to; the device access list already names the identity.
- **`BACKLOG.md`, `docs/product/`, `docs/architecture/`.** Product and
  architecture records. Findings go back to their owners.
- **The clipboard.** `README.md` known issue 6 bundles "no sound" with "the
  clipboard is open"; this ticket splits the sentence and fixes only the sound
  half. D-019 and item 7 own the other.
- **`pulseaudio-utils`.** A diagnostic for the author's test machine, not a
  package this product installs.

---

## Stop and escalate if

- **`/run/user/<uid>` gains a `bus`, `keyring`, `gvfs`, `doc-*` or snap socket**
  after the change (P1.1). The approach has the leak it was chosen to avoid.
  Architect.
- **The session class or type differs from before** (P1.1). Same.
- **A sound failure stops the connection coming up** (P1.3). R-12 has collided
  with R-8 and the resolution is a product call. Architect and product manager.
- **A terminal with no microphone will not connect** (P1.6). D-014 forbids it.
  Output ships alone and the input half becomes a new backlog item. Product
  manager.
- **Helpers leak across restarts** (P1.2). The cgroup assumption is wrong. Do
  not add a `pkill`. Architect.
- **`wireplumber -p main-embedded` fails on 0.5.x.** The one upstream fact this
  plan rests on is not true, and there is no second approach in reserve.
  Architect.
- **Anything suggests the fix belongs in a system unit rather than the runner.**
  The architect has already ruled on this; a second opinion arrived at while
  implementing is not a new decision.

---

## Size, honestly

**L, not the M recorded in `BACKLOG.md`.**

Nine files, three of them documentation. But the size is not in the files. It
is in this: **three of the four things the ticket depends on are unknown, and
each needs a person, a terminal and the remote host at the same time.** One
measurement session is not enough — P1.4 and P1.5 need ears in the room, P1.6
needs the opposite machine, and Phase 4 needs a Pi. Add to that a version gate
that excludes the product's own lowest supported Ubuntu, which is a product
promise narrowing rather than a line of code.

The implementation is genuinely small. The proving is not, and this ticket is
the proving.

---

## What stays unknown when this ticket is done

Written here so it can be copied into the record rather than reconstructed.

1. **Audio on Ubuntu 24.04 LTS.** wireplumber 0.4.17 has no profiles, so the
   chosen mechanism cannot run there. The terminal works and is silent, and
   says so. Closing it means either a 0.4 configuration that omits the
   bus-dependent modules — designed and proven by nobody — or raising the
   product's floor above its own stated one. **Architect and product manager.**
2. **Old hardware.** Realtime scheduling is unavailable without the system bus.
   Whether that means glitch-free audio on a 2009 machine is untested, and
   `BACKLOG.md` item 14 is where it gets tested.
3. **D-034's cost, unchanged.** Sound follows the active session on the seat, so
   a text console can silence a terminal until it restarts, and nothing says
   why. Accepted, and listed in `README.md` by this ticket.
4. **Whether a terminal that *had* sound and lost it is detectable.** The checks
   in this plan all run at start. Nothing watches afterwards. A sound server
   that dies an hour in is silent in both senses, and that is `README.md` known
   issue 1 in a new coat — it is item 12's, not this ticket's.
5. **Whether the microphone half is wanted on every terminal.** D-014 says yes.
   Nobody has sat in the room with one on.

---

## For the architect

Raised, not acted on.

1. **`wireplumber -p main-embedded` needs 0.5; Ubuntu 24.04 LTS ships 0.4.17,
   and 24.04 is this product's own stated floor.** The chosen approach delivers
   no audio on a supported platform. Measured from the Ubuntu archive while
   writing this plan; confirm on a 24.04 machine before acting.
2. **Three packages are added to the install** (`pipewire`, `pipewire-pulse`,
   `wireplumber`). Mechanically required by the chosen approach, but it grows
   what conversion puts on a machine, and `stack.md` has no row for any of them.
3. **`constraints.md` C-5, `boundaries.md` part 2 and `interfaces.md` I-4 will
   describe a product that has changed** once this lands: C-5 says audio is
   switched off; boundary 2 lists what the runner owns and will not mention the
   sound server; I-4 describes the identity and its runtime directory. The
   engineer is not editing architecture records.
4. **There is no test harness for shell in this repository**, so every step of
   this ticket is proven by a human running a command. Whether that is worth
   fixing is yours; it is a new component and was not designed here.
5. **`install -d` applying ownership only to the last component** is a defect
   shape, not one defect. Anywhere else that pattern appears has the same hole.
