# Plan — the sound guard must establish that something is listening

Written by the senior engineer, 2026-09-29, at the software engineer's
escalation: choosing the mechanism was a design decision, not an implementation
one. **There is no `BACKLOG.md` item holding this work** — it arrived as a
measured bug against the output half of item 5, which is marked done. Filing it
is the product manager's; this plan does not touch the backlog.

**Sensitive:** no. No credential, no permission, no personal data. It removes a
file from the terminal identity's own runtime directory and makes one local
socket connection; nothing leaves the machine.

---

## What changes, and for whom

A terminal that restarts — which is the normal case, because a dropped
connection causes one (R-18, D-020) — gets sound back. Today it does not: the
guard in `start_sound` sees the socket file the previous session left behind,
reports success, and starts nothing, so the client falls through to ALSA and
fails. The measured journal (test VM, 2026-09-29):

```
encore: sound: a PulseAudio-protocol socket already exists; leaving it alone
audin_pulse_connect failed
rdpsnd: Unable to load sound playback subsystem pulse because of error 12
rdpsnd: Loaded alsa backend
rdpsnd_alsa_open_mixer: snd_mixer_attach failed
```

For the operator, the visible change is three new journal lines that tell a
**dead socket found** apart from a **live server found** apart from **could not
establish which**. The last of those replaces a false `sound:` success with a
truthful `SOUND UNAVAILABLE:`, so the one command in `docs/troubleshooting.md`
keeps being a complete answer rather than a hopeful one.

---

## The component

- **Responsible for:** `encore-kiosk.sh` is the runner — it brings up whatever
  the client needs inside the kiosk's own PAM session, launches the client, and
  says in the journal what it did. `start_sound` is the part of it responsible
  for *there being a sound server for this session, or a single line saying why
  there is not*.
- **Has drifted by:** one thing, and it is the bug. `start_sound` answers "is
  there a sound server?" by asking "does a file exist?" in three places — the
  guard at line 63, and `wait_for` at lines 104 and 115 through a helper whose
  whole contract is existence (`[ ! -e "$1" ]`). Those were the same question
  as long as a socket file could only exist while its server lived. On the
  restart path they are not, and the drift is invisible because the marker
  comments above the function promise something the branch then breaks: the
  failure shape the markers exist to catch is produced by a marker's own
  success line.
- **This change belongs here because:** it is the same responsibility, answered
  correctly. Nothing new is being added to `start_sound` — the existence test it
  already performs is being replaced by the test it always meant.

---

## The mechanism: which tool, and why

