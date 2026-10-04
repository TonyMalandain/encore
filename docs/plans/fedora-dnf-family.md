# Plan — convert a machine on Fedora, with the same capabilities

Written by the senior engineer, 2026-10-04, for `BACKLOG.md` item 16 (**M**).
Serves R-1, R-2, D-036, D-024, D-003 and repays `debt.md` D-A19.

**Sensitive:** yes, in one place. Step 2 changes how the keyring plugin is put
out of reach while the RDP account's password is written into the profile. If
that suppression misses, Remmina either stores the password somewhere the
terminal cannot read it or blocks on a keyring prompt — so this step decides
whether a credential lands where it is meant to. No new secret, nothing new
leaves the machine, and no permission is widened.

---

## What changes, and for whom

A person with an old Fedora machine can run `encore-install.sh` on it and get
the same terminal an apt machine gets — same identity, same unit, same profile,
same undo. Today the script dies at `apt-get: not found` within seconds, and
`README.md` tells them not to try.

Two things change for the apt adopter too, both repairs: the installer stops
refusing to run on an architecture it has no multiarch triplet for, and it
starts checking that the shipped unit actually hides every copy of the keyring
plugin the machine has, rather than trusting a list of literal paths that is
silent when it is wrong.

**What does not change: nothing is offered on one family and withheld on the
other** (D-036). Only the step that installs software branches.

---

## The component

- **Responsible for:** `encore-install.sh` is the conversion — it brings the
  machine to the state the runner and the unit assume, checks each step it
  cannot afford to get silently wrong, and records what the machine was so the
  undo works years later. `encore-kiosk.service` is responsible for *the
  conditions the client runs under*, of which hiding the keyring plugin is one.
- **Has drifted by:** one thing, in two places, and it is D-A19. The product
  reasons from capability everywhere except where it names Remmina's secret
  plugin, and there it reasons from a distribution's filesystem layout —
  `encore-kiosk.service:28-30` as three literal Debian multiarch paths, and
  `encore-install.sh:42-48` as a fourth path computed from `uname -m` into the
  same multiarch shape. Both were correct for the only family that existed.
  D-036 made them wrong on 2026-10-04 without anyone touching either file.
  `debt.md` D-A19 records the unit. **The installer is the second site and is
  not in the record** — see *For the architect* at the bottom.
- **This change belongs here because:** the installer is the one component
  whose responsibility is "make this machine ready", and which package manager
  the machine has is a fact about this machine. Nothing else in the product
  names a package manager (`encore-kiosk.sh` and `encore-uninstall.sh` were
  re-read on 2026-10-04 and name none), so no second component is involved.

---

## The five design decisions, and why

### 1. The family is detected from capability — `command -v`, not `/etc/os-release`

```sh
if command -v apt-get >/dev/null 2>&1; then …
elif command -v dnf >/dev/null 2>&1; then …
else die …
fi
```

**This is not a preference; D-036 decided it.** Its own words: the install step
"differs by package manager rather than by distribution name". `/etc/os-release`
answers a different question — what the machine calls itself — and turns the
installer into a list of distribution names that must be extended for every
derivative (Linux Mint, Pop!_OS, Nobara, Bazzite, every rebuild) with no way to
notice a missing one. `ID_LIKE` is not even reliably present, and a machine can
set it to anything.

**D-A19 is in the record precisely because a literal layout claim was made
once**, and the cost of that mistake is the argument here: the thing that breaks
when a new distribution appears is any statement the code makes *about*
distributions. `command -v apt-get` makes none. It asks the machine whether it
can do the thing, and the answer is true or false on the machine in front of it.

One consequence, stated so it is not discovered later: `command -v` reads
`PATH`. `encore-install.sh` runs as root under `sudo`, so `PATH` is root's and
both binaries live in `/usr/bin`. A machine whose root `PATH` omits `/usr/bin`
has larger problems than this script.

### 2. Neither → `die`, before anything is asked or changed

The script's existing habit is to refuse loudly and early, and it already has
`die`. The new thing is **where** the check goes: **immediately after the
file-presence loop at `:20-23`, before the SSH hint and before the three
prompts.** Not at the packages step, where it would naturally sit.

The reason is the password. Prompting somebody for a hostname, an account and a
remote password and *then* saying "unsupported package manager" has made them
type a credential for nothing, and it has made them wait through three prompts
to learn a fact the script knew at line 24. The hint block at `:56-65` needs the
family too, which puts detection above it anyway.

Message, naming the capability rather than a distribution:

```
error: no supported package manager found: this needs apt-get or dnf (R-1)
```

Nothing has been written, no package installed, no identity created. An
unsupported machine gets nowhere, which is the requirement.

### 3. Both → apt wins, deterministically, and the choice is printed

A machine with both is real in both directions, measured on 2026-10-04:
Fedora 44 packages `apt` (`apt-0:3.1.16-2.fc44`, which provides
`/usr/bin/apt-get`), and Debian and Ubuntu package `dnf`. `command -v` cannot
tell which one owns the running system's package database.

**apt is checked first and wins.** Two reasons, and the second is the one that
matters:

- R-1 is `real` for apt and `intended` for dnf. On a machine where the evidence
  is ambiguous, the honest default is the family the product has actually been
  watched working on.
