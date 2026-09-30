# Tests

What to run on a converted machine, and what to write down. Run them in order;
each one assumes the ones before it passed.

**Expect some to fail.** Every failure here answers a question the project
cannot currently answer from its own records. A failure you write down is worth
more than a pass you assume.

Status column is what has actually been watched, not what is believed.

| Test | What it answers | Status |
|---|---|---|
| 1 | Does a session appear at all? | Passed, VM, 2026-09-14 and again 2026-09-23 from a clean install |
| 2 | What happens when the connection drops? | Never run |
| 3 | What happens with no profile? | Failed as expected, VM, 2026-09-14 |
| 4 | Does the off-switch give the machine back? | Never run |
| 5 | Is there sound? Three parts: 5a out, 5b in, 5c a terminal with no microphone | **5a passed, including across restarts** — VM and Mac Mini, 2026-09-29; the restart failure was item 5c and is fixed and observed fixed, VM, 2026-09-30 · **5b channel loads** — the input channel came up on the intended sound system, VM, 2026-09-30; nobody has spoken into it · 5c never run |
| 6 | Must the encryption key travel between machines? | Answered no, VM, 2026-09-23 |
| 7 | Does it survive a reboot? | Never run |
| 8 | Where does this machine read the global certificate file? | Never run |
| 9 | What does the screen show when the handshake is refused? | Never run |
| 10 | Does running setup again leave a working terminal? | Never run |
| 11 | Does the probe agree with the target? | Never run |
| 12 | Does the sound guard tell a live sound server from a socket a dead session left? | **12a passed** — Fedora workstation, `bash` and `dash`, 2026-09-29 · **12b passed** — VM, 2026-09-30, twice on consecutive fast restarts: both sockets found stale, both removed, server started, five output devices · 12a never run on the test VM, and no longer needs to be |
| 13 | Is `/run/user/<uid>` reused across a restart? | **Answered: yes** — VM, 2026-09-30, by 12b rather than by this procedure. Sockets from an ended session were still present, so the directory outlives the session and no existence test in `start_sound` ever meant what it appeared to |

---

## Test 1 — does a session appear?

```sh
systemctl status encore-kiosk.service
journalctl -t encore-kiosk -b --no-pager
```

**Pass:** the remote machine's login screen fills the terminal's screen.

**Do not trust `systemctl status`.** The runner loops forever, so the service
reports `active (running)` whatever is happening. Read the journal.

**It is `-t encore-kiosk` in every test below, never `-u`.** Asking by unit
returns systemd's own lines and nothing the capability wrote, and it does so
silently — so `-u` plus a `grep` looks like a clean result when it is an empty
one. `troubleshooting.md` explains why under "Before anything else".

If nothing appears, go to `troubleshooting.md` — every failure seen so far is
listed there with the check that identifies it.

## Test 2 — what happens when the connection drops?

With a session running, stop RDP on the other machine, or pull the terminal's
network.

**The one question:** does the client disappear and retry, or stay on screen
showing its own error dialog?

Upstream reports it does not exit on disconnect by default. If it sits there,
then self-recovery does not happen at all — and the person at the terminal is
looking at an application they should never see, which is Test 3's failure
arriving by another road.

**This answer decides how backlog item 12 gets fixed. Do not write that fix
before running this test.**

## Test 3 — what happens with no profile?

```sh
mv /var/lib/encore/.local/share/remmina/*.remmina /root/
systemctl restart encore-kiosk.service
```

**Expected, and confirmed on 2026-09-14:** the client's own interface appears,
with a connection editor and a file chooser. This is the defect backlog item 11
exists to close.

Put the profile back afterwards.

## Test 4 — does the off-switch give the machine back?

Reach the machine over SSH or on a text console — its own screen belongs to the
session — then:

```sh
cd ~/encore
sudo ./encore-uninstall.sh
reboot
```

**Pass:** the machine comes back to the startup mode it had before conversion,
with nothing to repair by hand, and behaves as it did before. The script
restores the previous default target from what the installer recorded at the
time, and re-checks every path it removed — it prints "Nothing of Encore's
remains" when the machine is clean.