The guard must establish that **something is listening on a Unix socket path**,
with no new package (the installer's list stays `remmina remmina-plugin-rdp cage
kbd pipewire pipewire-pulse wireplumber`).

**Chosen: `python3`, connecting an `AF_UNIX`/`SOCK_STREAM` socket to the path.**

1. **It asks exactly the question that failed.** `rdpsnd` connects to
   `pulse/native` and got error 12. A `connect(2)` is the same act: success
   means a server accepted, `ECONNREFUSED` means the path is a socket nobody is
   bound to, `ENOENT` means there is no path. Three facts, three distinct
   `errno` values, no text to parse and no output format to break.
2. **It adds no assumption this repository has not already made.** D-030 and
   ADR-0008 settled that Python 3 from the base system is available on a
   terminal: `encore-probe.py` ships at the repository root with
   `#!/usr/bin/python3` and the runner is designed to call it. Every other
   candidate would introduce a *second* tool assumption.
3. **Where it is absent, the design degrades to today's behaviour with an
   honest marker, never to something worse** — see *If `python3` is missing*.

Rejected, with reasons:

| Candidate | Why not |
|---|---|
| `ss` (iproute2) | Correct and read-only, and `ss -lx` genuinely omits a socket with no listener. But it answers "does the kernel have a bound socket at this path" by grepping a text table, and it is a tool this repository has never depended on. Choosing it would mean carrying two base-system assumptions (`python3` for the probe, `iproute2` here) where one will do. |
| `fuser` (psmisc) | `psmisc` is not something a minimal Debian-family install guarantees, and it answers about *processes holding a file*, which is a different question with the same answer most of the time. Measured present on one Ubuntu VM only. |
| `nc` | `netcat-openbsd` is not guaranteed on a minimal image, and `nc -U` connects *and transfers*, which is more than a guard should do to a running server. |
| `socat` | **Measured missing** on the test VM, 2026-09-29. Would be a new package. Excluded. |
| `pactl` | **Measured absent** on the test VM until installed by hand. Excluded. |
| `pw-dump` / any PipeWire utility | The runner already treats these as optional — `command -v pw-dump` with a written fallback at line 127. A tool this repository has decided may be missing cannot be the basis of a guard that must be correct. |

**A connection is made to a live server in one branch.** It sends no bytes and
closes at once; `pipewire-pulse` sees a client connect and disconnect. That is
the cost of asking the real question instead of a proxy for it, and it is paid
once per start.

---

## Seams

Three functions in `encore-kiosk.sh`. `wait_for` at lines 26–34 is **deleted**;
both of its callers move to `wait_for_socket`. No other file changes.

### `socket_is_listening <path>` — the whole mechanism, in one place

```sh
# Is something listening on the Unix socket at $1?
#   0  yes — a server accepted a connection
#   1  no  — $1 exists and nothing is bound to it (a socket a dead session left)
#   2  no  — $1 does not exist
#   3  could not be established
# Exit statuses, not text: the caller must branch on all four.
socket_is_listening() {
    [ -e "$1" ] || return 2
    command -v python3 >/dev/null 2>&1 || return 3
    python3 - "$1" <<'PY'
import errno, socket, sys
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(2)
try:
    s.connect(sys.argv[1])
except FileNotFoundError:
    sys.exit(2)
except ConnectionRefusedError:
    sys.exit(1)
except OSError as e:
    sys.exit(1 if e.errno == errno.ECONNREFUSED else 3)
else:
    sys.exit(0)
finally:
    s.close()
PY
}
```

Exactly as written. In particular: `FileNotFoundError` and
`ConnectionRefusedError` are caught **before** the generic `OSError`, because
both subclass it; the timeout is 2 seconds; and it is `python3 - "$1"` so the
path arrives as `sys.argv[1]` and never through a shell, so there is no
interpolation to get wrong.

**The misuse this makes impossible:** there is no way to ask this function
"does the file exist", because it does not have that answer to give. A caller
that writes `if socket_is_listening ...; then` gets the live-server branch and
nothing else — the other three outcomes are different numbers, so a caller that
ignores them reads as obviously unfinished rather than as working.

**Why `3` is not folded into `1`.** "Nothing is listening" licenses deleting a
file and starting a server. "I could not tell" licenses neither. Collapsing
them is the same error this ticket exists to fix, one level down.

### `claim_socket_path <path>` — the decision, made once

```sh
# Decide whether we may start a server that will bind $1, and clear the way if
# we may. Logs the distinguishing line itself in every branch.
#   0  the path is clear: nothing is listening, nothing is in the way
#   1  something is already listening there — not ours, leave it alone
#   2  could not be established, or a dead socket could not be removed
claim_socket_path() { ... }
```

Its three branches, and the line each one logs:

| `socket_is_listening` says | `claim_socket_path` logs | returns |
|---|---|---|
| `0` listening | `sound: a sound server is already listening on <path>; leaving it alone` | 1 |
| `2` absent | nothing — there is no fact here worth a line | 0 |
| `1` present, dead | `sound: the socket at <path> was left by a session that has ended and nothing is listening on it; removing it` then `rm -f`. If `rm -f` fails: `SOUND UNAVAILABLE: a dead socket at <path> could not be removed` and return 2 | 0 |
| `3` cannot tell | `SOUND UNAVAILABLE: something exists at <path> and whether a sound server is listening on it could not be established, so no second server was started beside a possibly working one` | 2 |

**The misuse this makes impossible:** the "leave a working server alone" rule
and the "clear a dead socket" rule cannot be applied in the wrong order or to
one path and not the other, because they are one call. And `0` is returned only
after the path has actually been cleared — the permission to start and the
clearing are the same event, so there is no prepare-then-use pair to forget.

### `wait_for_socket <path> <seconds>` — replaces `wait_for`

```sh
# Wait up to $2 seconds for something to be listening on $1. Returns 1 on
# timeout. Succeeds on socket_is_listening 0 (a server accepted) and on 3
# (something is there and we cannot interrogate it) — from a path that
# claim_socket_path found clear, both mean the server we just started has bound.
# A dead socket (1) and an absent path (2) both keep waiting, which is the whole
# difference from the old existence test.
wait_for_socket() { ... }
```

Same shape as the deleted `wait_for` — `_waited` counter, `sleep 1`, the
caller's budget — with `[ ! -e "$1" ]` replaced by `socket_is_listening "$1";
case $? in 0|3) return 0 ;; esac`.

**The misuse this makes impossible:** the old helper returned success instantly
for a stale socket, and its name (`wait_for`, "wait for the path $1 to exist")
told the caller that was correct. There is no longer a function in this file
that will tell a caller a socket is ready because a file is there.

---

## `start_sound`, after the change

Order, with every path's marker. Nothing else in the function moves: the
`XDG_RUNTIME_DIR` check, the three binary checks, the `wireplumber` version
check, the `</dev/null` redirections, the `HELPER_PIDS` accounting, the
`pw-dump` count and `return 0` at the end all stay exactly as they are.

1. `XDG_RUNTIME_DIR` unset → `SOUND UNAVAILABLE`, return 0. *Unchanged.*
2. `claim_socket_path "$XDG_RUNTIME_DIR/pulse/native"` — **this replaces the
   guard at lines 63–66.** `1` → return 0 (a server is already there: the
   guard's intent, now established rather than assumed). `2` → return 0. `0` →
   on.
3. Binary checks, `wireplumber` version checks. *Unchanged.*
4. `claim_socket_path "$XDG_RUNTIME_DIR/pipewire-0"` — **new, and it is the
   second half of the same bug.** `0` → on. `2` → return 0.
   `1` → a PipeWire server is listening that this capability did not start,
   while nothing serves the PulseAudio protocol. Log
   `SOUND UNAVAILABLE: a PipeWire server is already listening on <path> but nothing is listening on <pulse/native>; helpers were not started beside a sound server this capability did not start`
   and return 0.
5. Start `/usr/bin/pipewire`, record its PID. *Unchanged.*
6. `wait_for_socket "$XDG_RUNTIME_DIR/pipewire-0" 5` — **replaces line 104.**
   Timeout → the existing `SOUND UNAVAILABLE` line, `stop_helpers`, return 0.
   *Message and five-second budget unchanged.*
7. Start `pipewire-pulse` and `wireplumber -p main-embedded`. *Unchanged.*
8. `wait_for_socket "$XDG_RUNTIME_DIR/pulse/native" 5` — **replaces line 115.**
   Timeout → the existing `SOUND UNAVAILABLE` line, helpers deliberately left
   running, return 0. *Unchanged.*
9. `sound: server ready`, then the `pw-dump` count. *Unchanged.*

Every path still emits exactly one of the two markers, including the three new
branches, and `start_sound` still always returns 0.

### Step 4's branch `1` is a design decision, so it is recorded here

The alternative was to adopt the foreign PipeWire server — start
`pipewire-pulse` and `wireplumber -p main-embedded` against it. **Rejected.**
Attaching our own session manager to a sound graph this capability did not
create is the shape of the harm the product named — breaking a machine that was
previously fine — and nobody has ever seen that state on any machine, so it
could only be reasoned about, not tested. Declining loudly costs a silent
terminal on a configuration nobody has observed. If that configuration turns
out to be real, adopting it is a separate ticket with a machine attached.

### Is removing a socket risky when a server *is* running?

No, in the branch where it happens. `rm -f` runs only where a `connect(2)` was
refused, which means the kernel has no listener bound to that path; a path with
a live listener returns `0` and is never touched. The residual race — a server
binding in the microseconds between the refusal and the `rm` — cannot occur for
this identity by construction: no per-user service manager runs for it, which
is the whole finding behind item 5, so the only thing that starts sound here is
this function.

**Nothing for the uninstaller.** Both paths are inside
`$XDG_RUNTIME_DIR` — `/run/user/<uid>` — which is a tmpfs the machine owns and
clears at reboot. R-11 is untouched: this removes a file from the terminal's own
runtime directory, not from the machine's configuration.

### If `python3` is missing

Then `socket_is_listening` returns `3` whenever a path exists, and the only
reachable effects are:

- **First start after boot, no socket present** → `2` everywhere, nothing
  changes, sound comes up exactly as it does today.
- **Restart with a socket left behind** → `SOUND UNAVAILABLE`, no sound. Which
  is *today's outcome on that exact path* — today's guard already declines to
  start anything — with a truthful marker instead of a success line.

So the tool choice cannot make any machine worse than it is now. It can only
fail to make one better. That is the property that made `python3` affordable
here despite the unmeasured platform.

---

## Steps

All of them are one change to one file plus its documentation. There is **no
repair step**: the drift *is* the bug, so separating a behaviour-preserving
refactor from the fix would mean landing a rename and nothing else. Steps 2–4
are one commit; step 1 is a measurement that can be taken before or after and
blocks neither.

This repository has no test harness for shell — `docs/tests.md` holds
procedures run by a person on a machine, and `encore-probe-test.py` covers the
Python probe only. So "test first" here means step 2: the mechanism is exercised
against fabricated sockets, off-target, before it is wired into anything.

### Step 0 — is `/run/user/<uid>` reused across a restart?  [measurement, needs a person at the test VM]

Not a blocker, and the fix is correct either way, because it tests liveness
rather than lifetime. Run it because it decides whether *other* existence tests
in this repository are suspect.

```sh
U=$(id -u encore)
stat -c '%i %W %Z %n' /run/user/$U /run/user/$U/pulse /run/user/$U/pulse/native
systemctl restart encore-kiosk.service
sleep 8
stat -c '%i %W %Z %n' /run/user/$U /run/user/$U/pulse /run/user/$U/pulse/native
```

- **Same inode and same birth time for `/run/user/$U` across the restart** →
  the runtime directory outlives the session. This explains the measured bug,
  and it means **no existence test anywhere in `start_sound` means what it
  appears to mean** — which this plan now assumes and acts on. Write it into
  `docs/tests.md`.
- **Different inode** → the directory was torn down and recreated, and the
  socket seen ten seconds after a session ended came from somewhere this
  project has not identified. **Stop and report.** Do not redesign: the fix
  below is still right, but the bug's mechanism would be unexplained and that
  is worth knowing before more is built on it.
- **`stat` says the path does not exist** → record which of the three was
  missing and when, and carry on. It is a fact about timing, not a failure.

### Step 1 — close the platform gap  [needs a person at a Raspberry Pi]

Everything in *If `python3` is missing* is reasoning, not measurement: the tool
census of 2026-09-29 was taken on **one Ubuntu test VM**, and Raspberry Pi OS
has not been looked at. One command, run on a Pi as any user:

```sh
command -v python3 && python3 -c 'import socket; print(socket.AF_UNIX)'
```

- **A path and `AddressFamily.AF_UNIX`** → the gap is closed and the guard is
  correct on that platform.
- **No output, or an `ImportError`** → the guard degrades to the
  `SOUND UNAVAILABLE` branch on every restart of a Pi terminal. That is not a
  regression, but it means Pi terminals get no sound after a reconnect, and
  **that is a finding for the product manager**, who decides whether it is worth
  a second mechanism.

Can be run before or after the change lands.

### Step 2 — prove the mechanism, off-target  [mechanical, any machine with `python3` and `sh`]

Write `socket_is_listening` exactly as given above, and nothing else. Then
exercise all four of its answers against paths made for the purpose, in a
temporary directory — **no VM, no Pi, no service, nothing at risk**:

```sh
D=$(mktemp -d)
python3 -c 'import socket,sys; s=socket.socket(socket.AF_UNIX); s.bind(sys.argv[1]); s.listen(1); input()' "$D/live" &
sleep 1
: > "$D/plainfile"
python3 -c 'import socket,sys; s=socket.socket(socket.AF_UNIX); s.bind(sys.argv[1])' "$D/dead"   # binds, exits, leaves the socket
```

| Path | Expected status | What a wrong answer proves |
|---|---|---|
| `$D/live` | `0` | the mechanism cannot see a listener, and the guard would start a second server beside a working one — the one way this change could break a machine that was fine |
| `$D/dead` | `1` | the mechanism cannot see a dead socket, so the measured bug is not fixed |
| `$D/plainfile` | `1` or `3` | either is acceptable: a regular file at a socket path is not a listener. **`0` is a failure** |
| `$D/missing` | `2` | absence is being confused with something else |
| `$D/dead`, with `python3` hidden from `PATH` | `3` | the conservative branch is unreachable and a machine with no `python3` would take a decision on no evidence |

Record the five results in `docs/tests.md` as a new test, with the date and the
machine. **That table is the proof this ticket rests on** — every later step
assumes these five answers.

**These five were run, exactly as written above, by the senior engineer on the
author's Fedora workstation on 2026-09-29, and all five matched:** `live` → 0,
`dead` → 1, `plainfile` → 1, `missing` → 2, `dead` with `python3` off `PATH` →
3, and `sh -n` clean. So the table is a measurement on one machine, not a
prediction — but that machine is **Fedora with `bash` as `/bin/sh`**, not the
target's Debian-family `dash`, and not a Pi. Re-running it on the test VM is
still part of this step, because `dash` is where the heredoc-in-a-function has
to hold.

### Step 3 — wire it in  [mechanical]

Add `claim_socket_path` and `wait_for_socket` as specified. Delete `wait_for`
and both of its calls. Apply the nine-step order under *`start_sound`, after
the change*. Then, before anything is copied anywhere:

```sh
sh -n encore-kiosk.sh
```

It must be silent. The file is `#!/bin/sh` and the target runs `dash`, so
nothing bash-only may appear — in particular no `[[`, no `local`, no arrays.
Locals stay `_`-prefixed, as `_waited` and `_wp` already are.

