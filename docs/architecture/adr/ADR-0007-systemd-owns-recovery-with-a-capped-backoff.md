# ADR-0007 — systemd owns recovery; the runner is a launcher, not a supervisor
- **Date:** 2026-09-14
- **Kind:** reversible (unit-file and script shape; no stored format, no public
  contract beyond the unit names already fixed by D-022)

## Context

Two layers promise recovery today and neither is accountable for it
(`debt.md` item D-A2):

- `encore-kiosk.sh:8-16` wraps the client in `while true; do …; sleep 2; done`.
- `encore-kiosk.service:19-20` sets `Restart=always` / `RestartSec=3`.

Because the script never exits, the unit can never leave `active (running)`.
`docs/troubleshooting.md` already states the consequence as a rule for
debugging: *"`systemctl status` will lie to you."* A terminal that has failed
for days reports itself healthy, which is the operability failure behind R-8
and the reason D-A2 exists.

Three things force a decision now rather than later:

1. **D-020** requires the product to tell two failures apart — a missing or
   invalid configuration *stops*; an unreachable target machine *keeps trying,
   indefinitely and unattended*. A `while true` loop can express neither half:
   it cannot stop and stay stopped, and it discards the exit status that is the
   only thing carrying the distinction.
2. **The author asked for exponential retry** and doubted systemd could do it.
   It can, since systemd v254, with a limit worth knowing about (below).
3. **A flat 2-second retry is not free.** If the target machine is off
   overnight, a 2-second loop is roughly 14,000 restart cycles in eight hours,
   each one a PAM session, a VT acquisition and journal writes, on a machine
   whose storage is often an SD card.

What systemd can and cannot do natively, established by reading systemd 259's
`systemd.service(5)` and `src/core/service.c` on 2026-09-14:

- **It can** back off geometrically: `RestartSec=` is the first delay,
  `RestartMaxDelaySec=` the cap, and `RestartSteps=` the number of steps
  between them, the ratio being `(max/sec)^(1/steps)`. Both were added in
  **systemd 254**, which becomes a version floor to declare under D-024.
- **It can** stop restarting on a named exit status
  (`RestartPreventExitStatus=`), and it applies that exception even when
  `Restart=always`.
- **It can** rate-limit starts (`StartLimitIntervalSec=` /
  `StartLimitBurst=`) and mark the unit failed when the limit trips.
- **It cannot** randomise or jitter the delay. Irrelevant at a fleet of two or
  three (D-016).
- **It cannot** use a different backoff curve per failure kind. One curve for
  everything.
- **It cannot reset the backoff on its own.** `s->n_restarts` is flushed only
  when a start is *not* an auto-restart — a manual `systemctl start`/`restart`,
  a `reset-failed`, a reboot, or an explicit `RESTART_RESET=1` from an
  `sd_notify` service (systemd 257+, and `cage` is not a notify service).
  Time spent running successfully does **not** reset it. A terminal that has
  reconnected twenty times over three months is therefore at the cap, and the
  twenty-first reconnect waits the full cap even though nothing was wrong.
  This is the single most important limit here, and it is why the cap must be
  small rather than generous.

## Options

**Option A — leave the loop, drop `Restart=`.** Zero moving parts added.
Forever cost: the unit can never fail, so D-020's "stops" half is
unimplementable, no `systemctl` command ever tells the truth about a terminal,
backoff would have to be re-implemented as shell arithmetic, and the exit
status of the client — the only channel that can carry *why* it stopped — is
thrown away on every iteration. Rejected.

**Option B — systemd owns recovery; the runner becomes a launcher.** Delete the
loop; the script validates the configuration, then `exec`s the client so the
client's status becomes the script's status. `cage` propagates its child's exit
status as its own (`cage.c:199-213` and `cage.c:722-726`: the `SIGCHLD` handler
sets `return_app_code`, and `main` returns the child's code when cage itself
did not error), so the client's status reaches systemd through the compositor
unchanged. Forever cost: **every reconnect restarts the compositor**, not just
the client — a black screen for the length of the backoff delay, plus a PAM
session and a VT cycle each time. Recommended, and chosen.

