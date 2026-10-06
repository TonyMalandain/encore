# Constraints — the numbers and the hard edges

Most of this project's constraints are not performance numbers. They are
**absolutes**: things that must be true one hundred percent of the time,
because the user is a child and the failure mode is an unmanaged computer in a
bedroom. Absolutes are harder than percentages, and they are what the design
must be judged against.

**One section here is not a constraint.** `H-1` names a recurring *hazard* —
a mechanism that reports success without doing its job — and is kept in this
file because every instance of it is about what the system can and cannot
detect. It sets no number and orders no work.

**Names and citations corrected 2026-09-23.** This file was half-converted to
the names D-022 and D-023 fixed: C-4 was still on the old ones while C-6 was on
the new. Every `file:line` here has now been re-checked against the file, not
merely renamed.

---

## C-1 — Environment (from D-003, R-1, R-2)

| Constraint | Value |
|---|---|
| Package manager | **apt family or dnf family** (D-036, 2026-10-04) — nothing else |
| Display server | Wayland only |
| Mandatory access control | **no policy of our own, on either family.** SELinux enforcing is in scope and costs nothing — measured against the policy 2026-10-04 and **since watched on a screen, 2026-10-05**: enforcing and permissive gave the same session on one Fedora 44 machine, once (`docs/tests.md` test 14c). See the paragraph below for what that does and does not cover |
| Init | systemd only, **and ≥ 254** — `RestartSteps=` / `RestartMaxDelaySec=` arrived there and ADR-0007 depends on them. Older systemd ignores them silently and gives flat retries. |
| Python | CPython 3, standard library only, **and ≥ 3.10** — see the paragraph below. Below it `encore-probe.py` does not import at all. **Corrected 2026-09-23 down from 3.14**, which was derived from a defect since fixed. |
| Hardware | none assumed — 32-bit and ARM must be considered in scope. **No machine is refused for its processor any more, as of 2026-10-04**, but one can still be refused for its library layout: `encore-install.sh:46` used to `die "unsupported architecture"` on anything but `x86_64`, `aarch64` and `armv7l` — an artefact of constructing a Debian multiarch path, never a product limit, ruled out by the product manager as a deliberate behaviour change. **The refusal moved rather than ended:** a machine whose plugin path the unit does not name is still turned away, by the coverage check at `:282-285`, later and with a message naming the line to add. R-2's cost is reduced, not eliminated. **This row first claimed the refusal was gone; that was corrected the same day — see `debt.md` D-A20, which carries the trail** |
| Host distribution | out of scope (D-002) — **and this row no longer means what it said.** It was written when the author's host was a distribution we did not support; since D-036 the author's host is Fedora, which *is* a supported terminal family. The machine is still out of scope, but now because of what it *is* — the RDP target — and not because of what it runs. Nothing may be installed on it to test the dnf side |

**SELinux enforcing is permitted, and it needs nothing from us. Measured
2026-10-04 on Fedora 44, `selinux-policy-targeted-44.10-1.fc44`, SELinux
`Enforcing`.** D-036 named SELinux as the specific untested risk of accepting
dnf, and the answer is that the product's arrangement is already allowed by the
stock targeted policy. Five things were measured, not reasoned:

- **The identity's home carries `var_lib_t`, and that does not block it.**
  `matchpathcon` returns `system_u:object_r:var_lib_t:s0` for `/var/lib/encore`
  and for every directory `encore-install.sh:112-116` creates beneath it — not
  `user_home_dir_t`. The live kernel was then asked directly, with
  `selinux_check_access`, whether the session's domain may use that label:
  `dir` `search`/`write`/`add_name`, `file` `create`/`read` and `sock_file`
  `create` are all **allowed** from both domains the session can land in. The
  policy says why — both carry the `files_unconfined_type` attribute, and
  `allow files_unconfined_type file_type:…` covers every class; `unconfined_t`
  additionally gets `allow userdomain var_lib_t:dir { add_name … write }`. So
  the label is **untidy, not fatal**: a home that is not a home type reads
  oddly and changes nothing.