### Step 4 — watch a restart do the right thing  [needs a person at the test VM]

The whole point of the ticket, and it cannot be proved anywhere else. Copy the
new `encore-kiosk.sh` to `/usr/local/bin/encore-kiosk.sh`, mode 755, then:

```sh
U=$(id -u encore)
systemctl restart encore-kiosk.service
sleep 10
journalctl -t encore-kiosk -b --no-pager | grep -iE 'sound|rdpsnd|audin|pulse'
systemctl restart encore-kiosk.service          # the case the bug lives in
sleep 10
journalctl -t encore-kiosk --since '-12s' --no-pager | grep -iE 'sound|rdpsnd|audin|pulse'
ls -la /run/user/$U /run/user/$U/pulse
pgrep -u encore -x -c pipewire; pgrep -u encore -x -c pipewire-pulse; pgrep -u encore -x -c wireplumber
```

It is `journalctl -t encore-kiosk`, never `-u`: `PAMName=login` puts these
processes outside the unit's cgroup, so a query by unit matches nothing the
runner wrote and says so silently.

- **Second restart shows `removing it` then `sound: server ready`, one of each
  helper running, and no `rdpsnd: Loaded alsa backend`** → the ticket is done.
- **Second restart shows `already listening ... leaving it alone`** → something
  really was listening. Then the socket the bug report saw was live and the
  diagnosis is wrong. Stop and report.