**Option C — a supervisor process inside `cage`.** Keeps the compositor alive
across reconnects, so recovery is invisible to the person at the terminal.
Forever cost: it is Option A with better manners — a second policy owner that
must re-implement backoff, rate limiting and logging, and must be kept
agreeing with the unit's policy for ever. It also has to be written, tested and
maintained by one author, where systemd's version is already there. Rejected
now; named as the fallback if Option B's compositor restart proves visibly bad
on real hardware.

## Decision

**systemd owns recovery. The runner launches and exits; it never retries.**
The deciding reason: D-020 requires two different outcomes from two different
failures, and an exit status is the only channel that can carry that
distinction to a supervisor — a loop that never exits has no channel at all.

Concretely, in `encore-kiosk.service`:

```ini
[Unit]
StartLimitIntervalSec=0          # note: [Unit], not [Service]

[Service]
Restart=always
RestartPreventExitStatus=CONFIG  # 78; systemd names it, so status output reads plainly
RestartSec=2
RestartSteps=4
RestartMaxDelaySec=30
```

which gives delays of roughly 2s, 4s, 8s, 17s, then 30s repeating.

And in `encore-kiosk.sh`: find the profile, and

- if there is no usable profile, write one line naming the fault to stderr (the
  journal) and `exit 78`;
- otherwise `exec remmina --enable-fullscreen --disable-toolbar
  --enable-extra-hardening -c "$PROFILE"`.

Three deliberate sub-choices inside that:

- **`Restart=always`, not `on-failure`.** D-005 says there is no state in which
  the terminal is an ordinary computer, so a *clean* client exit must also
  return to the remote login screen. `RestartPreventExitStatus=` is honoured
  regardless of `Restart=`, so the one stop-and-stay-stopped case still works.
- **`StartLimitIntervalSec=0`, disabling the rate limit.** D-020 says an
  unreachable machine keeps trying *indefinitely*. Any burst limit is a promise
  to eventually give up, which contradicts it. This reverses the recommendation
  written in `debt.md` item D-A2 on 2026-09-13, which predates D-020.
  The cost is real and is accepted below.
- **`SuccessExitStatus=` is not used.** It only reclassifies an exit as
  success; under `Restart=always` it would not prevent a restart. It is the
  wrong directive for this job.

**`encore-kiosk.target` keeps `Wants=`, not `Requires=`** — this closes the
question `debt.md` item D-A3 and ADR-0003 both left open. The reason: under
this decision the *service* is the accountable object and its own state now
tells the truth, so `Requires=` adds no signal. What it would add is a target
that tears itself down on the one failure — a broken configuration — where the
most useful thing is a machine sitting still in a state an administrator can
inspect over SSH.

## Consequences

**Easier.** `systemctl status encore-kiosk.service` becomes honest: `failed`
with `status=78/CONFIG` means the configuration is broken, and repeated
restarts are visible and counted in the journal. Backoff, rate limiting and
logging are configuration rather than code. The configuration is re-read on
every restart, so repairing a profile and restarting the unit is the whole
repair procedure.

**Harder, and these are real costs, not footnotes.**

1. **Recovery is now visible to the person at the terminal.** The compositor
   dies and is rebuilt on every reconnect, so a drop shows a black screen for
   the backoff delay. `docs/product/users.md` names a black screen as a reason
   the person gives up, and C-6 records that nobody has ever stated how quickly
   a terminal must come back. The cap of 30s is a guess made to be small
   rather than a measured number.
2. **`ExecStopPost=+/usr/bin/chvt 1` (`encore-kiosk.service:18`) becomes wrong
   under this decision.** It is harmless today only because the loop never
   exits. Once the unit restarts on every drop, every reconnect flips the
   foreground console to tty1 and shows the person at the terminal a text login
   prompt — a C-2 breach arriving through the recovery path. That line belongs
   on the deactivation path, not on the restart path, and must move or go
   before the loop is removed. Not a separate decision; a required part of
   this one.
3. **The backoff converges upward and never comes back down.** See the
   `n_restarts` finding above. A long-lived terminal ends up waiting the full
   cap on every reconnect. `systemctl restart` or a reboot clears it. This is
   why the cap is 30s and not five minutes.
4. **Nothing gives up, so nothing ever reaches `failed` for an unreachable
   machine.** That is D-020 working as decided, and it means the "a terminal
   has been broken for days" signal cannot come from the unit state for that
   failure. It has to come from the journal, or from whatever `BACKLOG.md`
   item 13 specifies. This decision deliberately does not build a notifier.
