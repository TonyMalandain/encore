# Tests

What to run on a converted machine, and what to write down. Run them in order;
each one assumes the ones before it passed.

**Expect some to fail.** Every failure here answers a question the project
cannot currently answer from its own records. A failure you write down is worth
more than a pass you assume.

Status column is what has actually been watched, not what is believed.

**Most statuses in tests 1 to 13 are apt-family observations. A Fedora machine
is now named in three of them** — tests 1 and 7 passed on Fedora 44 on
2026-10-05, and the two Fedora lines in test 12a are off-target mechanism
checks on a workstation rather than on a converted machine.

**D-036 claimed the dnf family on 2026-10-04, and on 2026-10-05 the claim was
caught up with.** A Fedora terminal has shown a session, kept it across a
reboot, resolved `openh264` rather than the stub, and behaved identically with
SELinux enforcing and not enforcing. Test 14 is answered in both halves.
**What is still unwatched on dnf is tests 3, 4, 5 and 10** — notably sound, and
notably the off-switch, which is the product's reversibility promise and has
never been watched on *either* family.

| Test | What it answers | Status |
|---|---|---|
| 1 | Does a session appear at all? | Passed, VM, 2026-09-14 and again 2026-09-23 from a clean install · **Passed on the dnf family** — Fedora 44, 2026-10-05, reported by the author: the screen showed the session, with no keyring prompt, no dialog and not the client's own window. **This is the first time this test has answered yes on a family other than apt** |
| 2 | What happens when the connection drops? | Never run |
| 3 | What happens with no profile? | Failed as expected, VM, 2026-09-14 |
| 4 | Does the off-switch give the machine back? | **Never run, on either family** — and since 2026-10-05 the uninstaller has family-dependent behaviour of its own, so this row now covers two unwatched things rather than one. The package list it prints is checked off-target by 14a check 7; **an uninstall itself has never been watched anywhere.** R-11 is the product's reversibility promise and this is the test behind it |
| 5 | Is there sound? Three parts: 5a out, 5b in, 5c a terminal with no microphone | **5a passed, including across restarts** — VM and Mac Mini, 2026-09-29; the restart failure was item 5c and is fixed and observed fixed, VM, 2026-09-30 · **5b channel loads** — the input channel came up on the intended sound system, VM, 2026-09-30; nobody has spoken into it · 5c never run |
| 6 | Must the encryption key travel between machines? | Answered no, VM, 2026-09-23 |
| 7 | Does it survive a reboot? | **Passed on the dnf family** — Fedora 44, 2026-10-05, reported by the author: the machine was rebooted and came back into a working session by itself, with nothing done by hand · **never run on apt**, which is the odd result here: the family this product has shipped on longest has never had its reboot watched, and the newer one has |
| 8 | Where does this machine read the global certificate file? | Never run |
| 9 | What does the screen show when the handshake is refused? | Never run |
| 10 | Does running setup again leave a working terminal? | Never run |
| 11 | Does the probe agree with the target? | Never run |
| 12 | Does the sound guard tell a live sound server from a socket a dead session left? | **12a passed** — Fedora workstation, `bash` and `dash`, 2026-09-29 · **12b passed** — VM, 2026-09-30, twice on consecutive fast restarts: both sockets found stale, both removed, server started, five output devices · 12a never run on the test VM, and no longer needs to be |
| 13 | Is `/run/user/<uid>` reused across a restart? | **Answered: yes** — VM, 2026-09-30, by 12b rather than by this procedure. Sockets from an ended session were still present, so the directory outlives the session and no existence test in `start_sound` ever meant what it appeared to |
| 14 | Does a dnf-family machine convert and run? | **Answered: yes, both halves.** 14a passed off-target (seven checks) · **14b converts** — Fedora 44 VM, 2026-10-05, watched from `==> package manager: dnf` to `Installed.` · **14b runs** — Fedora 44, 2026-10-05, the screen showed a session (test 1) and kept it across a reboot (test 7) · **`openh264` won, not the stub** — the re-run put the eighth package on the machine and `rpm -q openh264 noopenh264` showed the stub absent, so no line of the install is unexercised any more · **14c passed** — the screen was the same with SELinux enforcing and not enforcing, which was the stated prerequisite before a Fedora terminal could be called working · still unrun on dnf: tests 3, 4, 5 and 10 |

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

One part of this script can be checked without a converted machine: the list of
packages it says it left behind differs by family, and 14a check 7 runs those
shipped lines for each family off-target.

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

## Test 14 — does a dnf-family machine convert and run?

Three parts, and only the first can be run without a Fedora machine. D-036
claimed the dnf family; **nothing on it has been watched**, so this test is
where that gets paid off rather than assumed.

### 14a — off-target: no Fedora terminal needed

