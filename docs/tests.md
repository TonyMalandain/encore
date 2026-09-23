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
| 5 | Is there sound? | Never run |
| 6 | Must the encryption key travel between machines? | Answered no, VM, 2026-09-23 |
| 7 | Does it survive a reboot? | Never run |

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