Confirm independently, rather than trusting the script that did the removing:

```sh
id encore; ls -d /var/lib/encore; ls /etc/systemd/system/ | grep encore
systemctl get-default
```

**Untested. Reversibility is a claim, not an observation** (R-11). It is also
the promise with the least behind it: with no package manager keeping the file
list, removal is only as correct as `encore-uninstall.sh` — so this test earns
its keep every time the installer changes.

## Test 5 — is there sound?

Three questions with three different answers, and one can fail while the others
pass. Record them separately; a single "Test 5 passed" hides which.

**Run this first, whatever the symptom:**

```sh
journalctl -t encore-kiosk -b | grep 'SOUND UNAVAILABLE'
```

**No output means the sound path came up** — the server started, so the fault is
further along (the client, the channel, the far end, the speakers). **Any output
is the reason there is no sound, in one line**, and it names which check
stopped. The runner writes one of `encore: sound: …` or
`encore: SOUND UNAVAILABLE: …` on every path through its sound code, so an
empty result here is an answer rather than an absence of one.

Expected noise in the journal, and **not** a fault: complaints about rtkit, the
desktop portal, mpris, bluez and libcamera. Those are the normal shape of
running a sound server with no session message bus, which is deliberate (R-16,
D-012). See `troubleshooting.md`.

### 5a — does sound come out?

The output half, which is what backlog item 5 ships. With a session up, play
something inside the remote session.

**Pass:** it comes out of the terminal's speakers, and nobody chose a device
from a list (R-12).

If it is silent, take the `grep` above first, then:

```sh
journalctl -t encore-kiosk -b --no-pager | grep -iE 'rdpsnd|audin|pulse|sound'
```

`rdpsnd` lines with no sound means the channel opened and the device or the far
end is the problem. No FreeRDP lines at all means the client's output is still
not reaching the journal, which is a different defect from the audio one.

**Passed on 2026-09-29, on the test virtual machine and on a converted Mac Mini.**
Sound from the session came out of the terminal, on both machines, with nobody
choosing a device. Reported by the author; the marker lines in the journal were
not read back, so what is recorded here is that it was heard, not that the log
said so.

### 5b — does the session hear the microphone?

**Not switched on by this ticket** — `microphone=` ships empty and the input
half is later work. It is tested anyway, because `sound=local` is read as
switching on both directions from one key, so input may arrive regardless.

On a machine that has a microphone: speak, and check the far end hears it.

**Pass:** the far end hears it. On a machine with no microphone this is recorded
as **not applicable**, never as a pass.

### 5c — does a terminal with no microphone still connect?

D-014's hard half, and the one that can silently break the product: a failing
input channel that drops the connection would be retried for ever and present a
healthy machine as an unreachable host.

**This check runs on every platform**, including ones that have a microphone, by
running it on the VM — the test VM has no microphone, which is what makes it the
right machine for this.

```sh
systemctl restart encore-kiosk.service
sleep 15
journalctl -t encore-kiosk -b --no-pager | tail -40
```

**Pass:** the remote login screen appears, and the journal shows no repeated
restarts.

**Fail:** sound cannot ship as it stands. Stop — R-12 has collided with R-8, and
which one gives way is the architect's and the product manager's call, not the
engineer's.

## Test 6 — must the encryption key travel?

```sh
systemctl stop encore-kiosk.service
cp /var/lib/encore/.config/remmina/remmina.pref /root/remmina.pref.bak
rm /var/lib/encore/.config/remmina/remmina.pref
```

Now re-run the password step from `README.md`, then:

```sh
grep '^secret=' /var/lib/encore/.config/remmina/remmina.pref
systemctl start encore-kiosk.service
```

**If a key is created locally and the session connects:** nothing secret ever
has to be copied between machines, and the install gets shorter.

**If it does not:** the key must come from the machine where the profile was
built, every terminal shares one, and what R-14 can honestly promise shrinks
again.

Restore from the backup either way.