Seven checks. Each one runs against the real shipped files, or against fabricated
inputs in a temporary directory where the point is the mechanism rather than
the file. Nothing is installed, and **no fabricated file ever stands in for
something the product ships or the system provides** — a copy of a shipped file
used as test input is not a substitute for the installed one, and is said so
each time it appears.

1. **The installer still parses, on both shells the targets use.** `/bin/sh` is
   `bash` on one machine in this project and `dash` on another, and that has
   mattered before.

   ```sh
   sh -n encore-install.sh && dash -n encore-install.sh && echo "syntax ok"
   ```

   **Pass:** `syntax ok`.

2. **The unit still parses, and no key in it is being ignored.** Two halves,
   and the first one exists because **the obvious form of this check cannot
   fail.** It was first written as the *absence* of two strings — no
   `Unknown key`, no `InaccessiblePaths` — and
   `systemd-analyze verify ./nope.service` on a unit that does not exist
   satisfies both: it prints `Unit nope.service not found.` and neither string
   appears. A typo in the filename, a renamed unit or a missing
   `systemd-analyze` all read as a pass. So the verifier is first made to say
   something that proves it parsed this very unit, and only then is silence
   worth anything.

   **(a) The control: the verifier is present, and it is reading our unit.** A
   misspelled copy in a temporary directory — fabricated input, never a
   substitute for the shipped file, which is left untouched:

   ```sh
   T=$(mktemp -d)
   sed 's/^InaccessiblePaths=/InaccesiblePaths=/' encore-kiosk.service > "$T/encore-kiosk.service"
   echo "misspelled: $(grep -c '^InaccesiblePaths=' "$T/encore-kiosk.service")"
   echo "complaints: $(systemd-analyze verify "$T/encore-kiosk.service" 2>&1 | grep -c "Unknown key 'InaccesiblePaths'")"
   rm -rf "$T"
   ```

   **Pass:** the two numbers are equal and **not zero** — one complaint per
   suppression line in the unit, whatever that number grows to. A zero, or a
   mismatch, voids half (b) entirely: it means the verifier did not read the
   keys, so its silence about the real unit proves nothing.

   **(b) The real shipped unit, with the one known-benign line filtered out:**

   ```sh
   systemd-analyze verify ./encore-kiosk.service 2>&1 | grep -vF 'Command /usr/bin/cage is not executable'
   ```

   **Pass:** **no output at all.** Stated positively like this, anything the
   verifier says is a failure — including `Unit … not found.`, which is how the
   earlier wording let a missing file through. On a machine without the client
   installed the filtered line is expected and is not a fault: `cage` is
   installed by the conversion, not by this check.

   **Read the output, never the exit status.** It is 0 while warning about a
   misspelled key, and 1 purely because `cage` is absent — measured both ways
   on Fedora 44 on 2026-10-04 — so neither value is evidence either way.

3. **The family block really produces the right family and the right package
   names, on a real machine of each family.** This runs the shipped lines
   themselves:

   ```sh
   { echo 'die() { echo "error: $*" >&2; exit 1; }'
     sed -n '/^# >>> family block/,/^# <<< family block/p' encore-install.sh
     echo 'echo "$PKG_FAMILY|$SSH_UNIT|$PACKAGES"'
   } | sh
   ```

   **Pass**, on a Fedora machine — read-only, nothing installed. Eight names:
   the seven both families need, plus `openh264`, which **only the dnf side
   asks for**. On Fedora the automatic `libopenh264.so.8` requirement under
   `freerdp-libs` is satisfied by default from Fedora's own repositories by
   `noopenh264`, **a stub that links and decodes nothing**, so the install is
   clean and the session is unusable. Naming `openh264` swaps the stub out
   (it carries `Obsoletes: noopenh264 < 1:0`) from
   `fedora-cisco-openh264`, which is enabled by default — no third-party
   repository. This makes **software** decoding work; the client is built
   `WITH_VAAPI=OFF` and this is not hardware acceleration:

   ```
   dnf|sshd|remmina remmina-plugins-rdp cage kbd pipewire pipewire-pulseaudio wireplumber openh264
   ```

   **Pass**, on the apt test VM — seven names, and **no `openh264`**: Debian
   and Ubuntu ship the real `libopenh264` in main with no stub beside it:

   ```
   apt|ssh|remmina remmina-plugin-rdp cage kbd pipewire pipewire-pulse wireplumber
   ```

   **And the empty variable must vanish, not become an empty argument.** The
   apt side leaves `$H264_DECODER` empty inside one unquoted `$PACKAGES`, and
   an empty string reaching `apt-get install` as its own argument is a
   different thing from one that is not there. Counted, not reasoned about —
   seven arguments on apt, eight on dnf, and every one of them non-empty:

   ```sh
   { echo 'die() { echo "error: $*" >&2; exit 1; }'
     sed -n '/^# >>> family block/,/^# <<< family block/p' encore-install.sh
     echo 'set -- $PACKAGES; echo "args=$#"; for a in "$@"; do [ -n "$a" ] || echo "EMPTY ARGUMENT"; done'
   } | sh
   ```

   **Pass:** `args=8` on Fedora, `args=7` on the apt test VM, and **no
   `EMPTY ARGUMENT`** on either.

   And the machine with neither, which needs no machine of its own — the
   fragment runs with an empty `PATH`, so `command -v` finds nothing. `sed`
   keeps the real `PATH`; only the fragment loses it. **The interpreter must be
   named absolutely** — `env PATH=/nonexistent sh` cannot find `sh` either, and
   gives exit 127 and a misleading `env: 'sh': No such file` instead of the
   check you wanted.

   ```sh
   { echo 'die() { echo "error: $*" >&2; exit 1; }'
     sed -n '/^# >>> family block/,/^# <<< family block/p' encore-install.sh
     echo 'echo "NOT REACHED"'
   } | env PATH=/nonexistent /bin/sh; echo "exit=$?"
   ```

   **Pass:** `error: no supported package manager found…`, `exit=1`, and **no
   `NOT REACHED`**.