- **The login mapping sends `encore` to an unconfined user.**
  `/etc/selinux/targeted/seusers` contains exactly two lines, and one is
  `__default__:unconfined_u:s0-s0:c0.c1023`. SELinux keys on nothing else:
  **neither `--system` nor `/usr/sbin/nologin` is visible to any rule**, as no
  rule in the policy conditions on a uid range or a login shell.
- **`PAMName=login` succeeds from systemd, which is the one thing that could
  have refused to start the unit.** Fedora's `/etc/pam.d/login` carries
  `session required pam_selinux.so open`, and `required` means a failed context
  computation stops the session dead. That computation was run directly against
  `libselinux-3.11`: `get_default_context("unconfined_u",
  "system_u:system_r:init_t:s0")` returns **0** and
  `unconfined_u:unconfined_r:unconfined_t:s0`. It does not fail.
- **The transition is explicitly contemplated by the policy, including under
  `NoNewPrivileges=true`.** `allow init_t init_t:process setexec` lets systemd
  set the exec context at all; `allow init_t login_userdomain:process
  transition` permits the domain change, and `unconfined_t` carries
  `login_userdomain`. The third rule is the one worth knowing about:
  `allow init_t login_userdomain:process2 nnp_transition`. An SELinux domain
  transition under `NoNewPrivileges=` requires that permission, and
  `encore-kiosk.service:48` sets `NoNewPrivileges=true` — so this pair would
  have been a hard, silent stop had the policy not named it.
- **If PAM does not relabel, the fallback is also unconfined.**
  `selinuxexeccon /usr/bin/chvt system_u:system_r:init_t:s0` returns
  `system_u:system_r:unconfined_service_t:s0` — a `bin_t` binary started by
  systemd lands in `unconfined_service_t`, which carries the same
  `files_unconfined_type`, `devices_unconfined_type` and
  `xserver_unconfined_type` attributes. `tty_device_t`, `dri_device_t` and
  `event_device_t` are all readable, writable, openable and ioctl-able from
  **both** candidate domains (asked of the live kernel). Which of the two the
  session actually ends up in was **not** established and does not matter:
  every file-label question has the same answer either way.
- **`pam_namespace.so`, also in Fedora's `login` stack, is a no-op**:
  `/etc/security/namespace.conf` has no active line on a stock Fedora 44.

**And nothing needs relabelling either, which is the stronger result.** Every
directory `encore-install.sh` writes into already carries the type
`matchpathcon` wants for the files placed in it, so the default
parent-inheriting label is the correct one and **no `restorecon` and no
`semanage fcontext` call belongs in the installer**:

| Written | Parent's type | What `matchpathcon` wants |
|---|---|---|
| `/etc/systemd/system/encore-kiosk.{service,target}` | `systemd_unit_file_t` | `systemd_unit_file_t` |
| `/usr/local/bin/encore-kiosk.sh` | `bin_t` | `bin_t` |
| the install record under `/etc` | `etc_t` | `etc_t` |
| everything under `/var/lib/encore` | `var_lib_t` | `var_lib_t` |

The first row is the one that would have been fatal — systemd refuses to load a
unit file of the wrong type — and it is correct for free.

**The hazard here is doing something, not doing nothing.** The obvious reflex,
`semanage fcontext -a -t user_home_dir_t "/var/lib/encore(/.*)?"`, is the one
change that could break a working terminal: `user_home_dir_t` is reachable from
a `home_root_t` parent, and `/var/lib` is `var_lib_t`, so the result is a home
type hanging off a non-home root — and a `--system` identity has no business in
a user home type in the first place. **There is nothing to add to the installer
on either family.** D-036's "one implementation" claim survives intact: no
policy module, no Fedora-only component, and so no ADR — there is no decision
left to take.

**That was all policy and labelling, and none of it was a terminal. It has now
been watched on a screen — 2026-10-05, Fedora 44, `docs/tests.md` test 14c.**

