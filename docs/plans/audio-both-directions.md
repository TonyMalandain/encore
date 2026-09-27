# Plan — audio in both directions, out of the box (`BACKLOG.md` item 5)

**Sensitive:** this touches **privilege and reversibility**, not credentials.
Candidate 2 writes a root-owned flag that grants the terminal's identity a
background service manager which outlives every login, and that file survives
deleting the account — it is the known trap against R-11. No secret is read,
written or logged anywhere in this ticket. Nothing here needs a new group, a new
capability, a device rule or a loosened sandbox: the access list on the sound
control device already names `encore` (observed 2026-09-27). **Do not add
`encore` to the `audio` group.** There is no server for that permission to apply
to, and adding it would be a privilege granted for nothing.

**Status of the evidence.** Everything called *observed* below was measured by
the author on a Mac Mini terminal on 2026-09-27 with the capability running.
Everything else is marked **unknown** or **inference** and has a command beside
it that would settle it. Nothing in this plan may be described as confirmed until
someone runs the command and writes the output into `docs/tests.md`.

---

## What changes, and for whom

For the person at the terminal — the owner's child: sound from the remote session
comes out of the speakers in front of them, and where the machine has a
microphone, the session hears them, so a call works. Nobody chooses a device at
either end. A terminal with no microphone stays fully usable.

For whoever converts a machine: nothing new to answer, nothing new to pick.

---

## The component

Two parts of the system are touched, and it matters which owns what.

- **`encore-kiosk.service` — responsible for:** starting the compositor as the
  terminal's identity in a session that owns the console. **Drift:** none of the
  interesting kind, but it has an **omission**: it declares no session type,
  so at the moment `pam_systemd` decides the session class the type is `tty`.
  **The change belongs here** because what kind of session the terminal runs in
  is precisely this unit's job, and nothing else in the product can state it.
- **`encore-kiosk.remmina.template` — responsible for:** being the baseline
  connection profile, generated verbatim from one observed working (its own
  header, lines 1–10). **Drift:** it carries `sound=off` and an empty
  `microphone=`, which nobody decided — they are properties of the machine the
  working profile came from (`docs/architecture/constraints.md` C-5). **The
  change belongs here** because switching audio on is a property of the shipped
  baseline, not of any one terminal.
- **`encore-install.sh` — responsible for:** what differs between terminals, and
  for refusing to finish if what it produced is not what it intended. Audio is
  *not* per-terminal, so the installer gets **no audio configuration** — only
  post-condition checks, and (candidate 2 only) the one persistent flag.

**Why the fault is where it is.** One fault, established by observation: nothing
starts a sound server for `encore`. The sound software is installed; the device
permission is granted; the session is active on `seat0`; but
`user@<uid>.service` is `inactive`, `/run/user/<uid>/` holds only the Wayland
socket and an empty `pulse/`, and `pactl info` gets `Connection refused`. The
sound server only ever starts through the per-user manager, and logind only
starts that manager for certain session classes. The session's class is
`user-light`.

**The one thing that is inference, not observation:** that the class is reduced
because the session type is `tty` at session-open time and only becomes `wayland`
later, by which point the class is stamped and never recalculated. Phase A
exists to prove or disprove exactly that, **before anything is built**.

---

## Sizing, honestly

| Part | Who | Cost |
|---|---|---|
| Phase A — prove the session class can be lifted | **a person at the terminal** | 30–45 min, several service restarts, screen watched each time |
| Phase B — get the two profile values from the client itself, then hear it | **a person**, one at a machine with a Remmina GUI, one at the terminal | 30 min |
| Phase C — the edits | engineer, mechanical, no hardware | under an hour |
| Phase D — Test 5 on the terminal | **a person at the terminal** | 15 min |
| The mic-less case | **a person, at a second machine that has no microphone** | untested, not deliverable in this ticket — see *What stays unknown* |

Phase C must not start until Phase A and Phase B have both produced written
outcomes. An engineer who starts at Phase C is guessing which candidate landed.