**Answered on 2026-09-23, on a VM, without needing the procedure above.** A
clean install reached the password step with no `remmina.pref` anywhere on the
machine — nothing earlier in the install creates one. Running the password
command produced a `remmina.pref` carrying a locally generated key, and the
profile came back with an encrypted password beside the hand-set username.

So the key is born on the terminal. **Nothing secret has to travel between
machines**, every terminal gets its own key rather than sharing one, and the
install needs no copy step for it. This is the better of the two outcomes the
test was written to distinguish.

What it does not buy: the key still sits on the same machine as the secret it
protects, readable by anyone who can read both files. Per-terminal keys mean
that someone taking one terminal's files learns one terminal's password rather
than every terminal's — worth having, and still a long way from what R-14
promises.

## Test 7 — does it survive a reboot?

```sh
systemctl set-default encore-kiosk.target
reboot
```

**Pass:** the machine comes back to the remote login screen with nobody
touching it.

This is the one that matters for a terminal in a child's room, and it is the
only way to test the console fix honestly — the failure found on 2026-09-14
only appears when nobody is sitting at the console holding it.

## Test 8 — where does this machine read the global certificate file?

Both of these must be run **before** anything is pinned. The path below was
confirmed on a different distribution, never on the one a terminal has actually
been built on.

```sh
man xfreerdp 2>/dev/null | grep -i -A3 "certificates.json\|/etc/FreeRDP"
ls -la /etc/FreeRDP/ 2>&1
```

**Why it cannot be skipped:** a pin written to a path the library does not read
is inert, and an inert pin means the terminal goes on accepting any certificate
— while the record says it is pinned. That is a failure in the unsafe
direction, and nothing on the machine would report it.

**Pass:** the path the installed library actually reads is established, in
writing, from that machine.

## Test 9 — what does the screen show when the handshake is refused?

**This one decides whether certificate pinning is worth doing at all.**

Set a deliberately wrong fingerprint so verification must fail, then watch the
terminal's screen — not the journal, the screen:

```sh
systemctl restart encore-kiosk.service
```

**The question:** does anything appear that a person could click? A connection
error, a message, a dialog — or does the screen stay blank?

The claim to be tested is that a hard refusal fails below the client, so no
dialog can be constructed and nothing clickable reaches the screen. If that
holds, pinning closes a hole and leaves the kiosk promise intact. **If anything
clickable appears, pinning has moved the breach rather than fixed it** — and
the one time this product's screen was watched, it disagreed with every other
channel about what was happening.

Run Test 2 and Test 3 again afterwards: the same refusal path is what a dropped
connection and a broken profile would travel down.

## Test 10 — does running setup again leave a working terminal?

On a machine that is already a working terminal, run the install a second time
without changing anything about the target.

```sh
cd ~/encore
sudo ./encore-install.sh
```

**Pass:** the terminal still reaches a session afterwards, with no manual repair.
Check that it did not quietly lose anything on the way:

```sh
sudo grep -c '^password=.\+' /var/lib/encore/.local/share/remmina/*.remmina
sudo grep -c '^secret=' /var/lib/encore/.config/remmina/remmina.pref
find /var/lib/encore/.local/share/remmina -name '*.remmina' | wc -l
```

The stored password and the key must still be there, and there must still be
exactly one profile — a second one means the terminal's target is now whichever
file is found first.

**Why this matters:** re-running setup is the supported way to update a terminal
whose target certificate has changed (D-031). It is a promise the record makes
and has never watched being kept.

## Test 11 — does the probe agree with the target?

`encore-probe.py` is proved against a fake server by `encore-probe-test.py`
(`python3 encore-probe-test.py`, no network, no root). **What no test on this
machine can prove is that a real target behaves as the one observed target
did.** That is what this test is for, and only one far end has ever been spoken
to (Q-11).

**Which Python ran it is part of the result.** On 2026-09-23 the suite was run
on the development machine under 3.10.21, 3.11.16 and 3.14.7, and passed on all
three. It is worth saying because it has not always: a defect found in review
made the probe exit 1 with a traceback on a doubled-dot hostname under 3.10 and
3.11, while the same code passed the whole suite under 3.14 — CPython rewrote
the IDNA codec's exception in 3.14. So a pass on the interpreter in front of you
is not a pass on the interpreter a terminal has. No minimum version is recorded
anywhere, and the shebang is a bare `#!/usr/bin/python3`; write down which
Python answered `python3 -V` on any machine you run this on.