- The realistic shape of the ambiguity is an apt machine with `dnf` installed as
  a tool, far more likely than a Fedora machine where somebody has installed
  `apt`. On a machine that has one package manager as a *tool*, the native one
  is the one whose repositories are configured, and the wrong choice fails at
  the install command with a message naming it — loudly, before the identity is
  created.

**I considered and rejected a tie-break that asks which database owns the
running system** (`rpm -q --whatprovides /bin/sh` against `dpkg -S /bin/sh`).
It is more correct and it is the wrong trade here: two more processes, two more
failure modes and a paragraph of explanation, to improve the outcome on a
machine nobody has ever reported.

**What is planned instead is visibility.** The script prints the family it chose
before it installs anything:

```
==> package manager: apt
```

A wrong guess on a dual machine is then a line on the operator's screen rather
than an inference from a confusing failure three steps later. That is the
mitigation; the tie-break is just a rule.

### 4. The package list is one list, with the two divergent names as variables

```sh
PACKAGES="remmina $RDP_PLUGIN cage kbd pipewire $PULSE_SHIM wireplumber"
```

`RDP_PLUGIN` and `PULSE_SHIM` are set in the family block. **Every package name
appears exactly once in the file**, the list keeps the order and shape of the
single line it replaces at `:91-92`, and a reader sees one sequence of seven
rather than two sequences of seven to diff by eye.

Rejected: **two literal lists, one per branch.** It reads well and it is how
this defect class arrives. Five of the seven names would be written twice, and
the next package to be added is already known — `stack.md` says item 7 needs
`freerdp3-x11` on Ubuntu and `freerdp` on Fedora, and warns in its own words
that it "will be missed". With two lists, adding a package to one branch and
forgetting the other is a package missing on one family and present on the
other: a silent, family-specific gap, which is this project's defining failure
shape. With one list, forgetting means the package is missing on **both**
families, which fails everywhere and is found immediately.

Rejected: **a per-package name map or a loop over pairs.** Nothing here needs
it. Seven packages, two differences; two named variables are the cheapest thing
that keeps each name in one place, and the result is still a list a stranger can
read aloud.

### 5. `dnf`, not `dnf5`; `-y -q`, not `-y -qq`; and **no refresh step on dnf**

Measured on Fedora 44 on 2026-10-04, on the author's own machine, read-only:

- `/usr/bin/dnf` is a symlink to `/usr/bin/dnf5` (dnf5 5.4.5.0); `/usr/bin/dnf-3`
  is dnf 4.24.0. **Invoke `dnf`.** It is the name present across the whole
  family and resolves to whichever generation the machine has. `dnf5` is an
  additional name on recent Fedora only, and branching on it would be a second
  detection with no test behind it.
- **`-qq` does not exist on dnf.** `dnf5 --help` gives `-q, --quiet` and
  `-y, --assumeyes`; both have been dnf options for its whole life, so the dnf4
  machines in scope take them too. apt's `-qq` is apt's own doubling convention
  and does not mirror. So: `apt-get install -y -qq` and `dnf install -y -q`.
- **There is no `dnf` analogue of `apt-get update` in this script, and there
  should not be one.** `apt-get update` is not optional on apt: `apt-get
  install` does not refresh and fails outright on an empty or stale list. dnf
  refreshes expired metadata as part of `install`. Adding `dnf makecache` would
  buy nothing and add a network step that can fail on its own — one unreachable
  optional repository would abort, under `set -e`, a conversion that
  `dnf install` would have completed from the remaining repositories.

  This asymmetry is the one place the engineer's instinct will be to mirror apt.
  The comment in the code must say why it is not mirrored, or somebody adds it
  back in six months.

---

## The architect's question: can Remmina simply be told not to load the plugin?

Asked in `debt.md` D-A19 and repeated in item 16: a list of literal paths is a
claim about every distribution the product will ever support and grows by one
line each time, and nobody had investigated whether one setting could replace
it. **CONTRIBUTING's rule is to search before measuring, so I searched. The
answer is no, and it is not a separate ticket to find that out — it is found.**

- The secret plugin is not configuration. Remmina's plugin manager discovers it
  by scanning the plugin directory at startup —
  `remmina_plugin_manager_get_available_plugins()` then
  `remmina_plugin_manager_get_secret_plugin()` — and warns that it is "running
  without a secret plugin" when the scan finds none. There is no key for it.
- **There is no `disable_secret_plugin` or equivalent in `remmina.pref`.** The
  documented preference keys do not include one. The idea was raised on the
  Remmina users list and the maintainer's answer was that they *could* add a
  hidden option, "but not immediately" — in 2019, for 1.3.6. It was never
  added, and 1.4.x went the other way: the hardening that did arrive arrived as
  command-line flags (`--enable-extra-hardening`, `--disable-toolbar`), none of
  which touches the secret plugin.
- The two mechanisms upstream actually documents are **uninstall the plugin
  package** or **hide the `.so`**. Uninstalling is not available to this
  product: R-11 and D-007 require the machine be left unchanged and the
  conversion be reversible, and on Fedora the plugin is a separate subpackage
  that may be something the adopter wants.