4. **The coverage check finds a missing path, and says which.** Fabricated
   inputs only, in a temporary directory:

   ```sh
   T=$(mktemp -d)
   mkdir -p "$T/usr/lib/x86_64-linux-gnu/remmina/plugins" "$T/usr/lib64/remmina/plugins"
   touch "$T/usr/lib/x86_64-linux-gnu/remmina/plugins/remmina-plugin-secret.so" \
         "$T/usr/lib64/remmina/plugins/remmina-plugin-secret.so"
   find "$T/usr/lib" "$T/usr/lib64" -name 'remmina-plugin-secret.so' | sed 's|^|-|' | tr '\n' ' '
   ```

   **Pass:** both paths, each `-` prefixed, on one line. Then the `grep` half,
   against a copy of the real unit in `$T` — a copy used as test input, never a
   substitute for the installed one:

   ```sh
   cp encore-kiosk.service "$T/u"; grep -qF -- "InaccessiblePaths=-/usr/lib64/remmina/plugins/remmina-plugin-secret.so" "$T/u" && echo covered
   grep -v 'lib64' "$T/u" > "$T/u2"; grep -qF -- "InaccessiblePaths=-/usr/lib64/remmina/plugins/remmina-plugin-secret.so" "$T/u2" || echo "missing, as it should be"
   rm -rf "$T"
   ```

   **Pass:** `covered`, then `missing, as it should be`. The second half is the
   red case: without it, the check has never been seen to fail.

5. **An empty `InaccessiblePaths=` is accepted**, which is the case where the
   plugin is not installed at all. One command, on the apt test VM — running a
   transient unit is not read-only inspection, so it does not belong on the
   author's workstation, which is the RDP target and out of scope (D-002):

   ```sh
   systemd-run --quiet --pipe -p "InaccessiblePaths=" /bin/true; echo "exit=$?"
   ```

   **Pass:** `exit=0`.

6. **The plugin search runs late enough to find anything.** This is a
   regression check on the order of the installer's own lines, and it exists
   because the first attempt at this ticket got it wrong: the search was put
   where the old static path used to be computed, 138 lines above the step that
   uses it and *before the packages step installs the client*. On a machine
   being converted for the first time the plugin does not exist yet, so the
   search found nothing, nothing was suppressed, and the install died at `no
   password stored in the profile` — the exact defect the ticket exists to
   remove, on both families, because apt and dnf both install weak
   dependencies by default and the secret plugin is one
   (`dnf -q repoquery --recommends remmina` lists `remmina-plugins-secret`,
   Fedora 44, 2026-10-04).

   **The mechanism — a filesystem query answers differently before and after
   the file exists.** Fabricated tree, nothing mocked, nothing installed:

   ```sh
   T=$(mktemp -d); mkdir -p "$T/usr/lib/remmina/plugins"
   echo "before: [$(find "$T/usr/lib" "$T/usr/lib64" -name 'remmina-plugin-secret.so' 2>/dev/null | sed 's|^|-|' | tr '\n' ' ')]"
   touch "$T/usr/lib/remmina/plugins/remmina-plugin-secret.so"
   echo "after:  [$(find "$T/usr/lib" "$T/usr/lib64" -name 'remmina-plugin-secret.so' 2>/dev/null | sed 's|^|-|' | tr '\n' ' ')]"
   rm -rf "$T"
   ```

   **Pass:** `before: []` and `after:` carrying the one `-` prefixed path. The
   `before` line is what the installer saw on a fresh target when the search
   ran too early. Note that `$T/usr/lib64` does not exist in this tree, which
   is also the apt case — `2>/dev/null` swallows find's complaint and the
   surviving root is still searched.

   **The order, in the shipped file.** Addressed by content, not by line
   number, so it does not drift:

   ```sh
   awk '/^echo "==> packages"/{p=NR} /^SECRET_PLUGINS=/{f=NR} /^echo "==> password"/{w=NR} END{print (p && f && w && p<f && f<w) ? "find runs between packages and password" : "WRONG ORDER: packages=" p " find=" f " password=" w}' encore-install.sh
   ```

   **Pass:** `find runs between packages and password`. Any other output means
   the search has been moved back up to sit with the other variable
   assignments — which reads tidier and reinstates the defect.