Run it on the terminal, against the host ADR-0008 recorded:

```sh
python3 ~/encore-probe.py <host>
python3 ~/encore-probe.py <host>
python3 ~/encore-probe.py --expect ed47d1c3744afa9ffa86d80f3dfbe7a2be67c34e4b171e5fe5a61fec5ed5ef41 <host>; echo $?
python3 ~/encore-probe.py --expect ed47d1c3744afa9ffa86d80f3dfbe7a2be67c34e4b171e5fe5a61fec5ed5ef40 <host>; echo $?
```

**Pass:** the first two print
`ed47d1c3744afa9ffa86d80f3dfbe7a2be67c34e4b171e5fe5a61fec5ed5ef41` and print the
*same* thing as each other; the third exits `0`; the fourth — one character
different — exits `10` and prints nothing at all on stdout.

**Repeatability is the point of running it twice.** A fingerprint that changes
between two runs a second apart cannot be pinned, and everything built on top
of it (7b, 7d) is then built on sand.

Write down what a *different* kind of target says, too, if one is available —
`xrdp` or `gnome-remote-desktop`. Exit `6` ("no TLS offered") and exit `8`
("TLS handshake failed") are the two opposite mistakes the probe could make
against a far end nobody has tried, and this test is the only thing that would
find them.

## Test 12 — does the sound guard tell a live sound server from a socket a dead session left?

The guard in `start_sound` used to ask "does this file exist?", and on a restart
a socket left by the session that had just ended answered yes with nothing
listening behind it — so no server was started and the terminal was silent while
the runner reported success (backlog item 5c). `socket_is_listening` in
`encore-kiosk.sh` replaces that test. **Everything else about the sound path
rests on these answers**, so they are measured rather than assumed.

### 12a — the mechanism, off-target

Runs anywhere with `python3` and `sh`. **No VM, no Pi, no service, nothing at
risk** — the sockets are fabricated in a temporary directory.

```sh
D=$(mktemp -d)
sleep 60 | python3 -c 'import socket,sys; s=socket.socket(socket.AF_UNIX); s.bind(sys.argv[1]); s.listen(1); input()' "$D/live" &
sleep 1
: > "$D/plainfile"
python3 -c 'import socket,sys; s=socket.socket(socket.AF_UNIX); s.bind(sys.argv[1])' "$D/dead"
```

**The `sleep 60 |` is not decoration.** The listener holds itself open by
blocking on `input()`, so with no stdin it reads end-of-file at once, exits with
an `EOFError` traceback, and leaves a socket with nothing behind it. That is
indistinguishable from the bug under test — a `1` for `$D/live` — except for the
traceback. It happened on the first run of this test on 2026-09-29. If `live`
answers anything but `0`, check the listener is still alive before believing the
mechanism is wrong.

Then, with `socket_is_listening` in scope, take the exit status for each of the
five cases — the fifth with `python3` hidden from `PATH`:

```sh
socket_is_listening "$D/live";      echo "live $?"
socket_is_listening "$D/dead";      echo "dead $?"
socket_is_listening "$D/plainfile"; echo "plainfile $?"
socket_is_listening "$D/missing";   echo "missing $?"
( PATH=/nonexistent; socket_is_listening "$D/dead"; echo "dead-no-python3 $?" )
sh -n encore-kiosk.sh
```

**Pass** is all five of these, and `sh -n` silent:

| Path | Required status | What a wrong answer proves |
|---|---|---|
| `$D/live` | `0` | the mechanism cannot see a listener, so the guard would start a second server beside a working one — the one way this change could break a machine that was fine |
| `$D/dead` | `1` | the mechanism cannot see a dead socket, so item 5c is not fixed |
| `$D/plainfile` | `1` or `3` | either is acceptable: a regular file at a socket path is not a listener. **`0` is a failure** |
| `$D/missing` | `2` | absence is being confused with something else |
| `$D/dead`, `python3` off `PATH` | `3` | the conservative branch is unreachable, and a machine with no `python3` would take a decision on no evidence |