---

## Seams

There are no function signatures here; the seams are three contracts between the
shipped parts. Each is written to make one misuse impossible.

**Seam 1 — the unit states the session type (candidate 1 only).** Added to the
`[Service]` section of `encore-kiosk.service`, immediately below the existing
`Environment=HOME=/var/lib/encore`, with this comment and no other wording:

```ini
# The session class logind stamps at session-open decides whether this identity
# gets a per-user service manager, and the sound server only starts through
# that manager. encore is a system account, so without a declared session type
# the class is reduced and there is no sound. This line is why audio works.
# See BACKLOG.md item 5.
Environment=XDG_SESSION_TYPE=wayland
```

*Misuse it prevents:* somebody reads the unit, sees an environment variable that
looks cosmetic next to `GDK_BACKEND` in the runner, and deletes it as
duplication. The comment says it is load-bearing and names the symptom.

**Seam 2 — the profile's audio keys are asserted, not hoped for.** Added to
`encore-install.sh` at the end of section 5, **after** the
`remmina --update-profile` call, because that call rewrites the profile and is
the last thing that can change it:

```sh
# Audio must be on, and must be the terminal's own (D-009). sound=remote is one
# word away and sends the session's audio to the far machine, which is the exact
# outcome the product forbids — so check for it by name rather than trusting
# that the template said local.
grep -q '^sound=local$' "$PROFILE" \
    || die "audio is not switched on in the profile — expected sound=local"
if grep -q '^sound=remote' "$PROFILE"; then
    die "sound=remote sends the session's audio to $RDP_SERVER, not to this terminal"
fi
```

*Misuse it prevents:* a hand-edit, a botched regeneration of the template, or a
client that rewrote the key — any of which today would produce a converted
terminal that installs cleanly and is silent. This is the project's recurring
failure mode, and it is the whole reason this is a check and not a comment.

If Phase B yields a non-empty microphone value, one more line goes with it, using
the literal value B1 produced — no other value, no fallback:

```sh
grep -q '^microphone=<VALUE FROM B1>$' "$PROFILE" \
    || die "the microphone key is not what the template ships"
```

**Seam 3 — the uninstaller's removal list is the definition of "no trace".**
Whatever candidate lands, every path it creates is added both to the removal
section *and* to the `STILL PRESENT` loop at the end of `encore-uninstall.sh`.
Removing without re-checking is how R-11 quietly stops being true.

*Misuse it prevents:* a path that is removed but not verified, so a failed
removal prints "Nothing of Encore's remains".

---

## Phase A — prove the class can be lifted (a person at the terminal)

Run with the capability on and a session on the screen. **After every restart,
look at the screen.** The compositor taking the console on tty7 is the only
end-to-end result this project has, and candidate 1 changes the session it lives
in. Every step below has its undo written beside it.

Set this once per shell:

```sh
ENCORE_UID=$(id -u encore)
```

### A0 — reproduce the baseline first

```sh
loginctl list-sessions
loginctl show-session <the encore session id> -p Class -p Type -p Active -p Seat -p VTNr
systemctl is-active "user@$ENCORE_UID.service"
ls -a "/run/user/$ENCORE_UID/"
tr '\0' '\n' < "/proc/$(pgrep -u encore -x cage | head -n1)/environ" | grep -E 'XDG_|WAYLAND'
```

- **Expected, matching 2026-09-27:** `Class=user-light`, `Type=wayland`,
  `Active=yes`, `Seat=seat0`, `VTNr=7`; manager `inactive`; runtime directory
  holding only `dconf`, empty `pulse`, `wayland-0`, `wayland-0.lock`.
- **If it does not match** — in particular if the class is already `user` —
  **stop.** The diagnosis this plan is built on no longer describes the machine,
  and the plan must be re-read before anything is changed.
- **The `environ` line answers something nobody has looked at:** whether
  `XDG_RUNTIME_DIR` is present in the kiosk process. It is believed to be, since
  the compositor found `wayland-0` there, but that is inference. Write down
  whether it is set, and to what. It decides one line in Phase C.