This paragraph used to end with the prerequisite rather than the answer, and the
prerequisite was the right one, so it is worth keeping what it said and why.
Everything measured above is policy and labelling; a session can still be refused
by a rule that has nothing to do with file labels, and such a refusal can be
invisible, because `dontaudit` rules suppress denials without logging them and
this policy carries **102** of them reaching `unconfined_service_t`, **164**
reaching `unconfined_t` and **121** reaching `init_t`. **A clean AVC log is
therefore not evidence of anything**, which is why the only check named here was
to look at the screen: isolate the target with `setenforce 0`, isolate it again
with `setenforce 1`, and compare. That was run, and **the two screens were the
same.** No rule had to be named, so there is no policy module, no Fedora-only
component, and still no decision left to take.

**What that observation covers, exactly, and it is less than "SELinux is out of
the picture for good".** It is two isolates on **one** machine, **once**. It does
not reproduce boot conditions — a Fedora reboot came back into a working session
by itself the same day (test 7), but nothing recorded which SELinux mode that
boot came up in, so the enforcing comparison is the pair of isolates and nothing
else. And a screen that matches tells us the *same* thing happened twice; it does
not tell us a `dontaudit` rule is not quietly suppressing the same denial in both
runs. The claim this row can now make is that **SELinux enforcing has been seen
not to change the outcome**, which is what C-1 needed, and not that it has been
proven irrelevant.

**Consequence nobody has priced yet:** "no hardware assumed" plus "Wayland
only" is a real tension on old machines. A 2009 iMac or an old PC with an
ancient GPU may have no working Wayland path at all. `BACKLOG.md` already asks
whether those two machines qualify. Until someone runs it, R-2 is a claim.

**The architecture that would have enforced the version floor does not exist,
2026-09-23.** Under D-027 there is no package, so no dependency resolver ever
sees `systemd (>= 254)`. `encore-install.sh` is the only thing that could check
it and it does not (`encore-install.sh:79-83` installs packages and checks no
version of anything). A machine on systemd 252 gets a terminal that works and
retries flat rather than backing off, with nothing anywhere saying why. D-027
records this cost in the product's own words; it is repeated here because it is
the mechanism half.

**The Python floor is 3.10, and it is syntactic. Corrected 2026-09-23, the
same day it was first recorded.**

*What this paragraph said, and why it was right when it was written.* It said
the floor was **3.14**, and that it was behavioural rather than syntactic:
`getaddrinfo` IDNA-encodes a name before it looks anything up, and
`encore-probe.py` turned the resulting error into `2 USAGE` — the stop-for-ever
side of ADR-0008's table — by reading the exception's `.reason`. That was
measured, not guessed: on `a..b:3389`, 3.10.21 and 3.11.16 raised a bare
`UnicodeError` with no `.reason`, while 3.14.7 raised `UnicodeEncodeError` with
`reason='label empty'`. On the older shape the handler raised `AttributeError`
inside an `except`, left `main` as a traceback, and exited **1** — the status
the probe holds unassigned so a crash can never be read as a classification.
The malformed `RDP_HOST=` that ADR-0008 stops on would have been retried for
ever instead. The floor was real and the consequence was real.

*What changed.* The defect was fixed concurrently by the engineer. The handler
now interpolates the exception itself — `{failure}`, not `{failure.reason}`
(`encore-probe.py:389-408`, and the comment there records why) — which works on
every version because every `UnicodeError` has a string form. **The behaviour
the 3.14 figure was derived from no longer exists, so the figure no longer has
a justification.** Verified 2026-09-23 on all three interpreters to hand:
`encore-probe.py "ex..ample.com"` exits 2 with one readable line and no
traceback on 3.10.21, 3.11.16 and 3.14.7, and the test suite passes 61 tests on
each. `docs/tests.md`, Test 11, is the authority on which interpreters the
suite has been run under.

*The floor that remains.* Two things in the probe set it, and both give the
same number:

- **3.10, from syntax, and this is the binding one.** `bytes | None`
  (`encore-probe.py:255`) is a PEP 604 union evaluated at runtime, in a
  function signature, with no `from __future__ import annotations` anywhere in
  either file. Below 3.10 the module does not import, so nothing else about it
  matters. (`list[str]` at `:437` is only 3.9.)