- **`SOUND UNAVAILABLE: ... could not be established`** → `python3` is missing
  on the VM. Step 2 said what that means; it is not a code fault.
- **More than one of any helper** → `claim_socket_path` let a second server
  start beside a first. Stop; this is the harm the product named.

Then the ordinary five-restart loop already written at
`docs/plans/audio-both-directions.md` under P1.2, which now counts
`SOUND UNAVAILABLE` correctly.

### Step 5 — write down the new lines  [mechanical]

`docs/troubleshooting.md`, the table under *A terminal with no sound*: add a row
for each of the three new messages — dead socket removed (informational, not a
fault), a server already listening, and could-not-establish (with `python3` as
the thing to check). `docs/tests.md`: the step 2 table, the step 0 result, and
an update to test 5's status line.

Nothing else. Do not add anything to `README.md`: no known issue is being
created, and one is being removed.

---

## Callers to update

- `wait_for` — **deleted.** Its only two callers are `encore-kiosk.sh:104` and
  `:115`, both converted. Nothing outside this file references it; it is a shell
  function in a script that is neither sourced nor exported.
- `start_sound` — one caller, `encore-kiosk.sh:149`, before the retry loop. Its
  contract is unchanged: always returns 0, exactly one marker per path.
- The three new functions have no callers outside `start_sound`.
- **No contract leaves the file.** No signature, exit code, file format,
  environment variable or unit setting changes, so `encore-install.sh`,
  `encore-uninstall.sh`, `encore-kiosk.service`, `encore-kiosk.target` and the
  profile template are all untouched. The installer's package list does not
  grow.