### A1 — candidate 1a: declare the session type

Use a drop-in, never an edit to the shipped unit, so the undo is deleting one
file:

```sh
mkdir -p /etc/systemd/system/encore-kiosk.service.d
cat > /etc/systemd/system/encore-kiosk.service.d/99-audio-probe.conf <<'EOF'
[Service]
Environment=XDG_SESSION_TYPE=wayland
EOF
systemctl daemon-reload
systemctl restart encore-kiosk.service
sleep 10
```

Then, exactly:

```sh
loginctl list-sessions
loginctl show-session <the new encore session id> -p Class -p Type -p Active -p Seat -p VTNr
systemctl is-active "user@$ENCORE_UID.service"
ls -a "/run/user/$ENCORE_UID/"
sudo -u encore XDG_RUNTIME_DIR="/run/user/$ENCORE_UID" pactl info
```

Undo, at any point: `rm -f
/etc/systemd/system/encore-kiosk.service.d/99-audio-probe.conf && systemctl
daemon-reload && systemctl restart encore-kiosk.service`.

What each outcome means:

| What you see | What it means | Where to go |
|---|---|---|
| Session on the screen as before, `Class=user`, manager `active`, runtime dir now holds `systemd/`, `bus`, `pipewire-0`, `pulse/native`, and `pactl info` prints a server name | **Candidate 1a proven.** One line, nothing on disk, fully reversible | A4, then Phase B, then Phase C as **candidate 1** |
| `Class=user` and manager `active`, **but** `pactl info` still refuses and there is no `pulse/native` | The class was the cause and there is a **third fault** underneath — the account's socket units are not enabled | **Stop.** Do not improvise. Finding for the architect: enabling per-user socket units is a new mechanism with its own reversibility question |
| `Class=user-light` still | 1a disproven — the PAM environment is not reaching the class decision, or the class rule is not what was read from the source | A2 |
| Screen is black, or the service restart-loops, or `VTNr` is no longer 7 | 1a is **unsafe at any price** — it broke the only working result | Undo immediately, confirm the screen is back, then A3. Write down what broke; the architect needs it |

### A2 — candidate 1b: declare the class as well

Only if A1 left the class reduced. Same drop-in, both lines:

```sh
cat > /etc/systemd/system/encore-kiosk.service.d/99-audio-probe.conf <<'EOF'
[Service]
Environment=XDG_SESSION_TYPE=wayland
Environment=XDG_SESSION_CLASS=user
EOF
systemctl daemon-reload
systemctl restart encore-kiosk.service
sleep 10
```

Re-run the five measurements from A1 verbatim. Same outcome table. If the class
lifts here, **candidate 1b is proven** and Phase C ships *both* lines.

This is a variant of the architect's candidate 1, not a new mechanism: same file,
same kind of declaration, still nothing on disk. It is flagged to the architect
as an addition to their ranking rather than a decision taken behind them.

### A3 — candidate 2: keep the per-user manager alive

Only if neither A1 nor A2 lifted the class. Remove the drop-in first so there is
one variable:

```sh
rm -f /etc/systemd/system/encore-kiosk.service.d/99-audio-probe.conf
systemctl daemon-reload
loginctl enable-linger encore
ls -l /var/lib/systemd/linger/
systemctl restart encore-kiosk.service
sleep 10
systemctl is-active "user@$ENCORE_UID.service"
ls -a "/run/user/$ENCORE_UID/"
sudo -u encore XDG_RUNTIME_DIR="/run/user/$ENCORE_UID" pactl info
```

- **Manager `active` and `pactl info` prints a server:** candidate 2 proven.
  Then undo the probe — `loginctl disable-linger encore && ls
  /var/lib/systemd/linger/` — so that Phase D exercises the installer's own
  path rather than a hand-made one.
- **Manager still inactive:** both candidates are exhausted. **Stop.** The
  diagnosis is incomplete and this is a finding for the architect, not a third
  thing to try.