- **3.10, from the standard library, independently.** The probe distinguishes
  `5 TIMEOUT` from `4 UNREACHABLE` by catching `TimeoutError` before `OSError`
  (`:345`, `:366`). `socket.timeout` became an alias of `TimeoutError` in 3.10;
  below that it is an `OSError` that is *not* a `TimeoutError`, so every socket
  timeout would fall through to the `OSError` clause and be reported as
  UNREACHABLE. Confirmed on 3.10.21: `socket.timeout is TimeoutError`.

Neither was tested on an interpreter below 3.10 — none was to hand — so
"3.9 fails" is `assumed`, from PEP 604 and from the 3.10 changelog for
`socket.timeout`, not measured. Everything at and above 3.10 is measured.

*How this was established:* from the code, by reading `encore-probe.py` and
`encore-probe-test.py` for what they actually require, and by running the suite
and the malformed-address case on `/usr/bin/python3.{10,11,14}`. Not from the
earlier reasoning, which is what had gone wrong.

**This is worth keeping as an example.** A constraint was recorded from a
defect. The measurement was sound, the reasoning was sound, and the number was
still wrong the moment the defect was fixed — because it described what the
code happened to do, not what the design needs. A floor derived from a bug
dissolves when the bug does.

Nothing checks the remaining floor, in the same way and for the same reason
nothing checks the systemd one — see D-A18 and D-A14 in `debt.md`. Whether
`encore-install.sh` should check either is a backlog question, not settled
here. Note that 3.10 is a far weaker case for a check than 3.14 was: it is
four years old, every release in scope ships something newer on either family
— Fedora 44 ships 3.14 — and
the failure mode is now a loud `SyntaxError` at import rather than a silent
misclassification.

**Only one hardware combination has ever been *recorded***, on 2026-09-23:
x86_64 on a clean Ubuntu 26.04 VM, with Remmina 1.4.43, cage 0.2.1 and FreeRDP
3.31. The 32-bit and ARM halves of the row above are in scope on paper and
untested in fact.

**A second machine was watched working on 2026-10-05 — Fedora 44 — and nobody
wrote down what it was.** Processor, and whether it was physical or virtual, were
not reported, so this paragraph cannot say whether that was a second hardware
combination or the same one again. It is recorded as a gap rather than guessed at,
because the guess would be the whole value of the sentence. **This is a question
for the author, not a measurement anybody can repeat later**: the machine is
known to them and unknowable from here. `encore-install.sh:37-43` does name all three architecture triplets,
so the intent is built in even though it is unproven.

---

## C-2 — The kiosk absolute (D-004, D-005, R-6, R-8)

**There must be no reachable state in which the person at the terminal sees
anything other than the remote machine's login screen or session.** Not a
desktop, not a settings panel, not an error dialog, not a terminal prompt, not
the remote client's own user interface.

This is one hundred percent, not "almost always". The current design has at
least two ways to fall short of it — see `debt.md`, items D-A1 and D-A4.

**It has now been watched falling short of it, three times.** On 2026-09-14 a
terminal with no profile showed the client's own connection editor and file
chooser, and the client's main window sat above the session with no way to
raise or dismiss it safely. On 2026-09-23 a failed connection put a clickable
certificate dialog on the terminal's screen. C-2 is an absolute the product
does not currently hold, and that is observed rather than argued.

---

## C-3 — Reversibility absolute (D-007, R-11)

**Deactivation must require no repair by hand.** Anything that rewrites a
system file in place, rather than adding a file beside it, breaks this. The
current design is well-behaved here: it adds units, adds a user, adds a script,
and flips one symlink.

**Under D-027 this is now a promise kept by our own code, 2026-09-23.** With no
package there is no package manager holding the file list, so
`encore-uninstall.sh` is the only thing that knows what to take off. It removes
the units, the script, the user and the home directory, restores the default
target from the record written at install time (`encore-uninstall.sh:81-97`,
I-7 in `interfaces.md`), and then *re-checks* that each of those is gone and
says so (`:127-137`). Packages installed at setup are deliberately left behind
and said out loud (`:122-125`), which is the right call — removing them is the
one step that could break something unrelated.