**So path-hiding is not a shortcut the product took; it is the only mechanism
Remmina offers.** The literal list stays, which makes step 5 — the installer
checking the list against what the machine actually has — the real answer to the
architect's concern rather than a consolation for it. It converts "grows by one
line per distribution, with no way to notice a missing line" into "grows by one
line per distribution, and refuses to convert a machine whose line is missing."

**What is still open, and is the architect's, not this ticket's:** whether the
installer should stop shipping the list at all and instead write what it found
into a drop-in at `/etc/systemd/system/encore-kiosk.service.d/`. That would
give one discovery feeding both the password step and the unit, and no literal
paths anywhere. It is not planned here because it adds an installed artifact,
which changes what `encore-uninstall.sh` must remove and therefore what C-3's
clean-undo claim covers — a contract across three files, not the insides of
one. D-A19's own *what would repay it* prescribes the fourth line; this plan
does what the debt entry asks and names the alternative.

Sources, so nobody re-searches: the Remmina users list thread on re-enabling
gnome-keyring (lists.remmina.org, August 2019), the Remmina Preferences wiki
page's list of `remmina.pref` keys, and `remmina.c` in the generated Remmina
source documentation.

---

## Seams

Shell, so the seams are blocks and the variables that leave them. These are
exact; do not improvise the names.

### The family block — `encore-install.sh`, new, immediately after `:23`

```sh
# --- which package manager this machine has ---------------------------------

# Asked as a capability, never as a distribution name (D-036): what this
# machine can do, not what it calls itself. A list of distribution names has to
# be extended for every derivative and is silent when it is short — which is
# exactly how D-A19 happened, one file over.
#
# apt is checked first, so a machine carrying both wins for apt: R-1 is `real`
# for apt and `intended` for dnf, and the ambiguous machine should get the
# family this product has actually been watched working on. Fedora packages
# `apt` and Debian packages `dnf`, so both directions are real.
#
# TWO places in this file branch on the family: this block, which holds every
# family-dependent *name*, and the packages step, which holds the two commands.
# A third is a defect — add a variable here instead.
#
# >>> family block — exercised off-target by docs/tests.md test 14a
if command -v apt-get >/dev/null 2>&1; then
    PKG_FAMILY=apt
    RDP_PLUGIN=remmina-plugin-rdp
    PULSE_SHIM=pipewire-pulse
    SSH_UNIT=ssh
    SSH_INSTALL="apt install openssh-server"
elif command -v dnf >/dev/null 2>&1; then
    # `dnf`, not `dnf5`: `dnf` exists across the whole family and is a symlink
    # to dnf5 where dnf5 is what the machine has (Fedora 44, 2026-10-04).
    PKG_FAMILY=dnf
    RDP_PLUGIN=remmina-plugins-rdp
    PULSE_SHIM=pipewire-pulseaudio
    SSH_UNIT=sshd
    SSH_INSTALL="dnf install openssh-server"
else
    die "no supported package manager found: this needs apt-get or dnf (R-1)"
fi

# Each of the seven names appears once. Two of them differ by family; the other
# five are identical, measured on Fedora 44 on 2026-10-04 and recorded in
# docs/architecture/stack.md. One list rather than one per family, so that
# adding a package and forgetting a branch is impossible — the next addition is
# already known to differ (item 7's capture tool).
PACKAGES="remmina $RDP_PLUGIN cage kbd pipewire $PULSE_SHIM wireplumber"
# <<< family block

# Said out loud, before anything is installed: on a machine carrying both
# package managers the choice above is a guess, and this is the line that makes
# it a visible guess rather than a confusing failure three steps later.
echo "==> package manager: $PKG_FAMILY"
```

**Contract of the block**, which the off-target test depends on:

- It is **pure**: it assigns variables, calls `die` on no match, and touches
  nothing else. No file is written, no package queried, no prompt shown. It must
  stay that way — `docs/tests.md` test 14a runs these exact shipped lines by
  extracting them between the two markers and executing them, and a side effect
  added here becomes a side effect of running the test.
- The two marker comments `# >>> family block` and `# <<< family block` are
  **load-bearing**. They are how the test addresses the block without naming
  line numbers that drift. Do not reword them.
- It exports nothing. Every variable is plain shell scope, as everything else in
  the script is.

### The keyring plugin paths — `encore-install.sh`, replacing `:42-48`

```sh
# The keyring plugin must be out of reach while the password is written, or the
# client insists on a secret service that an unattended terminal has nobody to
# unlock. Found, not computed: deriving the path from `uname -m` produced a
# Debian multiarch path on every machine and matched nothing on Fedora, which
# puts the file in /usr/lib64 (D-A19). Asking the machine where the file is
# costs one find and makes no claim about any distribution's layout.
#
# Each path is prefixed `-` so systemd tolerates one that has gone; empty means
# the plugin is not installed, so there is nothing to hide.
SECRET_PLUGINS=$(find /usr/lib /usr/lib64 -name 'remmina-plugin-secret.so' \
                 2>/dev/null | sed 's|^|-|' | tr '\n' ' ')
```

and at `:173`, `-p "InaccessiblePaths=-$SECRET_PLUGIN"` becomes

```sh
    -p "InaccessiblePaths=$SECRET_PLUGINS" \
```