- The journal markers are a contract — `docs/troubleshooting.md` and
  `docs/tests.md` grep for them. The two prefixes are unchanged; three lines are
  added, none removed, which is why step 5 exists.

---

## Out of scope

- **`encore-kiosk.service`.** Not `PAMName=login`, not the retry loop, not
  `KillMode`, not the sandboxing, not `SyslogIdentifier`.
- **The installer and the uninstaller.** No new package. Do not run either on
  the development machine.
- **The microphone** — item 5b, tests 5b and 5c. This is the output path only.
- **`pw-dump` and the output-device count.** It is correct as it stands, its
  `command -v` fallback is deliberate, and nothing branches on it.
- **The tempting nearby thing: making the rest of the runner liveness-aware.**
  There is exactly one other existence test in this file — `[ -f "$PROFILE" ]`
  at line 155 — and a profile *is* a file, so existence is the right question
  there. Leave it.
- **`encore-probe.py`.** It owns one question, the target's RDP certificate.
  The socket check does not go in it, however convenient a Python file looks.
- **`BACKLOG.md`, `docs/product/`, `docs/architecture/`.** Not the engineer's,
  and not this plan's.

---

## Stop and escalate if

- **`sh -n` complains, or the mechanism needs anything `dash` does not have.**
  Do not switch the shebang to `bash`; that is an architect decision about what
  the runner is.