5. **The two failures are told apart by *our* check, not by the client.** The
   client's exit status is not trusted to mean anything; only exit 78, written
   by our own script before the client starts, carries meaning. "Unreachable"
   is simply the default branch. What counts as an invalid configuration is
   not settled here — it belongs to the configuration design (`debt.md` item
   D-A7). Until that lands, "no profile found" is the only thing that yields
   78.
6. **D-020's "says so on the screen" is not delivered by any of this.** An
   exit status produces the *stop*, never the message. The message is item D-A1
   and collides with ADR-0002 head on; nothing here changes that.
7. **A version floor.** `RestartSteps=` and `RestartMaxDelaySec=` need systemd
   ≥ 254. Current apt-family releases satisfy this; under D-024 that is a
   declared prerequisite rather than a compatibility problem, and a machine on
   systemd 252 silently gets flat `RestartSec=2` retries, because systemd
   ignores directives it does not know.

**What is contingent on a test nobody has run.** Everything about *backoff*
assumes the client exits when a connection drops. Upstream says it does not by
default ([Remmina issue 3113](https://gitlab.com/Remmina/Remmina/-/issues/3113)),
and Test 2 in `docs/tests.md` has never been run. If the client stays on screen
showing its own dialog, no restart policy at any layer ever fires and the
backoff numbers above are tuning for an event that never happens. The parts of
this decision that hold either way are the single owner, the exit-78
configuration path, the absence of a rate limit, and the `chvt` consequence —
all of which concern the configuration failure and the truthfulness of the
unit state, neither of which depends on drop behaviour.

## Revisit when

- **Test 2 shows the client does not exit on a dropped connection.** Then the
  next question is how to make it exit — a client flag or profile setting, or
  something that watches the connection — and a restart policy is downstream of
  that answer, not a substitute for it.
- **The compositor restart proves visibly bad on real hardware** (item 14): a
  black screen of seconds on every reconnect may be worse for the person at the
  terminal than the duplication this decision removed. Option C is the fallback,
  and it must then keep the exit-78 path intact.
- **Someone states how fast a terminal must return to a login screen.** C-6
  records that no such number exists. When it does, `RestartMaxDelaySec=` is
  measured against it rather than guessed.

---

## Addendum, 2026-09-23 — the missing premise arrived, and consequence 4 was
## observed

All `file:line` citations in this ADR were re-checked against the files on
2026-09-23 and every one is still correct.

**The premise under the cap is no longer unwritten.** This decision was taken
on 2026-09-14 while the architect's question Q-6 was open: the author had
cited a decision about audio as the basis for retrying for ever, and no
decision anywhere said the target machine is always on. **D-026, 2026-09-21,
answers it** — the machine being connected to is available about 99% of the
time, not always, so a terminal that cannot reach it is experiencing an
expected condition and must wait through it quietly, raising no alarm. That
supports every part of this decision and closes Q-6. It does not supply Q-7's
number — how long a *person* may be shown nothing — which is still open in
`NOTES.md`, so the 30-second cap remains a defensible guess.

**Consequence 4 has been watched happening.** It predicted that nothing would
ever reach `failed` for an unreachable machine, so "a terminal has been broken
for days" cannot come from the unit state. On 2026-09-23 a failed connection
produced a clickable dialog on the terminal's screen while the journal recorded
only "started" and "session opened" — so on that occasion it did not come from
the *journal* either, which this decision had named as the fallback channel.
The cause of that particular silence was never identified; a clean reinstall
afterwards connected successfully. It is recorded as unexplained rather than
attributed. What it establishes is narrower than a fault and worth stating:
the journal is not, on the evidence, a channel that can be relied on to carry
this signal, and this decision leans on it.

**D-026 also sharpens consequence 4 in the other direction.** Under it, "cannot
connect" may never be treated as evidence of a fault at all. So the distinction
this decision can express mechanically — exit 78 for a broken configuration,
retry for everything else — is not merely all that is built; it is all that is
*permitted*. A genuinely broken terminal is indistinguishable from an ordinary
outage for as long as an outage could plausibly last, by design.