The `-` prefixes now come from the `sed`, so the `-` that was spliced in at
`:173` goes. `SECRET_PLUGIN` (singular) ceases to exist; so do `TRIPLET` and the
`case "$(uname -m)"` around it, which had no other reader.

### The coverage check — `encore-install.sh`, new, inside step 6

Placed immediately after the `install -m 644 … /etc/systemd/system/` at `:190-191`
and **before** `systemctl daemon-reload`.

```sh
# The unit hides the plugin by naming literal paths, and the leading `-` on
# each tells systemd to tolerate a path that is not there. That is what lets
# one unit cover several layouts — and it is also what hid every path being
# wrong on Fedora, in a unit that started perfectly clean (D-A19). So the
# coverage is checked here, on the machine, where it can be asked rather than
# assumed. $SECRET_PLUGINS is unquoted on purpose: the word splitting is the
# mechanism. It is empty when the plugin is not installed, and the loop then
# does nothing, which is correct — there is nothing to hide.
for p in $SECRET_PLUGINS; do
    grep -qF -- "InaccessiblePaths=$p" /etc/systemd/system/encore-kiosk.service ||
        die "encore-kiosk.service does not hide ${p#-} — the terminal would stop at a keyring prompt nobody can answer. Add to the unit: InaccessiblePaths=$p"
done
```

**What misuse this makes impossible:** the whole of D-A19, not its Fedora
instance. A distribution with a layout nobody has met gets a loud failure at
install time, on the machine, naming the exact line to add — instead of a
terminal that converts cleanly and then shows a child a keyring prompt. It
costs six lines and it is the only part of this ticket that can be *watched*
without a Fedora machine.

It couples to the unit's formatting: one path per `InaccessiblePaths=` line,
`-` prefixed, nothing after it. Step 3 keeps that shape, and the comment at the
top of the unit's block says so.

---

## Steps

Seven, in this order. **Steps 1 to 6 are one commit each; step 7 is the last
thing that happens** and may not be done earlier — see the ordering guard in
`BACKLOG.md`.

This repository has no automated harness for shell. The only suite is
`encore-probe-test.py`, which covers the probe. **So "test first" here means
what it meant for item 5: the `docs/tests.md` entry, with its exact command and
its pass condition, is written before the code it describes.** That is step 1,
and it is weaker than a unit test; this plan says so rather than pretending
otherwise. What rescues it is that three of the four checks in test 14a can be
run immediately, off-target, by the engineer, against the real shipped files.

**Fabricated inputs in a temporary directory are allowed. Standing in for
anything the product ships or the system provides is not** — no stub `apt-get`
on `PATH`, no substituted copy of `encore-kiosk.service` under
`/etc/systemd/system`, no fake `/usr/lib` tree. The author has refused that
twice and it is a standing constraint. Every check below respects it: they run
the real shipped lines on a real machine, or they exercise a *pipeline* against
files made in `mktemp -d`, which is what was accepted for item 5's 12a and for
the `find` correction in `docs/troubleshooting.md`.

### Step 1 — `docs/tests.md`: the Fedora tests, written before the code  [feature]

- **Then:** add one row to the summary table and one new section. No code in
  this commit.
- **The new row:**

  | 14 | Does a dnf-family machine convert and run? | Never run — see 14a for what has been checked off-target |

- **Also in this commit**, one sentence under *Status column is what has
  actually been watched*: every status in tests 1 to 13 is an apt-family
  observation unless a Fedora machine is named in it, and none is; D-036
  claimed the dnf family on 2026-10-04 and nothing has been watched there.