7. **The uninstaller's list of what it left behind is true on the family it
   prints on.** `encore-uninstall.sh` removes no packages — that is R-11 and is
   correct — so it names them instead, for somebody who wants to clean up by
   hand. A list written from one family's names is wrong on the other in both
   directions at once: it gives two packages that do not exist and hides one
   that does, and a wrong name defeats the only use the list has.

   **The uninstaller still parses, on both shells the targets use** — the same
   reason as check 1, for the other shipped script:

   ```sh
   sh -n encore-uninstall.sh && dash -n encore-uninstall.sh && echo "syntax ok"
   ```

   **Pass:** `syntax ok`.

   **The shipped lines themselves, run for each family, with the package
   manager fabricated.** Three stub trees under `mktemp -d`, each holding one
   executable called `apt-get` or `dnf` or nothing at all, and `PATH` pointing
   at exactly one of them. The stubs are never run — `command -v` only asks
   whether they are there — and they stand in for nothing the system provides,
   because the thing under test is the question, not the package manager.
   **The interpreter is named absolutely**, for the reason check 3 gives.
   `set -eu` is prepended so a branch that forgets a variable fails here
   instead of at the end of somebody's uninstall:

   ```sh
   T=$(mktemp -d)
   echo "block lines: $(sed -n '/^# >>> leftovers block/,/^# <<< leftovers block/p' encore-uninstall.sh | grep -c .)"
   for pm in apt-get dnf none; do
     mkdir -p "$T/$pm"
     [ "$pm" = none ] || { printf '#!/bin/sh\nexit 0\n' > "$T/$pm/$pm"; chmod +x "$T/$pm/$pm"; }
     { echo 'set -eu'
       sed -n '/^# >>> leftovers block/,/^# <<< leftovers block/p' encore-uninstall.sh
       echo 'echo "'"$pm"'|$LEFT_PACKAGES|$LEFT_UNNAMED"'
     } | env PATH="$T/$pm" /bin/sh; echo "  exit=$?"
   done
   rm -rf "$T"
   ```

   **`block lines:` is the control, and it must not be zero.** Without it this
   check is the empty-list trap again: a renamed marker or a moved block makes
   `sed` print nothing, and a pass condition phrased as "no wrong names" is
   satisfied by a run that executed no shipped line at all. Stated positively
   instead — these three lines exactly, and `exit=0` under each:

   ```
   apt-get|remmina remmina-plugin-rdp cage kbd pipewire pipewire-pulse wireplumber|
   dnf|remmina remmina-plugins-rdp cage kbd pipewire pipewire-pulseaudio wireplumber openh264|
   none|remmina cage kbd pipewire wireplumber|the RDP plugin, the PulseAudio shim and any H.264 decoder
   ```

   **The two lists agree with the installer's.** `encore-install.sh` is what
   installed these packages, so it is the authority on their names and the
   uninstaller's copy is the thing that can be wrong. Compared as strings, on a
   machine of the family being compared — it answers for that family only:

   ```sh
   T=$(mktemp -d); mkdir -p "$T/dnf"; printf '#!/bin/sh\nexit 0\n' > "$T/dnf/dnf"; chmod +x "$T/dnf/dnf"
   INST=$({ echo 'die() { echo "error: $*" >&2; exit 1; }'
            sed -n '/^# >>> family block/,/^# <<< family block/p' encore-install.sh
            echo 'echo $PACKAGES'; } | sh)
   UNIN=$({ echo 'set -eu'
            sed -n '/^# >>> leftovers block/,/^# <<< leftovers block/p' encore-uninstall.sh
            echo 'echo $LEFT_PACKAGES'; } | env PATH="$T/dnf" /bin/sh)
   echo "installer:   [$INST]"; echo "uninstaller: [$UNIN]"
   [ "$INST" = "$UNIN" ] && echo "AGREE" || echo "DISAGREE"
   rm -rf "$T"
   ```

   **Pass:** `AGREE`, with both lists printed so a disagreement says which name.

   **And every name exists, asked of the machine rather than of this file.**
   String equality between two files written by the same hand proves only that
   the hand was consistent. This asks the package database, read-only, nothing
   installed:

   ```sh
   for p in $UNIN; do
     if [ -n "$(dnf -q repoquery --qf '%{name}' "$p" 2>/dev/null)" ]
     then printf '  exists            %s\n' "$p"
     else printf '  NO SUCH PACKAGE   %s\n' "$p"; fi
   done
   ```

   **Pass:** `exists` against all eight on a dnf machine, and no
   `NO SUCH PACKAGE`. The apt equivalent is
   `apt-cache show "$p" >/dev/null 2>&1` and is unrun — it needs the apt test
   VM, and nothing here can stand in for it.

   **And no printed line is wider than 72 columns.** A correct name broken
   across a line wrap is as useless to copy as a name that does not exist, and
   the screen this message is most likely to be read on is the narrowest one
   the product mentions: `README.md` sends somebody whose terminal will not
   start to a text console on `Ctrl+Alt+F1`..`F6`, which is 80 columns. The
   list is computed and has already grown by one name, so the width is
   asserted rather than eyeballed. This runs the block **and the `echo` lines
   after it**, up to but not including `LEFT=0`:

   ```sh
   T=$(mktemp -d)
   for pm in apt-get dnf none; do
     mkdir -p "$T/$pm"
     [ "$pm" = none ] || { printf '#!/bin/sh\nexit 0\n' > "$T/$pm/$pm"; chmod +x "$T/$pm/$pm"; }
     printf '%-8s ' "$pm"
     { echo 'set -eu'
       sed -n '/^# >>> leftovers block/,/^LEFT=0/p' encore-uninstall.sh | sed '$d'
     } | env PATH="$T/$pm" /bin/sh |
     awk '{ n++; if (length($0) > m) m = length($0) } END { printf "lines: %d, widest: %d%s\n", n+0, m+0, (n+0 > 0 && m+0 <= 72) ? "" : "   <-- FAIL" }'
   done
   rm -rf "$T"
   ```

   **`lines:` is this half's control, and it must not be zero.** An awk
   `END` block over no input prints `widest: 0`, and 0 is under 72 — so a
   broken `sed` range, a renamed marker or a script that died before printing
   all read as a pass on width alone. **Pass:** `lines: 7` on apt and dnf,
   `lines: 10` on the `none` arm, `widest: 69` on all three, and no `FAIL`.
   Both `/bin/sh` and `dash` must give the same numbers — `${#CAND}` is what
   places the breaks, and it counts bytes in one shell and characters in the
   other.