### A4 — can the identity actually reach the speakers, once a server exists?

With the proven candidate active. This is the question `docs/tests.md` records as
unsettled, and it is worth answering before the profile is touched, so that a
later silence has one cause and not two:

```sh
sudo -u encore XDG_RUNTIME_DIR="/run/user/$ENCORE_UID" pactl list short sinks
sudo -u encore XDG_RUNTIME_DIR="/run/user/$ENCORE_UID" pactl list short sources
sudo -u encore XDG_RUNTIME_DIR="/run/user/$ENCORE_UID" speaker-test -D pulse -c 2 -t sine -l 1
```

- **At least one sink, and a tone out of the speakers:** the output path is whole.
- **No sink:** stop — a running server with no sink is a different fault and a
  finding, not something to configure around.
- **No source listed:** this machine has no capture device. That is the mic-less
  case; note it, and read *What stays unknown* before expecting input to work.
- `speaker-test` comes from `alsa-utils`. If it is absent, install it as a
  debugging tool on that machine only. **It must not be added to the installer's
  package list** — it is not something a terminal needs.

---

## Phase B — get the profile values from the client, then hear it

Two facts about the remote-desktop client are **unknown** and must not be
guessed: the exact token that switches audio on, and whether input needs the
`microphone` key to be non-empty. The template's own header says how such a
change is made: *change a working profile, prove it, regenerate.* Follow it.

### B1 — let the client write the values (not the terminal; no remote host)

On any machine with the Remmina GUI — the author's own desktop is fine:

1. Open the connection editor on a throwaway RDP profile.
2. Set audio output to the local machine, and enable microphone redirection,
   **choosing no device and typing no device name.**
3. Save, and read the file it wrote:

```sh
grep -E '^(sound|microphone|audio-output)=' ~/.local/share/remmina/<that-profile>.remmina
```

Write the three values down verbatim. Those are the values Phase C ships — not
`sys:pulse`, not any hand-written subsystem. **Pinning a subsystem at install
time is forbidden:** a package upgrade or a plugged-in headset changes the right
answer later, and the library resolves it per connection when the subsystem is
left unset.

If the editor offers no way to enable the microphone without naming a device,
**stop and say so.** That would mean "no device picking" and "input works" are in
tension in this client, and it is a product question, not an engineering one.

### B2 — apply them to the live profile on the terminal and look at the log

On the terminal, with the Phase A candidate active:

```sh
P=/var/lib/encore/.local/share/remmina/encore-kiosk.remmina
cp -a "$P" /root/encore-kiosk.remmina.bak
sed -i -e 's/^sound=.*/sound=<VALUE FROM B1>/' \
       -e 's/^microphone=.*/microphone=<VALUE FROM B1>/' "$P"
systemctl restart encore-kiosk.service
sleep 20
journalctl -u encore-kiosk.service --since "3 minutes ago" --no-pager \
  | grep -iE 'rdpsnd|audin|audio|pulse|alsa|oss|backend|sound'
```

Restore afterwards with `cp -a /root/encore-kiosk.remmina.bak "$P"` if anything
goes wrong.

**This is the first time anyone has read the log for the backend.** The template
already ships `freerdp_log_level=INFO`, and the service already sends output to
the journal, so the lines exist and have simply never been looked at.

- **Copy the matching lines out verbatim** and into `docs/tests.md` in Phase C.
  They are what turns "sound does not work" from a silence into a grep.
- Then, with a person at the terminal: play something in the session — is it
  heard from the terminal's speakers? Speak into the microphone — does the
  session hear it?
- **Output works, input silent, and no `audin` line in the log:** input is not
  being requested at all. Go back to B1 — the value is wrong, not the mechanism.
- **Output works, input silent, and there *is* an `audin` line with an error:**
  record the error verbatim. That is the mic path failing for a reason, and it is
  a finding; do not start trying values against it.