- **Test 14 has three parts**, following the 5a/5b and 12a/12b convention:

  **14a — off-target: no Fedora terminal needed.** Four checks. Each is run by
  the engineer during this ticket and its result recorded here.

  1. *The installer still parses, on both shells the targets use.* `/bin/sh` is
     `bash` on one machine in this project and `dash` on another, and that has
     mattered before.
     ```sh
     sh -n encore-install.sh && dash -n encore-install.sh && echo "syntax ok"
     ```
     Pass: `syntax ok`.
  2. *The unit still parses, and no key in it is being ignored.*
     ```sh
     systemd-analyze verify ./encore-kiosk.service
     ```
     Pass: **no line containing `Unknown key` and no line containing
     `InaccessiblePaths`.** On a machine without the client installed it also
     prints `Command /usr/bin/cage is not executable` — expected, not a
     failure. **Read the output: the exit status is 0 even when it has
     complained** (checked on Fedora 44, 2026-10-04), so a passing exit status
     here means nothing at all.
  3. *The family block really produces the right family and the right seven
     packages, on a real machine of each family.* This runs the shipped lines
     themselves — it fakes nothing and installs nothing:
     ```sh
     { echo 'die() { echo "error: $*" >&2; exit 1; }'
       sed -n '/^# >>> family block/,/^# <<< family block/p' encore-install.sh
       echo 'echo "$PKG_FAMILY|$SSH_UNIT|$PACKAGES"'
     } | sh
     ```
     Pass, on the author's Fedora 44 machine — read-only, nothing installed:
     ```
     dnf|sshd|remmina remmina-plugins-rdp cage kbd pipewire pipewire-pulseaudio wireplumber
     ```
     Pass, on the apt test VM:
     ```
     apt|ssh|remmina remmina-plugin-rdp cage kbd pipewire pipewire-pulse wireplumber
     ```
     And the machine with neither, which needs no machine of its own — the
     fragment runs with an empty `PATH`, so `command -v` finds nothing. `sed`
     keeps the real `PATH`; only the fragment loses it. **The interpreter must
     be named absolutely** — `env PATH=/nonexistent sh` cannot find `sh`
     either, and gives you exit 127 and a misleading `env: 'sh': No such file`
     instead of the check you wanted. Checked both ways on 2026-10-04:
     ```sh
     { echo 'die() { echo "error: $*" >&2; exit 1; }'
       sed -n '/^# >>> family block/,/^# <<< family block/p' encore-install.sh
       echo 'echo "NOT REACHED"'
     } | env PATH=/nonexistent /bin/sh; echo "exit=$?"
     ```
     Pass: `error: no supported package manager found…`, `exit=1`, and **no
     `NOT REACHED`**.
  4. *The coverage check finds a missing path, and says which.* Fabricated
     inputs only:
     ```sh
     T=$(mktemp -d)
     mkdir -p "$T/usr/lib/x86_64-linux-gnu/remmina/plugins" "$T/usr/lib64/remmina/plugins"
     touch "$T/usr/lib/x86_64-linux-gnu/remmina/plugins/remmina-plugin-secret.so" \
           "$T/usr/lib64/remmina/plugins/remmina-plugin-secret.so"
     find "$T/usr/lib" "$T/usr/lib64" -name 'remmina-plugin-secret.so' | sed 's|^|-|' | tr '\n' ' '
     ```
     Pass: both paths, each `-` prefixed, on one line. Then the grep half,
     against a copy of the real unit in `$T` — a copy used as test input, never
     a substitute for the installed one:
     ```sh
     cp encore-kiosk.service "$T/u"; grep -qF -- "InaccessiblePaths=-/usr/lib64/remmina/plugins/remmina-plugin-secret.so" "$T/u" && echo covered
     grep -v 'lib64' "$T/u" > "$T/u2"; grep -qF -- "InaccessiblePaths=-/usr/lib64/remmina/plugins/remmina-plugin-secret.so" "$T/u2" || echo "missing, as it should be"
     rm -rf "$T"
     ```
     Pass: `covered`, then `missing, as it should be`. The second half is the
     red case: without it, the check has never been seen to fail.
  5. *An empty `InaccessiblePaths=` is accepted*, which is the case where the
     plugin is not installed. One command, on the apt test VM — **I did not run
     this; running a transient unit is not read-only inspection and this
     machine is out of scope (D-002)**:
     ```sh
     systemd-run --quiet --pipe -p "InaccessiblePaths=" /bin/true; echo "exit=$?"
     ```
     Pass: `exit=0`. The unit-file form of the same empty assignment was
     verified with `systemd-analyze verify` on Fedora 44 on 2026-10-04 and
     parses.

  **14b — a scratch Fedora machine converts.** Never run. Needs a Fedora
  machine that can be snapshotted and reverted; not the author's workstation,
  which is the RDP target and out of scope (D-002). Record, in order and by
  observation:
  - `==> package manager: dnf` appears before anything is installed.
  - the seven dnf package names install.
  - the keyring suppression during the password step: `==> password` completes
    and neither of the two guards after it fires. **On Fedora today this is
    exactly where the installer stops** — the password is not written into the
    profile and `no password stored in the profile` is the error — so this line
    is the one that proves step 2 did its job.
  - the unit coverage check passes silently, or dies naming a path.
  - then tests 1, 3, 4, 7 and 10 from this file, which have never been run on
    this family.

  **14c — does SELinux change what the screen shows?** Never run. **The
  architect named this as the one prerequisite before a Fedora terminal may be
  called working** (`constraints.md` C-1). Everything measured there is policy
  and labelling; none of it is a terminal, and a refusal can be invisible —
  that policy carries 102 `dontaudit` rules reaching `unconfined_service_t`,
  164 reaching `unconfined_t` and 121 reaching `init_t`, **so a clean AVC log
  is not evidence of anything.** After 14b, on the same machine:
  ```sh
  getenforce
  sudo setenforce 0 && getenforce
  sudo systemctl isolate encore-kiosk.target      # watch the screen, write down what it shows
  sudo setenforce 1 && getenforce
  sudo systemctl isolate encore-kiosk.target      # watch the screen again
  ```
  Pass: **the two screens are the same.** Then SELinux is out of the picture
  for good and `constraints.md` C-1 can say so from observation. If they
  differ, `sudo semodule -DB` to switch the `dontaudit` rules off, repeat the
  enforcing run, and `sudo ausearch -m avc -ts recent` names the rule — then
  stop and hand it to the architect, because a policy module is a Fedora-only
  component and weakens D-036's one-implementation claim.
  Note what this does **not** cover: `systemctl isolate` does not reproduce
  boot conditions, so the enforcing/permissive *comparison* is this pair of
  isolates, and a real Fedora reboot is test 7 on this family under 14b.

### Step 2 — the installer finds the keyring plugin instead of computing it  [repair]