**Results, 2026-10-04, on the author's Fedora 44 workstation — read-only,
nothing installed, no `encore` identity created, `encore-install.sh` not run:**

- **Check 1 passed.** `syntax ok`, under `bash` 5.3.9 as `/bin/sh` and under
  `dash` 0.5.13.1.
- **Check 2 passed, and was watched failing first — in both halves.** Half (a):
  the misspelled copy gave `misspelled: 4` and `complaints: 4`, the four
  complaints naming the copy's own path and lines 35 to 38
  (`Unknown key 'InaccesiblePaths' in section [Service], ignoring.`). Half (b)
  against the real unit: **no output**, once the expected
  `encore-kiosk.service: Command /usr/bin/cage is not executable: No such file
  or directory` is filtered. Exit status 1 there, from the absent `cage` and
  nothing else.

  **The red, which is why this check was rewritten.** The earlier wording — the
  absence of `Unknown key` and of `InaccessiblePaths` — was satisfied by
  `systemd-analyze verify ./nope.service`: output `Unit nope.service not
  found.`, `exit=1`, `Unknown key` lines **0**, `InaccessiblePaths` lines
  **0**, so a run that never opened a unit file passed. Under the new wording
  the same command fails as it should: half (b) prints `Unit nope.service not
  found.` and the pass condition is no output. **The check had never been seen
  to fail, which is exactly why nothing exposed that it could not** — the same
  shape as the installer's coverage check reporting success over an empty list,
  and worse here, because this file's whole purpose is recording what was
  watched.
- **Check 3 passed on the dnf side and for the machine with neither.** The
  shipped fragment printed
  `dnf|sshd|remmina remmina-plugins-rdp cage kbd pipewire pipewire-pulseaudio wireplumber`,
  and with an empty `PATH` it printed
  `error: no supported package manager found: this needs apt-get or dnf (R-1)`,
  `exit=1`, and no `NOT REACHED`. **The apt side is unrun** — it needs the apt
  test VM, and nothing here can stand in for it. Before the family block
  existed the same command printed `||`, so the check has been seen failing.
- **Check 4 passed.** Both fabricated paths came back `-` prefixed on one line;
  the real unit answered `covered`, and the copy with the `lib64` line removed
  answered `missing, as it should be`.
- **Check 5 never run.** It starts a transient unit, which is not read-only, and
  the only Fedora machine available is the RDP target (D-002). The unit-file
  form of an empty `InaccessiblePaths=` was accepted by `systemd-analyze
  verify` on Fedora 44 on 2026-10-04; that is parsing, not running.