**Still a claim, not an observation.** Test 4 in `docs/tests.md` has never been
run. C-3 is the absolute with the largest gap between how carefully it is
implemented and how little it has been checked.

---

## C-4 — Privilege ceiling (D-012, R-15, R-16)

The running capability may reach:

- the screen, the keyboard, the mouse, the audio devices
- the one host named in its profile

and nothing else. In particular: no root, no other hosts on the LAN, no other
users' data, no package management, no storage beyond its own home.

**Measured against the code, re-measured 2026-09-23 — and the previous
measurement was wrong.**

What is present (`encore-kiosk.service:7-8`, `:34`, `:36`): `User=encore`,
`Group=encore`, `ProtectSystem=yes`, `NoNewPrivileges=true`. Plus
`InaccessiblePaths=` on Remmina's keyring plugin (`:13-15`), which is a
confinement of a different kind — it exists so the client cannot demand a
keyring no unattended terminal can unlock.

**`ProtectHome=true` is NOT present.** This section previously said it was,
citing the old file name and the old line numbers. It is commented out at
`encore-kiosk.service:35`. `docs/troubleshooting.md` gives the reason: it hides
`/run/user` along with `/home` and `/root`, and `/run/user` is where the
Wayland socket lives, so the capability cannot start with it on. It was turned
off to reach a working session on 2026-09-14 — a blocker being cleared, not a
decision that the extra reach is acceptable.

**So the confinement this constraint describes is currently absent**, and the
capability can read other users' home directories. The record said otherwise
for nine days. See `debt.md` item D-A4, which is now the inverse of what it was
written as.

**The network half is entirely unbuilt** — there is no `IPAddressDeny=`, so
the process can reach every host the machine can reach. `ProtectSystem=yes` is
also the weakest of the three levels; it leaves `/etc` writable.

**And the reach is wider than this constraint says in one more way:** the
identity is added to the `video`, `input` and `render` groups
(`encore-install.sh:94`). That is how the compositor gets the GPU and the input
devices, so it is doing real work, but "the screen, the keyboard, the mouse"
above is a description of intent and `video,input,render` is the mechanism
nobody wrote down until now.

---

## C-5 — Audio absolute (D-009, D-014, R-12)

Sound out through the terminal's speakers and, where a microphone exists, in
through the terminal's microphone — **as the default, with nobody choosing a
device from a list**, and a terminal with no microphone must still work fully.

**Measured against the code:** the shipped template sets `sound=off` and leaves
`microphone=` empty (`encore-kiosk.remmina.template:22,102`). Audio is not
merely unbuilt; the current configuration switches it off.

**Citation corrected 2026-09-23. The conclusion is unchanged; the evidence was
never ours.** This used to be measured against
`group_rdp_server_server.remmina` at the repository root, which is an untracked
personal connection profile and will never exist on an adopter's machine.
Measuring a shipped constraint against a file we do not ship is how a record
describes a product that does not exist. The template is the shipped artifact
and it says the same thing.

**And the template says it for a reason that is now explicit.** It is generated
verbatim from the profile observed working on 2026-09-14, with only host,
account, password and label blanked (`encore-kiosk.remmina.template:1-10`). So
`sound=off` is not a decision anybody took — it is a property of the machine
the working profile was built on, carried along. The product record says the
same in its own words on 2026-09-23: policy and baseline had been bundled, and
separating them makes D-009, D-014 and D-019 visibly undelivered rather than
invisibly claimed.

---

## C-7 — Fleet size: two or three terminals, one household

**The number this design is built for is 2–3.** Not a dozen, not a site.

This is the smallest-looking constraint in the file and one of the most
load-bearing. It is the whole reason for ADR-0005 (assemble from parts rather
than adopt a thin-client platform), and it is why the absence of central
configuration management is a reasonable position rather than a glaring hole.