- **Step 2 gives `0` for `$D/dead` or a non-`0` for `$D/live`.** The mechanism
  is wrong and the whole design rests on it. Report the five results; do not
  patch around one of them.
- **Step 4 shows a second helper of any kind.** Stop immediately.
- **The fix appears to need a new package, a new shipped file, or a change to
  the unit.** All three are outside this ticket; the design was chosen
  specifically so that none is required, so needing one means a premise is
  wrong.
- **Step 0 says the runtime directory is recreated on restart.** Report it. The
  fix still stands, but the mechanism of the measured bug would be unexplained.
- **A socket turns out to need removing anywhere outside `$XDG_RUNTIME_DIR`.**
  That is a footprint question and R-11 is at stake.

---

## What remains unestablished when this is done

Stated plainly, because the value of the two markers is that nobody has to
guess which of these was checked.

1. **Raspberry Pi OS has no tool census.** The 2026-09-29 measurement is one
   Ubuntu VM. Everything about the `3` branch — how often a Pi terminal takes
   it — rests on step 1, which needs a Pi. Bounded: the worst case is today's
   behaviour with a truthful marker.
2. **Whether `pipewire-pulse` would have bound over a dead socket by itself.**
   This design removes it first and never finds out. If it would have, the
   removal is belt and braces; the branch is still needed for the log line that
   tells an operator a restart happened.
3. **The live-foreign-`pipewire-0` branch has never been observed on any
   machine.** It is reasoned. It declines rather than adopts, which is the safe
   direction, but the state itself is hypothetical.
4. **Whether `/run/user/<uid>` is reused on a Pi.** Step 0 answers it for the
   VM only.
5. **The microphone, and a terminal with no microphone** — tests 5b and 5c,
   never run, untouched here.
6. **Whether one extra client connect-and-disconnect per start shows up in the
   journal** of a live `pipewire-pulse`. Expected to be quiet or debug-level;
   not measured, and cosmetic either way.