**Run it on the test VM as well as on a workstation, and write down which.** The
development machine is Fedora, where `/bin/sh` is `bash`; the target is
Debian-family, where it is `dash`, and the heredoc inside a shell function is
exactly the construct that could differ. A pass on `bash` is not a pass on
`dash`.

**Passed on 2026-09-29, on the author's Fedora workstation**, with the function
text extracted from `encore-kiosk.sh` itself rather than retyped: `live` → 0,
`dead` → 1, `plainfile` → 1, `missing` → 2, `dead` with `python3` off `PATH` →
3. Run twice, under `bash` 5.3.9 as `/bin/sh` and under `dash` 0.5.13.1, with
the same five answers both times — so the heredoc-inside-a-function holds in
`dash` the interpreter. `sh -n encore-kiosk.sh` and `dash -n encore-kiosk.sh`
were both silent.

The two callers were exercised on the same fabricated sockets, under both
shells, and all of this held:

| Call | Result |
|---|---|
| `claim_socket_path` on the live socket | logged `already listening … leaving it alone`, returned 1, **and the socket was still there afterwards** |
| `claim_socket_path` on the dead socket | logged `was left by a session that has ended … removing it`, returned 0, and the socket was gone |
| `claim_socket_path` on an absent path | returned 0 and logged nothing |
| `claim_socket_path` with `python3` off `PATH` | logged `could not be established`, returned 2, and removed nothing |
| `wait_for_socket` on the live socket, budget 5 | returned 0 in 0 seconds |
| `wait_for_socket` on a dead socket, budget 3 | returned 1 after 3–4 seconds — **it did not return success instantly, which is the second half of item 5c** |
| `wait_for_socket` on an absent path, budget 2 | returned 1 after 2 seconds |

**What this does not cover:** `dash` on the target's own image, and every branch
of `start_sound` above the function level. Those are 12b.

### 12b — a restart gets its sound back, on the test VM

The point of item 5c, and it cannot be proved off-target. Copy the runner to
`/usr/local/bin/encore-kiosk.sh`, mode 755, then:

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

**Pass:** the second restart logs `removing it` and then `sound: server ready`,
exactly one of each helper is running, and there is no
`rdpsnd: Loaded alsa backend`.

Three failures that mean different things:

- `already listening … leaving it alone` — something really was listening, so
  the socket in the 2026-09-29 report was live and the diagnosis of item 5c is
  wrong. **Stop and report.**
- `SOUND UNAVAILABLE: … could not be established` — `python3` is missing on that
  machine. Not a code fault; it is the branch designed for it, and it leaves the
  machine no worse than before the fix.
- **More than one of any helper** — the guard let a second server start beside a
  first. **Stop immediately**; this is the harm the product named.

**Never run.** Needs a person at the test VM.

## Test 13 — is `/run/user/<uid>` reused across a restart?

Not a blocker for item 5c — the guard tests liveness rather than lifetime, so it
is correct either way. Run it because it decides whether *other* existence tests
in this repository are suspect.

```sh
U=$(id -u encore)
stat -c '%i %W %Z %n' /run/user/$U /run/user/$U/pulse /run/user/$U/pulse/native
systemctl restart encore-kiosk.service
sleep 8
stat -c '%i %W %Z %n' /run/user/$U /run/user/$U/pulse /run/user/$U/pulse/native
```

- **Same inode and birth time for `/run/user/$U` across the restart** — the
  runtime directory outlives the session. That explains the measured bug, and it
  means no existence test anywhere in `start_sound` meant what it appeared to
  mean.
- **A different inode** — the directory was torn down and recreated, and the
  socket seen ten seconds after a session ended came from somewhere this project
  has not identified. **Stop and report.** The fix still stands; the bug's
  mechanism would be unexplained, which is worth knowing before more is built on
  it.
- **`stat` says a path does not exist** — record which of the three, and when,
  and carry on. That is a fact about timing, not a failure.

**Never run.** Needs a person at the test VM.