- **Check 6 was watched failing, then passing.** Against the first commit of
  this work the order half printed
  `WRONG ORDER: packages=136 find=97 password=235`; after the search was moved
  into the password step it prints `find runs between packages and password`,
  with the search at line 249 against the packages step at 124, the password at
  252 and the unit coverage loop at 282 — so both readers of `$SECRET_PLUGINS`
  are now downstream of it. The mechanism half printed `before: []` and then
  `after: [-…/usr/lib/remmina/plugins/remmina-plugin-secret.so]`, in a tree
  with no `usr/lib64` at all, and that pipeline exited 0 — so a missing search
  root is not a failure under `set -e`.
- **The unit coverage check in step 6 of the installer had the same fault, and
  the same move fixed it.** It greps the installed unit for every path
  `$SECRET_PLUGINS` holds, so while the search ran too early the list was empty
  on every first conversion, the loop body never ran, and the check reported
  success having examined nothing. It could not have failed. Nothing about the
  check itself changed; it is correct now only because the value it reads is
  gathered after the client is installed.

**Addendum, 2026-10-05, same machine and same conditions — read-only, nothing
installed, `encore-install.sh` not run. Check 3 grew the `openh264` name and
the argument count, and was watched failing first.**

- **Red.** Against the family block before the change, the first half printed
  `dnf|sshd|remmina remmina-plugins-rdp cage kbd pipewire pipewire-pulseaudio
  wireplumber` — no `openh264` — and the counting half printed `args=7` where
  the pass condition on dnf is `args=8`.
- **Green.** After the change the first half printed
  `dnf|sshd|remmina remmina-plugins-rdp cage kbd pipewire pipewire-pulseaudio
  wireplumber openh264` and the counting half printed `args=8` with no
  `EMPTY ARGUMENT`.
- **The empty variable was watched, not reasoned about.** The apt branch cannot
  run here, so the shipped `PACKAGES=` line itself was fed the apt side's
  values with `H264_DECODER=` empty: `args=7`, and the seven arguments printed
  as `[remmina][remmina-plugin-rdp][cage][kbd][pipewire][pipewire-pulse]`
  `[wireplumber]` with no eighth, empty one. **The apt side of check 3 proper
  is still unrun** — it needs the apt test VM.
- **The two facts the fix rests on, from `dnf -q repoquery` on Fedora 44.**
  `--whatprovides 'libopenh264.so.8()(64bit)'` lists both
  `noopenh264-0:2.6.0-4.fc44.x86_64` and `openh264-0:2.6.0-3.fc44.x86_64`, and
  `--obsoletes openh264` prints `noopenh264 < 1:0`.
- **This machine cannot demonstrate the defect and was not made to.** `rpm -q`
  says `openh264-2.6.0-3.fc44.x86_64` is installed and `noopenh264` is not, so
  it already carries the real decoder. The stub being what a *fresh* Fedora
  picks is a repository fact, shown by the two queries above; watching the
  unusable session itself belongs to 14b.

**Addendum, 2026-10-05, same machine and same conditions — read-only, nothing
installed, no `encore` identity created, neither `encore-install.sh` nor
`encore-uninstall.sh` run. Check 7 is new, and was watched failing first.**

- **Red, and it failed twice over.** Against the uninstaller before the change,
  `block lines: 0` — there was no block to run — and all three families printed
  `/bin/sh: line 2: LEFT_PACKAGES: unbound variable`, `exit=1`. The control is
  what makes that red legible: a bare "no wrong names were printed" would have
  been satisfied by those three runs, which printed no names at all.
- **Red, on the defect itself.** The names the old lines 123–124 printed, asked
  of this Fedora machine's package database, came back
  `NO SUCH PACKAGE  remmina-plugin-rdp` and
  `NO SUCH PACKAGE  pipewire-pulse`, with `remmina`, `cage`, `kbd`, `pipewire`
  and `wireplumber` existing, and `openh264` not printed at all. That is the
  reported defect reproduced as a measurement rather than as an argument: two
  names a Fedora reader cannot act on, one package on the machine the list did
  not mention.
- **Green.** `block lines: 17`, and the three expected lines exactly, each
  `exit=0`. The `none` arm names the five packages both families spell the same
  and says in the message that the other three cannot be named here, rather
  than guessing a family.
- **The lists agree.** `AGREE`, both printing
  `remmina remmina-plugins-rdp cage kbd pipewire pipewire-pulseaudio wireplumber openh264`.
- **All eight names exist**, by `dnf -q repoquery`, with no `NO SUCH PACKAGE`.
- **The rendered message was read, not inferred** — the block plus its `echo`
  lines, run under the dnf stub tree:

  ```
  Removed. Still on this machine, deliberately:
    remmina remmina-plugins-rdp cage kbd pipewire pipewire-pulseaudio wireplumber openh264    (ordinary packages)
    the copied files in your home directory (encore-*.sh, *.service, …)
  ```