- **Test first:** 14a checks 1 and 4 from step 1, which exist by now.
- **Then:** `encore-install.sh` — replace `:42-48` and the `-p` line at `:173`
  with the forms given under *Seams*. Delete `TRIPLET`, `SECRET_PLUGIN` and the
  `case "$(uname -m)"`.
- **Why here:** the installer is responsible for the conditions under which the
  password is written, and where a file is on this machine is a question for
  this machine.
- **Behaviour change:** two, both deliberate, and the second must be in the
  commit message.
  1. On apt, **none that can be observed**: `find` locates the same multiarch
     path the triplet computed. On dnf it is the difference between the
     password step working and the installer dying.
  2. **The installer no longer refuses to run on an architecture it has no
     multiarch triplet for.** That `die "unsupported architecture"` was never a
     product limit — R-2 says no particular hardware is required and names
     32-bit and ARM as in scope — it was an artefact of needing to build a
     triplet. Removing the need removes the refusal. A machine on, say,
     riscv64 will now be converted rather than turned away at line 46. Nothing
     has ever been watched on such a machine, and nothing about it is being
     claimed; the point is that the script no longer makes a claim either way.

### Step 3 — the unit hides the dnf-family path too  [repair]

- **Test first:** 14a check 2.
- **Then:** `encore-kiosk.service` — add, after `:30`:
  ```ini
  InaccessiblePaths=-/usr/lib64/remmina/plugins/remmina-plugin-secret.so
  ```
  Keep the `-` on all four, which is what lets one unit cover both families and
  the architectures a given machine does not have. Verified on Fedora 44 on
  2026-10-04: `remmina-plugins-secret-1.4.41-2.fc44` owns exactly
  `/usr/lib64/remmina/plugins/remmina-plugin-secret.so`, confirmed with
  `dnf repoquery --whatprovides` as well as `-l`.
- **And replace the one-line comment at `:27`**, which says what the lines do
  and not what is dangerous about them:
  ```ini
  # Keep the client away from gnome-keyring: a secret service wants a human to
  # unlock it and an unattended terminal has none. The leading `-` makes
  # systemd tolerate a path that is not on this machine, which is what lets one
  # unit cover three Debian multiarch layouts and Fedora's /usr/lib64 — and is
  # also what let ALL FOUR be wrong on Fedora in a unit that started perfectly
  # clean (D-A19). One path per line, `-` prefixed, nothing after it:
  # encore-install.sh greps these lines for every copy of the plugin the
  # machine actually has, and refuses to finish if one is not named.
  ```
- **Why here:** the unit is responsible for the conditions the client runs
  under. It cannot run `find`, so it keeps a literal list; the installer, which
  can, is what checks the list is complete. The asymmetry is deliberate and the
  comment names it.
- **Behaviour change:** on dnf, the suppression starts working. On apt, none —
  the fourth path is absent and the `-` tolerates it, as it already does for
  the two architectures the machine is not.

### Step 4 — the family block, the packages step and the SSH hint  [feature]

- **Test first:** 14a check 3, which will fail before this step because
  `# >>> family block` does not exist yet, and must then pass on the author's
  Fedora machine and on the apt VM.
- **Then:** `encore-install.sh`, three edits.
  1. The family block from *Seams*, immediately after the file-presence loop at
     `:23` and above the `# --- your way back in ---` comment.
  2. The SSH hint at `:63` becomes
     ```sh
     echo "    $SSH_INSTALL && systemctl enable --now $SSH_UNIT"
     ```
     The `is-active` test at `:56-57` already tries both `ssh` and `sshd` and
     needs no change — it was family-agnostic by luck, and only the printed
     advice was wrong. Verified on Fedora 44 on 2026-10-04: the package is
     `openssh-server` under the same name, and it ships `sshd.service` (and a
     `sshd.socket`), so `systemctl enable --now sshd` is right.
  3. The packages step at `:86-92` becomes:
     ```sh
     echo "==> packages"
     # The sound server the runner starts for itself inside the kiosk session —
     # the pipewire, PulseAudio-shim and wireplumber entries in $PACKAGES. A
     # minimal install may not carry them, and without them the terminal is
     # silent.
     #
     # Two commands, not one with a variable in it, so that what runs as root
     # on somebody's machine reads as a command. $PACKAGES is unquoted on
     # purpose: the word splitting is how seven names become seven arguments.
     #
     # There is no `dnf` line matching `apt-get update`, and adding one would
     # be a mistake: `apt-get install` does not refresh and fails outright on a
     # stale list, while dnf refreshes expired metadata as part of `install`.
     # A `dnf makecache` would buy nothing and add a network step that can fail
     # on its own — one unreachable optional repository would abort, under
     # `set -e`, a conversion that `dnf install` would have completed.
     case "$PKG_FAMILY" in
         apt) apt-get update -qq
              apt-get install -y -qq $PACKAGES ;;
         dnf) dnf install -y -q $PACKAGES ;;
     esac
     ```
     No `*)` arm: the family block already died on anything else, 60 lines
     earlier, and a second unreachable `die` here would suggest the first one
     is not trusted.
- **Why here:** which package manager the machine has is a fact about this
  machine, and making the machine ready is what this script is for.
