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
| 5 | Is there sound? | No, and why is now known — VM, 2026-09-27 |
| 6 | Must the encryption key travel between machines? | Answered no, VM, 2026-09-23 |
| 7 | Does it survive a reboot? | Never run |
| 8 | Where does this machine read the global certificate file? | Never run |
| 9 | What does the screen show when the handshake is refused? | Never run |
| 10 | Does running setup again leave a working terminal? | Never run |
| 11 | Does the probe agree with the target? | Never run |

---

## Test 1 — does a session appear?

```sh
systemctl status encore-kiosk.service
journalctl -u encore-kiosk.service -b --no-pager
```

**Pass:** the remote machine's login screen fills the terminal's screen.

**Do not trust `systemctl status`.** The runner loops forever, so the service
reports `active (running)` whatever is happening. Read the journal.

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

There will not be. The template sets `sound=off`, and two-way audio is decided
(D-009, D-014) but unbuilt. Recorded so nobody spends an evening on it.

When backlog item 5 is done, this test becomes: play something in the session
and confirm it comes out of the terminal's speakers, then speak into the
terminal's microphone and confirm the session hears it — with nobody having
chosen a device from a list.

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

**Answered on 2026-09-27, on a VM, with the capability running.** There is no
sound, and the cause was watched rather than reasoned. The sound software is
all present. What is absent is the per-user service manager for the terminal's
identity: the runtime directory held the graphical socket and nothing else —
no service-manager directory, no message bus, no sound socket — and the manager
itself reported inactive. The sound server starts on demand through that
manager, so nothing ever starts it.

Two things this does **not** settle. Whether the terminal can reach the sound
hardware once a server exists is a separate question nobody has got to, because
the session also holds no seat. And whether a terminal with no microphone stays
usable is still untested.