- **The width was the second red, found in review and fixed in the same
  ticket.** The first fix printed the computed list on one line, which was 111
  columns on dnf and 96 on apt where the two hand-wrapped lines it replaced
  were about 60. The width half of the check was run against it first and said
  so: `apt-get lines: 5, widest: 96 <-- FAIL`, `dnf lines: 5, widest: 111
  <-- FAIL`, `none lines: 8, widest: 74 <-- FAIL` — the `none` arm was over by
  two columns as well, which eyeballing had missed. **This matters on exactly
  the screen the product recommends for a terminal that will not start**: 80
  columns, and a name broken across the wrap is as useless to copy as a name
  that does not exist.
- **Green on width, and the same under both shells.** `lines: 7, widest: 69`
  for apt and dnf, `lines: 10, widest: 69` for `none`, with no `FAIL`, and
  byte-for-byte the same numbers under `/bin/sh` (bash 5.3.9) and
  `/usr/bin/dash` (0.5.13.1). The dnf list breaks after `pipewire,` and the
  apt list after `pipewire-pulse,`; neither break is written down anywhere, and
  the ninth name will move them without anyone editing a string. The widest
  line in all three arms is the pre-existing home-directory line, not the
  package list.
- **The rendered dnf message, read rather than inferred:**

  ```
  Removed. Still on this machine, deliberately:
    ordinary packages, which the machine may want for other reasons:
      remmina, remmina-plugins-rdp, cage, kbd, pipewire,
      pipewire-pulseaudio, wireplumber, openh264
    the copied files in your home directory (encore-*.sh, *.service, …)
  ```
- **The apt arm of this check is unrun** on a real apt machine, exactly as
  check 3's apt side is. What was watched here is the apt *arm of the block*,
  selected by a fabricated `apt-get`; whether those seven names exist in Debian
  or Ubuntu was not asked of any machine.

### 14b — a scratch Fedora machine converts

**Passed, both halves — Fedora 44, 2026-10-05.**

**The terminal half, reported by the author.** The screen showed the session —
no keyring prompt, no dialog, not the client's own window. The machine was
rebooted and came back into a working session by itself, with nothing done by
hand (test 7). And the re-run resolved the eighth package correctly:
`rpm -q openh264 noopenh264` showed `openh264` installed and the stub absent,
so **the `openh264` line is no longer unexercised code** and the fresh-Fedora
`noopenh264` defect is now watched being prevented rather than argued about
from repository metadata.

**Not watched on this machine, and not claimed:** tests 3, 4, 5 and 10. Sound
in particular — a session on the screen says nothing about whether it has
sound. And test 4, the off-switch, which has never been watched on either
family.

**One gap in this record, left open rather than guessed:** whether the terminal
half ran on the Fedora 44 virtual machine used for the install or on the
author's other Fedora machine. The version is recorded; the hardware is not.
That matters to one claim only — the README's "it has barely run on real
hardware" — and nowhere else, so it is noted here rather than resolved by
assumption.

**The install half**, watched end to end on a scratch Fedora 44 virtual
machine, by the author, from the printed output of `sudo ./encore-install.sh`.
Four things are observation rather than belief:

- **`==> package manager: dnf`** printed before anything was installed. The
  family block picked the dnf arm on a real dnf machine, not off-target.
- **The dnf install path ran and completed.** `dnf install -y -q $PACKAGES`
  resolved and installed the Fedora package names.
- **`remmina-plugins-secret` arrived as a weak dependency, exactly as
  predicted.** The log shows `Installing weak dependencies:` with
  `remmina-plugins-exec`, `remmina-plugins-secret` and `remmina-plugins-vnc`.
  This is the fact the whole keyring defect rests on: nobody asks for that
  plugin, so nobody expects it to be there.
- **`==> password` completed, and neither guard after it fired.** This is the
  line that matters most. **Before this ticket a Fedora install died exactly
  here**, with `no password stored in the profile`, because the plugin search
  ran before the packages step and found nothing. It completing is the proof
  that moving the search worked, and that the unit's `/usr/lib64` path is
  named correctly. The run ended `Installed.` with the expected
  `WARNING: the password appears in the journal.`

**What the install run did not cover, and the re-run did.** That first run was
made before `openh264` was added to the dnf arm in `cb94d97`: it installed
**seven** packages where the installer now asks for **eight**, so for a day the
`openh264` line was unwatched code and this section said so. The re-run closed
it. Kept here rather than deleted, because the gap is the useful part: **a test
run that predates the line it is cited as evidence for proves nothing about
that line**, and the record claimed a pass for a day while that was true. That
is `H-1` in `docs/architecture/constraints.md`, instance 6, now closed.

**And an install completing was never a terminal.** For the day between the two
runs, this file recorded a converting machine and no session, `R-1` stayed
`intended`, and item 16 stayed open. That was the right call and it is worth
noting that it held: the pressure to read a clean install as a working terminal
was real, and the record did not give way to it.

#### The procedure, for the next time