- **The session drops or reconnects in a loop after the change:** this is the
  D-014/D-020 hazard named in the backlog — a failing audio channel presenting
  as an unreachable host, retried for ever. Restore the backup and **stop.** It
  is a finding for the architect and the product manager.

---

## Phase C — the implementation (engineer, mechanical)

In this order. Nothing here is behaviour-preserving repair; there is no drift to
repair. Every step is the feature.

### Step 1 — the session type in the unit  [feature; **candidate 1 only**]
- **Test first:** there is no automated test harness for a unit in this
  repository, and inventing one is out of scope. The test is Phase A's written
  outcome, which already exists by the time this step runs. Before committing,
  `systemd-analyze verify /etc/systemd/system/encore-kiosk.service` on the
  terminal after install must report no errors.
- **Then:** add Seam 1 verbatim to `encore-kiosk.service`, in `[Service]`,
  directly below `Environment=HOME=/var/lib/encore`. If A2 was the proven step,
  add the `XDG_SESSION_CLASS=user` line too, with the same comment block.
- **Why here:** the kind of session the terminal runs in is this unit's
  responsibility and nothing else can state it.
- **Behaviour change:** the session's class, and therefore that a sound server
  exists at all. `XDG_SESSION_TYPE=wayland` is also simply true — the compositor
  is a Wayland compositor — and it reaches the kiosk process, where it is
  consistent with the `GDK_BACKEND=wayland` the runner already exports.

### Step 2 — the linger flag in the installer  [feature; **candidate 2 only**]
- **Test first:** as above, the proof is Phase A's written outcome. The check
  that belongs in code is the uninstaller's, in Step 5.
- **Then:** in `encore-install.sh`, section 2 (*the user the terminal runs as*),
  immediately after the `usermod -aG` line:

```sh
# The sound server starts only through a per-user service manager, and this
# account's session class is not granted one. Lingering keeps the manager
# running for this identity regardless of class. It writes
# /var/lib/systemd/linger/encore, which deleting the account does NOT remove —
# encore-uninstall.sh removes it explicitly, and R-11 depends on that.
loginctl enable-linger encore
```

- Re-running setup stays safe: `enable-linger` on an already-lingering account
  is a no-op.
- **Why here:** it is a property of the account, and section 2 is where the
  account is made.
- **Behaviour change:** a service manager for `encore` now runs whenever the
  machine is up.

### Step 3 — the template  [feature; **both candidates**]
- **Test first:** none possible in isolation; the installer's Seam 2 check in
  Step 4 is what proves this landed, and it runs on every install.
- **Then:** in `encore-kiosk.remmina.template`, change **only** these lines, in
  place, without reordering anything:
  - line 22: `sound=` to the B1 value.
  - line 102: `microphone=` to the B1 value.
  - Leave `audio-output=` exactly as it is unless B1 shows the client wrote
    something into it.
  - Leave `freerdp_log_level=INFO` alone. It is how the backend becomes visible;
    lowering it is how this ticket becomes unmaintainable.
- Add to the **existing header comment block only** (lines 1–10), never mid-file
  — the client rewrites the body of this file when the installer sets the
  password, and a comment between keys may not survive:

```
# Audio (BACKLOG.md item 5, D-009, D-014). sound=local means the session's
# audio belongs to THIS terminal. sound=remote is one word away and sends it to
# the other machine, which is the outcome the product forbids — encore-install.sh
# refuses to finish if it ever finds that value. No audio subsystem is named on
# purpose: the client resolves it per connection, so a package upgrade or a
# plugged-in headset does not need a re-install.
```

- **Why here:** audio is a property of the shipped baseline, identical on every
  terminal. It is not per-terminal, so it does not belong in the installer's
  `sed`.

### Step 4 — the installer's post-conditions  [feature; **both candidates**]
- **Test first:** run the installer on the terminal, then hand-corrupt the
  profile — `sed -i 's/^sound=local/sound=remote/' "$PROFILE"` — and re-run the
  installer. It must `die` with the `sound=remote` message and a non-zero exit.
  That failure is the test. Restore by re-running the installer.