- **Behaviour change:** a dnf machine installs the seven packages it needs. An
  apt machine runs the same two commands it ran before, with one new line of
  output naming the family. A machine with neither stops at line 24 instead of
  at `apt-get: not found` after three prompts.

### Step 5 — the installer refuses to finish if the unit misses a plugin path  [feature]

- **Test first:** 14a check 4.
- **Then:** the `for p in $SECRET_PLUGINS` loop from *Seams*, in step 6 of the
  script, after `install -m 644 … /etc/systemd/system/` and before
  `systemctl daemon-reload`.
- **Why here:** this script's job includes checking the steps it cannot afford
  to get silently wrong, and it already dies on five of them — a profile that
  still says `CHANGEME`, a profile that says `sound=remote`, a directory owned
  by the wrong user, a missing key, a missing stored password. This is the
  sixth and it is the same shape.
- **Behaviour change:** on a machine whose plugin layout the unit does not
  name, conversion stops with the line to add. On every machine met so far,
  nothing. If the plugin is not installed at all — which on Fedora is the
  common case, since `remmina-plugins-secret` is a separate subpackage the
  installer does not ask for — the loop body never runs, which is correct:
  there is nothing to hide.
- **This is the one step the author can cut** without touching the rest. It is
  last among the code steps for that reason. The engineer does not cut it.

### Step 6 — `docs/troubleshooting.md`: the sound fix names both families  [feature]

- **Then:** at `:413`, the fix cell reads
  `apt install pipewire pipewire-pulse wireplumber` — an apt-only command with
  the apt-only name, given to somebody whose terminal has no sound. Make it
  carry both, in the same style the keyring section already uses after the
  architect's correction. The two divergent names are in
  `docs/architecture/stack.md`; link rather than restating the table.
- **Why here:** `troubleshooting.md` is what a person reads during a bad
  evening. A command that cannot work on their family is worse than no command.
- **Behaviour change:** none. Documentation.
- **Do not touch the keyring section** at `:300-336`. It is the architect's
  correction from 2026-10-04 and it carries the by-hand workaround for D-A19.
  Once step 3 lands the workaround is no longer needed — **say so in the
  handover and let the architect retire it**, because that file's account of
  D-A19 and `debt.md`'s are one record.

### Step 7 — `README.md`: the Requirements bullet  [feature, and it goes last]

- **Then:** replace `:19-20`. Proposed wording, **for the product manager to
  review** — the honesty is the requirement, the words are theirs:

  ```markdown
  - **A Linux using `apt` or `dnf`.** Watched working on Raspberry Pi OS
    "trixie" (October 2025), Ubuntu 26.04 and Debian 13 — or newer. **Fedora is
    handled by the installer and has never been watched working:** no Fedora
    machine has been converted and seen running, so you would be the first.
    No other package manager is supported.
  ```

  Three things it does on purpose:
  - **It says what has been watched and what has not, in the place the decision
    is made.** A stranger deciding whether to install reads this bullet and
    nothing else.
  - **It does not become a known issue.** CONTRIBUTING draws the line: a known
    issue is something this software does wrong, and never having been watched
    on Fedora is not a defect — it is the limit of the evidence. The
    Requirements list already carries limits of qualification this way; the
    `wireplumber` bullet two lines down does exactly the same job.
  - **It names no ID.** The README references `debt.md` and `BACKLOG.md` by
    link and never by number, and this bullet keeps to that.
- **This step may not land before step 4.** `BACKLOG.md` carries the guard in
  its own words: the README is the one document a stranger meets before
  installing, and naming a platform there that the installer cannot handle is a
  false statement to the person least able to detect it.
- **Behaviour change:** none. Documentation.

---

## Callers to update

**No contract change.** Nothing outside `encore-install.sh` reads any variable
it sets, and the two scripts that could have cared do not: `encore-kiosk.sh` and
`encore-uninstall.sh` name no package manager, re-read on 2026-10-04.
`encore-install.conf`, the one interface between the installer and the
uninstaller (`encore-install.sh:127-134`, read by `encore-uninstall.sh`), gains
no field and loses none.

One near miss worth naming: `encore-uninstall.sh` does not remove packages at
all, so the two divergent names create no second site there. That stops being
true when item 7 adds `freerdp3-x11`/`freerdp`, which must be removed under both
names or C-3's clean undo is broken on one family and not the other —
`stack.md` already says so.

---

## Already checked

Do not survey these again; verify anything you depend on at the point you
depend on it.

- **Measured on the author's Fedora 44 machine, 2026-10-04, read-only, nothing
  installed:** `/usr/bin/dnf` → `/usr/bin/dnf5` (5.4.5.0), `/usr/bin/dnf-3` is
  4.24.0; `dnf5 --help` offers `-q/--quiet` and `-y/--assumeyes` and **no
  `-qq`**; `apt-get` is absent but `apt` is packaged
  (`apt-0:3.1.16-2.fc44`, providing `/usr/bin/apt-get`), so a both-present
  machine is real in that direction too;
  `remmina-plugins-secret-1.4.41-2.fc44` owns
  `/usr/lib64/remmina/plugins/remmina-plugin-secret.so` and nothing else
  matching; `openssh-server` is the same package name and ships
  `sshd.service` and `sshd.socket`; `systemd` is 259.