**All of this has now been run and passed on Fedora 44, 2026-10-05.** It is kept
because this test is the one that earns its keep on every change to the
installer, and because the next family — or the next Fedora release — needs the
same sequence rather than a fresh guess at it.

Needs a Fedora machine that can be snapshotted and reverted — not the author's
workstation, which is the RDP target and out of scope (D-002). Record, in order
and by observation:

- `==> package manager: dnf` appears before anything is installed. *(Watched
  2026-10-05. Confirm it again rather than assuming it — the point of a
  re-run is that the installer may have changed since.)*
- the eight dnf package names install. *(Watched 2026-10-05, all eight.)*
- **`openh264` is in the transaction, and `noopenh264` is not what satisfies
  `libopenh264.so.8`.** *(Watched 2026-10-05: `rpm -q openh264 noopenh264`
  showed the real package installed and the stub absent.)* This can only be
  checked on a fresh Fedora. The author's workstation already carries the real
  decoder, so it cannot show the defect and was never made to; and the
  2026-10-05 VM run happened before this package name existed. Read the
  transaction dnf prints, and then the installed truth:

  ```sh
  rpm -q openh264 noopenh264
  rpm -q --whatprovides 'libopenh264.so.8()(64bit)'
  ```

  **Watch for:** `openh264` installed, `noopenh264` **not installed**, and the
  provider of the library being `openh264`. If `noopenh264` is what is there,
  the stub won and the session will be unusable while the install reports
  success — the exact defect the `openh264` name in `$PACKAGES` exists to
  prevent. Note that `openh264` obsoletes the stub, so on a machine that
  already had `noopenh264` the transaction should show it being *replaced*,
  with no `--allowerasing` and no third-party repository: the real package
  comes from `fedora-cisco-openh264`, which Fedora enables by default.
  **Then watch the session**, because that is the only evidence that matters —
  and note that decoding here is on the processor either way; this makes
  software decoding work and is not hardware acceleration.
- the keyring suppression during the password step: `==> password` completes and
  neither of the two guards after it fires. **Before this ticket, Fedora
  stopped exactly here** — the password was not written into the profile and
  `no password stored in the profile` was the error — so this line is the one
  that proves the installer's `find` did its job. *(Watched 2026-10-05 — this
  is the line that turned red into green.)*
- the unit coverage check passes silently, or dies naming a path. *(Watched
  2026-10-05 by inference: the run reached `Installed.`, which is past the
  check. Silence is the pass condition here, so this is the weakest of the
  four observations — a check that passes by printing nothing looks identical
  to a check that did not run.)*
- **then the terminal.** *(Tests 1 and 7 watched 2026-10-05: a session on the
  screen, and a reboot that came back into one by itself.)* **Tests 3, 4, 5 and
  10 have still never been run on this family** — no profile, the off-switch,
  sound, and a repeated setup. Sound is the gap most likely to be noticed by
  whoever lives with the terminal; the off-switch is the one with the largest
  promise behind it (`R-11`) and it is unwatched on *both* families.

### 14c — does SELinux change what the screen shows?

**Passed — Fedora 44, 2026-10-05, reported by the author. The two screens were
the same.** So SELinux does not change what a Fedora terminal shows, and
`constraints.md` C-1 can now say that from a screen rather than from labels.

**What the pass covers, stated narrowly:** two screens, on one machine, once.
It is the strongest evidence available and it is not proof that no SELinux
refusal exists anywhere in this product on any Fedora machine — the policy
carries over a hundred `dontaudit` rules per domain, so a refusal can still be
silent. What it does rule out is the thing that mattered: SELinux making the
difference between a terminal that works and one that does not.

**This was the prerequisite the architect named before a Fedora terminal could
be called working** (`constraints.md` C-1). It is met. The procedure is kept
below for the next Fedora release.

Everything
measured there is policy and labelling; none of it is a terminal, and a refusal
can be invisible — that policy carries 102 `dontaudit` rules reaching
`unconfined_service_t`, 164 reaching `unconfined_t` and 121 reaching `init_t`,
**so a clean AVC log is not evidence of anything.** After 14b, on the same
machine:

```sh
getenforce
sudo setenforce 0 && getenforce
sudo systemctl isolate encore-kiosk.target      # watch the screen, write down what it shows
sudo setenforce 1 && getenforce
sudo systemctl isolate encore-kiosk.target      # watch the screen again
```

**Pass:** the two screens are the same. Then SELinux is out of the picture for
good and `constraints.md` C-1 can say so from observation. If they differ,
`sudo semodule -DB` to switch the `dontaudit` rules off, repeat the enforcing
run, and `sudo ausearch -m avc -ts recent` names the rule — then stop and hand
it to the architect, because a policy module is a Fedora-only component and
weakens D-036's one-implementation claim.

What this does **not** cover: `systemctl isolate` does not reproduce boot
conditions, so the enforcing/permissive comparison is this pair of isolates, and
a real Fedora reboot is test 7 on this family under 14b.