- **Then:** add Seam 2 verbatim to the end of section 5 of `encore-install.sh`,
  after the two existing `grep` assertions about the password. Mind `set -eu`:
  use the `if ... then die` form for the negative check, as written in Seam 2,
  never a bare `grep && die`.
- **Why here:** the installer already refuses to finish when what it produced is
  not what it intended (the `CHANGEME` check, the profile count, the key and
  password checks). This is the same responsibility, one more property.
- **Behaviour change:** an install that would have produced a silent terminal now
  fails loudly instead.

### Step 5 — the uninstaller  [feature; **both candidates, contents differ**]
See *Uninstaller changes* below. Written as its own step because R-11 is a
promise and this is the step that keeps it.

### Step 6 — `docs/tests.md`  [documentation]
- Replace the body of *Test 5 — is there sound?* with the procedure in *Tests*
  below, including the verbatim journal lines recorded in Phase B.
- **Write no result.** The summary-table row on line 18 stays as it is. Only the
  person who ran it on a machine may change that row, and they say which machine
  and which date, as every other row in that file does.

### Step 7 — `README.md` item 6  [documentation]
- Item 6 currently reads *"No sound, and the clipboard is open."* Split it: the
  clipboard sentence stays exactly as it is; the audio sentence becomes a
  statement of what is now switched on and what has been seen on a machine, and
  it must agree with `docs/tests.md` at the moment of the commit — which, at
  Step 7, means switched on and confirmed only on the machine Phase B ran on.
  Do not write that audio works on hardware in general.

### Step 8 — a note at install time when no sound server is installed  [feature]
- **Test first:** on a machine where the units are absent, the installer prints
  the note and still exits 0. Contriving that absence on a real terminal is not
  worth it; assert instead by temporarily inverting the condition in a scratch
  copy of the script and seeing the note print.
- **Then:** in `encore-install.sh`, in section 1, after `apt-get install`:

```sh
# Nothing in this list installs a sound server, and a terminal with none is
# silent with no error anywhere. Say so here rather than let it be discovered
# by a child who cannot hear a film. This only reports; it configures nothing,
# and it must not decide which audio subsystem the client uses — that is
# resolved per connection, on purpose.
if [ ! -e /usr/lib/systemd/user/pipewire-pulse.socket ] &&
   [ ! -e /usr/lib/systemd/user/pulseaudio.socket ]; then
    echo
    echo "Note: no PulseAudio-protocol sound server is installed, so this"
    echo "terminal will have no sound. On Debian and Ubuntu:"
    echo
    echo "    apt install pipewire pipewire-pulse wireplumber"
    echo
fi
```

- **Why here:** the installer already tells the operator about a missing SSH
  server in exactly this shape. Same responsibility, same form.
- **Behaviour change:** none to the machine. One more line of output, sometimes.
- **Not decided here, and flagged to the architect:** whether those three
  packages should become dependencies of the installer. They were present on the
  Mac Mini; whether a minimal Ubuntu or a Raspberry Pi OS Lite image has them is
  **unknown**. `apt-cache policy pipewire pipewire-pulse wireplumber` on each
  kind of machine settles it. Adding packages to the install list is a stack
  decision, and this ticket does not take it.

### Step 9 — `XDG_RUNTIME_DIR` in the runner  [feature; **only if A0 says so**]
- **Only if** A0 showed `XDG_RUNTIME_DIR` absent from the kiosk process
  environment. If it was present — which is what the compositor finding
  `wayland-0` implies — **skip this step entirely** and write in the commit
  message that A0 showed it present.
- **Then:** in `encore-kiosk.sh`, beside the two existing exports:

```sh
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
```

- Computed, never hardcoded: the uid is whatever `useradd --system` chose on that
  machine.

---

## Uninstaller changes