- **`systemd-analyze verify` behaves as the tests above need**, checked on
  Fedora 44 on 2026-10-04: it reports `Unknown key 'InaccesiblePaths'` for a
  misspelled property, it accepts one `InaccessiblePaths=` per line, a
  space-separated list on one line, and an empty assignment — and it **exits 0
  while warning**, so the exit status is worthless and the output is what
  counts.
- **`sh -n encore-install.sh` passes today**, so a failure after an edit is the
  edit.
- **The three callers of the thing being changed:** `SECRET_PLUGIN` is set at
  `encore-install.sh:48` and read only at `:173`; `TRIPLET` is set at `:42-47`
  and read only at `:48`. Nothing else in the repository reads either.
- **The SELinux question is closed and needs nothing from this ticket.**
  `constraints.md` C-1 measured it against the live kernel on Fedora 44 on
  2026-10-04 — labels, `seusers`, `get_default_context`, the `nnp_transition`
  permission and the `matchpathcon` table. **There is no SELinux step on either
  family, no `semanage`, no `restorecon`, no policy module and no SELinux
  branch anywhere in the installer, and `/var/lib/encore` is not relabelled.**
  The reflex that would break a working terminal is named there too:
  `semanage fcontext -a -t user_home_dir_t "/var/lib/encore(/.*)?"`. **Do not
  write it.** What is left is 14c, which is an observation on a machine, not
  code.

---

## Out of scope

- **`docs/product/`.** R-1 already says `real` for apt and `intended` for dnf,
  which is correct and stays correct — **do not promote it.** D-036 is closed.
  Both are the product manager's.
- **`docs/architecture/constraints.md` and `overview.md`**, which still read
  apt-only in places. `BACKLOG.md`'s ordering guard assigns them to the
  architect by name.
- **`docs/architecture/debt.md`.** D-A19 is repaid by steps 2 and 3, and the
  installer is a second site the entry does not mention. Report both; the
  architect writes them.
- **`BACKLOG.md`.** Item 16 is not finished when this lands — see *the honest
  end state* below — and in any case ordering is the author's.
- **The keyring section of `docs/troubleshooting.md`** (`:300-336`). Step 6
  touches one table cell at `:413` and nothing else in that file.
- **`encore-kiosk.sh` and `encore-uninstall.sh`.** They name no package
  manager. Do not open them.
- **Item 7's capture tool** (`freerdp3-x11` / `freerdp`). The one-list shape in
  step 4 is what will make it cheap; adding it now is a different ticket.
- **`remmina-plugins-secret`.** Do not add it to `$PACKAGES` on either family.
  The product hides the plugin rather than managing it, so that the machine is
  left unchanged and the conversion stays reversible (R-11, D-007).
- **A `--dry-run` or a `--family` flag on `encore-install.sh`.** Tempting,
  because it would make the family block trivially testable. It is a new
  user-facing contract on the one script that runs as root on somebody's
  machine, it would need documenting in the README, and test 14a check 3 gets
  the same evidence by running the shipped lines as they are.

---

## Stop and escalate if

- **The family block needs a third branch**, or a package name turns out to
  differ a third way, or something in the five "identical" names is not
  identical on the machine in front of you. The record says seven names and two
  differences; a third difference is a change to what D-036 priced.
- **14b dies anywhere other than where this plan says it will.** The expected
  failure before step 2 is `no password stored in the profile`; anything else is
  a fact nobody has.
- **14c's two screens differ.** That is an SELinux finding, it contradicts
  `constraints.md` C-1, and a policy module is a Fedora-only component and
  therefore the architect's and the product manager's, not yours. Collect
  `semodule -DB` plus `ausearch -m avc -ts recent` and stop.
- **`find /usr/lib /usr/lib64` returns a path with a space in it.** The
  space-separated list in `SECRET_PLUGINS` cannot carry it, and neither can the
  unit-file syntax it is compared against. No such machine is known. Do not
  invent a quoting scheme — stop and say so.
- **Any step needs a decision this plan did not make.** There should be none.

---

## The honest end state of this ticket

Say this in the handover, in these terms, because the temptation to call it done
is the thing the project's rules exist to resist.

**What will be true:** `encore-install.sh` handles both families; D-A19 is
repaid at both sites and the class of defect is caught at install time on any
future layout; the README is honest; test 14a has been **watched**, off-target,
on both a real Fedora machine and a real apt machine, with nothing mocked.

**What will not be true:** **no Fedora machine has been converted, and no
Fedora terminal has been seen working.** 14b and 14c are never run. Tests 1 to
13 remain unrun on the dnf family. R-1 stays `intended` for dnf, and `stack.md`
keeps its line that nothing in the stack has been seen working there.

**So item 16 is not done.** Its own text sets the bar: "this item is not done
when the script branches, it is done when a Fedora terminal has been seen
working end to end." The code half can be closed and reviewed; the item stays
open on 14b and 14c, which need a scratch Fedora machine somebody can snapshot
and revert — not the author's workstation, which is the RDP target and out of
scope (D-002). **The engineer does not tick item 16 and does not promote R-1.**