**What it licenses:** configuring each terminal individually; no fleet view; no
push of changes; no inventory; no rollout mechanism.

**When it stops holding:** watch for the symptom, not the count — the first
time a change has to be applied to every terminal by hand and one of them gets
missed. Around a dozen machines, or terminals in more than one household, the
platforms that were rejected start being cheaper than the assembly.

**Source:** the author, 2026-09-13.

---

## C-6 — No clock, but one real timing number

`RestartSec=3` and `sleep 2` are the only numbers in the system
(`encore-kiosk.service:20`, `encore-kiosk.sh:15` — both re-verified
2026-09-23). Neither has a stated
reason and neither has been tuned against anything. There is **no stated
requirement for how quickly a terminal must return to a login screen** after a
drop. If one matters, it belongs in the product record, not here.

**2026-09-14: the absence of that number now costs something.** ADR-0007 has to
choose a backoff cap, and under it that delay is a black screen in front of the
person at the terminal rather than an invisible pause, because the compositor
restarts with the client. Thirty seconds was chosen — small on purpose, because
systemd's backoff never decays on its own, so the cap becomes the steady-state
wait on a long-lived terminal. It is a defensible guess, not a measurement, and
it is put to the author as Q-7 in `NOTES.md`.

**A third number now exists, and it is not ours: 90 seconds.** That is how long
stopping the unit took on 2026-09-14 while the compositor held a console it had
not been granted. `TimeoutStopSec=10s` and `KillMode=mixed`
(`encore-kiosk.service:21-22`) are the answer to it, and that pair is the one
timing number in the system that was chosen against an observation rather than
guessed.

**And the premise under ADR-0007's cap is no longer missing.** D-026
(2026-09-21) states the machine being connected to is available about 99% of
the time, not always, so an outage is an ordinary event a terminal waits
through quietly. That closes the architect's Q-6, which had found the premise
leaned on everywhere and stated nowhere. It does not supply the number Q-7
asks for — how long a *person* may be shown nothing — which is still open.

---

## H-1 — A clean result that proves nothing

**Named 2026-10-05.** This is not a constraint and it is not debt. It is a
*failure mode* that has now been met six times, recorded across three documents
under six different names, and never written down as one thing — so each time
it is found, it is found again from scratch. It lives here because every
instance is about what this system can and cannot *detect*, which is the
subject of this file.

**The shape.** A mechanism reports success without having done its job,
because the thing it depends on is **satisfiable without being satisfied**. No
error, no log line, no failed exit status. The result is clean and it is empty.

**The one question that finds it, and it must be asked out loud:** *if the
thing this checks were absent, broken, or doing nothing, would this report
anything different?* If the answer is no, the check reports nothing and the
pass is decoration. The question has to be asked when the check is **written**,
because a check of this kind has, by construction, never been seen to fail —
and so nothing will ever prompt the question later.

The six, oldest first, each already recorded where it bites:

1. **`systemctl status` reports `active (running)` for ever.** The runner
   loops, so the unit's state is the same whether a session exists or not, and
   the restart policy can never fire. `debt.md` D-A2.
2. **`Wants=` means the target succeeds even when the terminal does not.**
   `debt.md` D-A3 — the name of that item is this hazard stated exactly.