**If candidate 1 landed** (the unit's environment): the mechanism leaves nothing
on disk, so there is nothing to remove for it. One addition anyway, in the
*units* section of `encore-uninstall.sh`, beside the two `rm -f` calls:

```sh
rm -rf /etc/systemd/system/encore-kiosk.service.d
```

Reason: a drop-in directory named after our unit is ours, and Phase A creates
one. Add `/etc/systemd/system/encore-kiosk.service.d` to the `STILL PRESENT`
loop as well. Do this whichever candidate lands.

**If candidate 2 landed** (lingering), all of the following, in this order:

1. In the *user and credentials* section, **before** `userdel`, capture the uid
   while the account still resolves:

```sh
ENCORE_UID=$(id -u encore 2>/dev/null || echo "")
```

2. Still before `userdel`, stop lingering and the manager it kept alive:

```sh
# Lingering was switched on at install so a sound server could exist. It writes
# a root-owned flag file that userdel does NOT remove, so it is removed here by
# name as well as by loginctl — R-11 promises this machine comes back clean.
loginctl disable-linger encore 2>/dev/null || true
[ -n "$ENCORE_UID" ] && systemctl stop "user@$ENCORE_UID.service" 2>/dev/null || true
```

3. After `userdel`, and unconditionally, because `disable-linger` can fail and
   the file outlives the account:

```sh
rm -f /var/lib/systemd/linger/encore
```

4. Add `/var/lib/systemd/linger/encore` to the `STILL PRESENT` loop, and when
   `ENCORE_UID` is known, check `/run/user/$ENCORE_UID` is gone too. A removal
   that is not re-checked is how this script starts printing "Nothing of
   Encore's remains" while something remains.

**Verify by hand after uninstalling, not by trusting the script** — this is
Test 4's discipline:

```sh
ls -l /var/lib/systemd/linger/ ; ls -d /etc/systemd/system/encore-kiosk.service.d
loginctl list-users
```

---

## Tests

This project's history is things that report healthy while not working. Three
places make a wrong or absent audio backend **visible** instead of silent, and
all three are required:

**1. Install time — the profile is asserted, not assumed.** Seam 2. A profile
that does not say `sound=local`, or that says `sound=remote`, stops the install
with a message naming the machine the audio would have gone to. Exercised by
Step 4's test, which deliberately corrupts the profile and expects a non-zero
exit.

**2. Connect time — the log names the backend, and someone finally reads it.**
`docs/tests.md` Test 5 becomes:

```sh
ENCORE_UID=$(id -u encore)
loginctl show-session <the encore session id> -p Class -p Type -p Active -p Seat
systemctl is-active "user@$ENCORE_UID.service"
ls -a "/run/user/$ENCORE_UID/"
sudo -u encore XDG_RUNTIME_DIR="/run/user/$ENCORE_UID" pactl info
journalctl -u encore-kiosk.service -b --no-pager | grep -iE 'rdpsnd|audin|pulse|alsa|oss'
```

**Pass** requires all of: `Class=user`; the manager `active`; `pulse/native` and
`pipewire-0` present in the runtime directory; `pactl info` printing a server
name; and the journal showing the output channel with a loaded backend **and**,
on a machine with a microphone, the input channel. The exact lines to expect are
the ones copied verbatim out of Phase B — write them into the test, so a future
run compares strings rather than squinting.

**Fail, and specifically:** the journal showing an output channel with *no*
backend loaded, or a `pulse` backend failing to connect, is the silent case made
loud. `grep` finding nothing at all means the client never asked for audio,
which points at the profile, not at the server.

**3. The human end, which nothing else replaces.** Play something in the session
and hear it from the terminal's speakers. Speak into the terminal's microphone
and have the session hear it. Nobody chose a device at either end. That is the
requirement (R-12, C-5) and no log line is a substitute for it.

**What is deliberately *not* added:** no runtime audio health check in
`encore-kiosk.sh`. A check there could only either kill a session that is
otherwise fine — which would break a mic-less terminal, the one case the product
promises stays usable — or print something nobody reads. The journal line is the
evidence; the test is where the reading happens.

---

## Callers to update

- `sound` and `microphone` in the profile are read by the client, launched by
  `encore-kiosk.sh`. The runner passes no audio arguments and needs no change.
- `encore-install.sh`'s `sed` touches only `server=` and `username=`. It does not
  read or write the audio keys, so Step 3 does not affect it beyond Seam 2.
- `encore-push.sh` already lists every file this ticket touches. **No change.**
- `docs/architecture/constraints.md` C-5 measures the constraint against
  `encore-kiosk.remmina.template:22,102`, which this ticket changes; and
  `docs/architecture/00-index.md` describes Test 5 as never run. Both become
  stale. **The engineer must not edit either** — architecture records are the
  architect's. Flagged in *For the architect*.
- No contract crosses a repository boundary. Nothing outside this repository
  calls anything here.

---

## Out of scope

- **`docs/architecture/*`, `docs/product/*`, and `BACKLOG.md`.** Not the
  engineer's, in either direction.
- **The `audio` group, device ACLs, `DeviceAllow`, `PrivateDevices`, and every
  other privilege.** The permission is already granted; this was measured. No new
  privilege is needed and none may be added.
- **Naming an audio subsystem** anywhere — in the template, the installer, or the
  unit. It resolves per connection, on purpose.
- **Installing sound packages.** Step 8 mentions them; the installer does not
  install them in this ticket.
- **The clipboard.** `disableclipboard=0` is right there in the template, one
  line from what is being changed, and it is a different decision and a different
  ticket.
- **Switching on both candidates at once.** Lingering *and* the declared type is
  two mechanisms for one fault, and the second one hides whether the first
  works.
- **The indefinite-retry behaviour** (D-014/D-020). If audio breaks the
  connection, that interaction is a finding, not something to patch here.

---

## Stop and escalate if

- The Phase A baseline does not match the 2026-09-27 reading — the machine has
  changed under the diagnosis.
- The class lifts but no sound socket appears: a third fault, needing a mechanism
  nobody has costed.
- Neither candidate lifts the class: the cause is not what was read from the
  source.
- The compositor stops taking the console on tty7 under either candidate: the one
  working result outranks this feature.
- The session drops or reconnects in a loop once audio is on — especially on a
  machine with no microphone.
- Phase B cannot enable the microphone without naming a device: "no device
  picking" and "input works" are then in tension, which is a product decision.
- Any step seems to call for a new package, a new group, or a new unit. All three
  are decisions above this ticket.

---

## What stays unknown after this ticket

1. **A terminal with no microphone.** Nobody has tested one. The product promises
   it stays fully usable, and the named risk is that a failing input channel
   drops the connection, which the indefinite retry then presents for ever as an
   unreachable host. **What would settle it:** the Phase D test on a machine with
   no capture device — `pactl list short sources` empty — watching whether the
   session stays up and whether output still works, with
   `journalctl -u encore-kiosk.service -b | grep -i audin` read afterwards. Until
   that is run on such a machine, R-12's second half is switched on and unproven.
2. **Which value the `microphone` key needs.** Settled by Phase B1 for the
   client version on the author's machine only. A different Remmina or FreeRDP
   version may write a different value, and nothing in the product pins those
   versions.
3. **Whether a sound server exists at all on the other target platforms.** The
   installer installs none. `apt-cache policy pipewire pipewire-pulse
   wireplumber` on a Raspberry Pi OS machine and on a minimal Ubuntu settles it.
4. **Old hardware other than the one Mac Mini**, which is the general caveat
   already on the record: the backlog item says old machines vary and each kind
   needs checking.
5. **Whether the class is stamped once and never recalculated.** Phase A proves
   the *fix*, not the *explanation*. If A1 works, the explanation is strongly
   supported but still not directly observed; nobody will have watched the class
   being decided.
6. **Echo, latency and whether a call is actually pleasant.** "A call works" is
   tested as sound in and sound out. Quality on a ten-year-old machine over a
   household network is unmeasured, and no number for it exists anywhere in the
   record.