3. **The installer's coverage loop reports success over an empty list.** `for p
   in $SECRET_PLUGINS` does nothing, and dies about nothing, when the `find`
   returned nothing — which is precisely what happened when that `find` ran
   before the packages step and so searched a machine with no plugin on it yet.
   `debt.md` D-A19.
4. **A `systemd-analyze verify` check passed against a unit file that does not
   exist.** The old wording looked for the *absence* of two strings, and
   `./nope.service` has no strings at all. `docs/tests.md` test 14a check 2,
   rewritten to require positive output.
5. **`noopenh264` provides the decoder's soname and decodes nothing.** rpm's
   requirement is satisfied, the install is clean, and H.264 silently does not
   work. `stack.md`, and the withdrawal of D-037.
6. **Test 14b's install half passed while the one line nothing has exercised
   was added afterwards.** An installer that completes is not a terminal that
   runs, and a run that predates a line is no evidence about that line.
   `stack.md`, 2026-10-05. **Closed the same day, by observation**: a later
   install on Fedora 44 ran with the `openh264` line in place and `rpm -q
   openh264 noopenh264` then showed the real package installed and the stub
   absent. Kept here rather than deleted — the instance was found by asking H-1's
   question of a passing test, and a closed instance with its resolution is worth
   more to the seventh reader than a gap would be.

**Instances 5 and 6 are the same defect one level apart**, which is the clearest
statement of why this needs a name: a stub that satisfies a dependency while
decoding nothing, and a test run that satisfies a check while exercising
nothing, are one hazard at two altitudes. Finding it in the packaging taught
nobody to look for it in the test record, because nothing connected them.

**What this does not say.** It sets no number, forbids nothing, and orders no
work — the six instances are already recorded, and **as of 2026-10-05 four of
them are shut and two are open.** Three are guarded or repaired (3, 4 and 5,
and 5's guard has since been watched working), one is closed by observation (6),
and **1 and 2 are still open** — `systemctl status` still reports
`active (running)` for a terminal that has failed, and `Wants=` still lets the
target succeed when the terminal does not. Those two are the oldest and the
costliest, and nothing about the Fedora observations touched either.
It exists so that the seventh is recognised on sight. `CONTRIBUTING.md`'s
evidence rules name the neighbouring mistake, reasoning from configuration to
runtime, which is about how a person reads a machine; this one is about how a
mechanism reports on itself, and the two are worth keeping apart.

---

## The conflict this record must not hide

**R-6 (nothing but the remote session) and R-10 (the administrator can reach
the machine without the screen) are served by the same mechanism, in opposite
directions.**

The design leaves consoles 1–6 as text logins so the administrator can get in.
The person at the terminal can press `Ctrl+Alt+F1` through `Ctrl+Alt+F6` and
land on one of them — **which of those keys gives a login prompt varies by
machine**, and the kiosk holds tty7. A child without credentials cannot log in,
so nothing is *granted* — but the screen has stopped being the remote session,
which is what C-2 says must never happen, and a blank console with a cursor is
exactly the kind of thing a child calls an adult about.

**Corrected 2026-09-23, from the author.** This paragraph said `Ctrl+Alt+F2`,
`interfaces.md` said `Ctrl+Alt+F1`, and `NOTES.md` Q-1 said `F2`. Three
documents, three answers, and all three were wrong in the same way: they named
one key for something that is a range and is machine-dependent.
`encore-install.sh:55` already says `Ctrl+Alt+F1..F6` and is the artifact a
stranger actually reads.

Both reasons still hold. This is a genuine **Conflict**, not drift, and the
architect does not get to pick. It is put to the author in `NOTES.md` as
question Q-1, and to the author by the product manager as Q-P1.

**Half of it dissolved on 2026-09-21 and this file did not know.** R-10 was
reworded: it promises an administrator can reach an active terminal *from
another machine*, and never promised a person standing at the terminal a text
login prompt on it. So R-10 is no longer one of the two sides. What is left is
D-017's own reason — a terminal whose network has died would otherwise be
unreachable for good — against R-6. Both still hold, so it stays a conflict,
but it is a smaller and cheaper one than this file described.

**And the mechanism is one character.** `cage -s`
(`encore-kiosk.service:17`) is what permits console switching; without `-s`
there is no route out of the session from the keyboard. The record treated this
as expensive; it is not.

The trade-off: disabling VT switching hardens R-6 and makes R-10 depend
entirely on the network being up, which risks locking a household out of its
own hardware.

**Correction, 2026-09-13, from the product manager, and it is right.** My first
framing of this called that "the exact cost D-006 already accepted". It is not.
D-006 accepted the lock-out risk *while a text console still existed as a way
in*. Closing that console does not re-accept the same cost — it accepts a
strictly larger one, with the last local route removed. Pointing the author at
D-006 as precedent would have understated what they were agreeing to. The
question must be put as a new cost, not a settled one.
