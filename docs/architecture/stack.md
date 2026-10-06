# Stack — every choice, and why

The whole system is assembly of parts that already exist on the target machine.
**That is the single best property this architecture has**, and it should be
defended: the problem statement says the pieces are "all free and all present
on an ordinary Linux system", and the product is the assembly, not the parts.

**Corrected 2026-09-23.** This used to read "nothing here was written by us
except sixteen lines of shell". That is no longer true and has not been since
the install scripts landed: the runner is still 16 lines, but
`encore-install.sh` is about 170 and `encore-uninstall.sh` about 140. Under
D-027 that is deliberate — the scripts are the install mechanism, in place of a
package — and it moves the shell we maintain from "a footnote" to "most of the
code in the product". Worth saying plainly, because the old sentence was the
strongest argument in this file and it was quietly becoming false.

| Part | Version pinned? | Version seen working | Role | Decision |
|---|---|---|---|---|
| systemd | no | — (Ubuntu 26.04 stock) | activation, supervision, sandboxing | ADR-0003 |
| cage | no | 0.2.1 | single-window Wayland compositor | ADR-0002 |
| Remmina | no | 1.4.43 | remote desktop client | ADR-0001 |
| FreeRDP (via Remmina) | no | 3.31 | the RDP protocol | ADR-0004 |
| `kbd` (`chvt`) | no | — | bringing the capability's console to the foreground | — |
| H.264 decoder (`libopenh264`, loaded by FreeRDP) | no | **never observed decoding anything, on either family** — the real library was watched *installed* on Fedora 44, 2026-10-05, which is a different claim | software H.264 decoding for the session — there is no hardware path to use | D-036; named on dnf by D-037's withdrawal |
| POSIX `sh` | n/a | — | the runner (16 lines) and the install/uninstall scripts (~170 and ~140) | — |
| PAM (`PAMName=login`) | n/a | — | acquiring a logind seat so libseat can take the console | — |
| CPython | no, **but ≥ 3.10 is required** (corrected 2026-09-23 down from 3.14) | 3.14.7, and the suite also runs on 3.11.16 and 3.10.21 (and OpenSSL 3.5.7 beneath it) | the certificate probe (~500 lines), standard library only — no third-party module, ever | ADR-0008 |

Every version number in that column is one observation: a clean Ubuntu 26.04
x86_64 VM on 2026-09-23. It is not a support matrix.

**Corrected 2026-10-05 — a Fedora terminal has now been watched working, and
this paragraph used to deny it.** It said "nothing in it has been seen working
on Fedora — D-036 claimed the dnf family on 2026-10-04 and no terminal has been
booted there". Three observations on a Fedora 44 machine on 2026-10-05 ended
that: the remote desktop session was on the screen, with no keyring prompt and
no dialog and none of the client's own windows (`docs/tests.md` test 1); the
machine came back into a working session by itself after a reboot, with nothing
done by hand (test 7); and the screen was the same with SELinux permissive and
enforcing (test 14c).

**No version in the column changes, and that is deliberate rather than an
oversight.** Which Remmina, cage and FreeRDP the Fedora machine was running was
not recorded, so the numbers in the column still belong to one family. What is
established on dnf is the distribution release — Fedora 44 — and that every part
in the table did its job there at least once. **The hardware was not recorded
either**, so this column and the paragraph at the end of `constraints.md` C-1
still describe one hardware combination and only one.

**"No version" in that column means two different things, which is why the
decoder row spells its own out instead of writing `—`.** For `kbd`, POSIX `sh`
and PAM, `—` means *present and working on the machine that was watched, with no
version worth recording* — they were on the Ubuntu VM that produced a session.
For the H.264 decoder it would have meant *no
observation has ever established that this part did any work*, and the two
families are unwatched for different reasons. On apt the real library was on
the Ubuntu VM that produced a session — but nothing checked whether that
session negotiated H.264 at all, and the profile settings that would decide it
are the never-examined ones under backlog item 13c, so a working session is not
evidence about the decoder. On dnf, as of 2026-10-05, the *real library* has been
watched arriving — the re-run install asked for `openh264` and `rpm -q openh264
noopenh264` afterwards showed `openh264` installed and `noopenh264` absent — and
a session has been watched appearing on that same machine. **Those two
observations together still do not establish that the session negotiated H.264**,
and the record must not let them, because the same profile settings decide it
there as on apt. A working session is not a working decoder on either family.
The row exists **because** that question is unanswered — a part the file
omits is a part the file disagrees with a real machine about, which is exactly
what happened with `kbd` below.

## The same parts, two package names each — added 2026-10-04 (D-036)

Every part above is present on both families. **Of the eight names the family
block asks for, five carry the identical name on both, two differ by name, and
one is asked for on dnf only.** That last one arrived on 2026-10-05 and it
changed the *shape* of the difference: until then the two lists differed in two
names and were the same length. They are no longer the same length — **apt asks
for seven packages and dnf asks for eight.**

This table exists so the difference lives in the record rather than only in the
installer, and so nobody has to re-derive it. The installer keeps every
family-dependent name inside one marked region — `>>> family block` to
`<<< family block` in `encore-install.sh` — and the single `PACKAGES=` line is
the last statement in it. **That marker is the reference here, not a line
number.** Two line numbers in this section have already gone stale (`:91-92` on
2026-10-05, `:83` before it), and a file whose whole purpose is to stop people
reading the installer should not send them to a line of it.

**Since 2026-10-05 these names are written in a second shipped place, and a
change to one of them has to be made twice.** `encore-uninstall.sh` removes no
packages (R-11) and so prints them instead, for an operator who wants to clean
up by hand — which means it carries its own copy of both lists, inside its own
marked region, `>>> leftovers block` to `<<< leftovers block`. It cannot read
the installer's: the installer need not still be on the machine, and
`/var/lib/encore/encore-install.conf` records nothing about the family. The
installer is the authority, because it is what installed them; a disagreement
is a defect in the uninstaller's copy. `docs/tests.md` 14a check 7 compares the
two lists as strings, so the drift is caught by a check rather than by a reader.

| Part | apt name | dnf name |
|---|---|---|
| Remmina | `remmina` | `remmina` |
| Remmina's RDP plugin | `remmina-plugin-rdp` | **`remmina-plugins-rdp`** |
| compositor | `cage` | `cage` |
| `chvt` | `kbd` | `kbd` |
| sound server | `pipewire` | `pipewire` |
| PulseAudio shim | `pipewire-pulse` | **`pipewire-pulseaudio`** |
| session manager | `wireplumber` | `wireplumber` |
| H.264 decoder | *nothing asked for* | **`openh264`** |

**Why the decoder row has a package on one side and nothing on the other**, and
why that is not an omission. On neither family is the decoder missing as a
*library*: the client's own `freerdp-libs` carries
`NEEDED libopenh264.so.8()(64bit)`, so rpm requires it automatically and the
install is always clean. What differs is *which provider satisfies that
requirement*. On Fedora two packages provide the same soname — `openh264`, from
`fedora-cisco-openh264`, which is enabled by default, and `noopenh264` from
Fedora proper, **a stub that provides the library and decodes nothing**. A fresh
Fedora resolves the requirement to the stub: the link resolves, the install
reports success, and H.264 silently does not work. **That is a named hazard in
this record, `constraints.md` H-1** — a dependency satisfiable without being
satisfied — and this is instance 5 of six. Naming `openh264` swaps the
stub out with no extra flags, because it carries `Obsoletes: noopenh264 < 1:0`.
Debian and Ubuntu ship the real library in `main` with no stub beside it, so on
apt there is nothing to name. Measured on Fedora 44, 2026-10-05:
`openh264-2.6.0-3.fc44` obsoletes `noopenh264 < 1:0`, both packages provide
`libopenh264.so.8()(64bit)`, and the stub ships in the Fedora repository while
the real decoder ships in `fedora-cisco-openh264`. This is **software**
decoding; nothing here is hardware acceleration, which is what D-037's
withdrawal settled. The long form is the comment on the dnf arm of the family
block and `docs/troubleshooting.md`.

**And the eighth package has now been watched — corrected 2026-10-05, the day
after it was written.** This paragraph said the opposite: the only dnf install
then on record (Fedora 44, 2026-10-05, the install half of `docs/tests.md` test
14b) predated the `openh264` line, so the one name that makes the two lists
differ in length was unexercised code, and that was instance 6 of
`constraints.md` H-1 — a test run that predates a line is no evidence about that
line. A later install on Fedora 44 the same day ran *with* the line in place, and
`rpm -q openh264 noopenh264` on that machine then showed `openh264` installed and
`noopenh264` absent.

So **the stub was watched being displaced rather than reasoned about**, which is
what the `Obsoletes:` line above predicted and is the whole point of naming the
package. Instance 6 of H-1 is closed by observation and stays on file there with
its resolution; instance 5's guard — naming `openh264` at all — is now observed
working rather than read off package metadata. What it does **not** close is the
row in the parts table above: the provider on the machine is settled, and whether
any session ever asked it to decode a frame is not.

**The capture tool item 7 needs is a third difference, and it is the one that
will be missed**, because it is not in the installer yet and so will be written
fresh against one family: it is **`freerdp3-x11` on Ubuntu** and **`freerdp` on
Fedora**. Verified on Fedora 44, 2026-10-04: `freerdp-2:3.31.1-1.fc44` provides
`/usr/bin/xfreerdp` and `/usr/bin/wlfreerdp`. Whatever ships item 7's capture
step must carry both names from the first line it is written, not acquire the
second one later — and it also has to be removed again by
`encore-uninstall.sh`, under both names, or C-3's clean undo is broken on one
family and not the other.

**Remmina's secret plugin is a separate subpackage on Fedora**
(`remmina-plugins-secret`), which the installer does not ask for and which may
or may not already be on an adopter's machine. That is not a reason to relax
the suppression — see `debt.md` D-A19, where the suppression is measured to
miss on Fedora for an unrelated reason.

**`kbd` was added to this table on 2026-09-23.** It is installed by the
`PACKAGES=` line in the family block (the reference that went stale as `:83`),
and the unit depends on `chvt` in its `ExecStartPre=` and `ExecStopPost=`
(which is where the stale `:16` and `:18` pointed; they are
`encore-kiosk.service:39` and `:41` today, and this sentence no longer tracks
them). It
had been missing from the record entirely, which means the stack had five parts
in this file and six on a real machine.

**Nothing is version-pinned anywhere, and under D-027 nothing ever will be by a
resolver.** This section used to say "packaging (R-4) is the place to declare
minimum versions, and it must". There is no packaging (D-027, 2026-09-23), so
the only place left is `encore-install.sh` — and its packages step does not
check a version of anything (`:79-83` when written; the step is now the
`case "$PKG_FAMILY"` block, and the reference is deliberately by name). Two
consequences follow, and both are now the installer's or nobody's:

- **The systemd ≥ 254 floor that ADR-0007 depends on is unenforced.** Older
  systemd ignores `RestartSteps=` and `RestartMaxDelaySec=` silently and gives
  flat retries. See `constraints.md` C-1.
- **The CPython ≥ 3.10 floor the probe depends on is unenforced.**
  `encore-probe.py` carries a bare `#!/usr/bin/python3` and asks for no
  version. **Corrected 2026-09-23, the same day it was added.** This said
  ≥ 3.14, and that below it the structurally-invalid-address path crashed
  instead of classifying — true when written, and no longer: the probe no
  longer reads `UnicodeError.reason`, so that path works on every version. What
  is left is syntactic — below 3.10 the module does not import — which fails
  loudly rather than silently. `constraints.md` C-1 carries the full trail;
  the accepted cost is `debt.md` D-A18.
- **A Remmina behaviour change upstream silently changes what a child sees.**
  D-024 says the product tracks current releases and carries no compatibility
  handling, which makes this an accepted cost rather than an oversight — but
  the acceptance is only as good as the check that is not there.

---

## Build-versus-adopt: the standing answer

Every part above is adopted. Nothing is built. The **only** thing this project
should ever build is the assembly and the configuration step — that is the
differentiating logic, and it is precisely the thing the problem statement says
is missing ("what is missing is a way to join the two ends together").

If a future proposal involves writing our own compositor, our own RDP client,
our own supervisor, or our own credential store, the burden is very high and
the answer is almost certainly no.

---

## Alternatives that exist, and why each was rejected

Settled on 2026-09-13 by the author, and recorded as ADR-0005. `BACKLOG.md`
notes a stranger will ask "why not one of the existing projects?" — the
user-facing version of that answer is product work, but the engineering reasons
are here.

- **LTSP** — the long-standing Linux thin-client project, with a documented
  Remmina kiosk recipe. Rejected: it is a fleet platform. It network-boots
  clients from a central image, which means learning and running a boot
  infrastructure, and in practice adopting a distribution to host it. The
  author's fleet is two or three machines (C-7). See ADR-0005.
- **ThinLinc / Thinstation / porteus-kiosk** — all ship an image or a
  distribution. Same conflict with the "capability, not an operating system"
  premise, and the same fleet-scale assumption.
- **`remmina-gnome`, Remmina's own kiosk session** — the closest existing thing
  to what we built. **Rejected on a hard constraint, not on preference:** it is
  an *X11* session (`remmina-gnome-xsession.desktop`, launching
  `gnome-session`), and D-003 fixes the display server as Wayland. It would
  also pull a full GNOME Shell onto an old machine, which is precisely the
  large lockdown surface ADR-0002 chose `cage` to avoid.

  Liveness checked 2026-09-13: not removed upstream and still packaged by some
  distributions as `remmina-gnome-session`, but stagnant — upstream's own
  direction for kiosk use moved to command-line flags, and the session entry
  has a history of issues from appearing in login menus. So the question "is it
  dead?" turned out not to matter; the X11 dependency decides it either way.

**Remmina itself is healthy**, and that is the dependency that counts: v1.4.42
released 2026-02-14, maintained, primary repository on GitLab with a GitHub
mirror. Checked 2026-09-13; 1.4.43 was the version running on the clean VM on
2026-09-23, so the distribution is tracking upstream closely, which is what
D-024 assumes.

Sources: [Remmina Kiosk Edition](https://remmina.org/remmina-kiosk-edition/),
[remmina-gnome-xsession.desktop](https://github.com/FreeRDP/Remmina/blob/master/data/desktop/remmina-gnome-xsession.desktop),
[Remmina tags](https://gitlab.com/Remmina/Remmina/-/tags),
[LTSP Remmina Kiosk wiki](https://github.com/ltsp/ltsp/wiki/Remmina-Kiosk-(RDP,-Spice,-&-VNC)).

---

## Not chosen, and worth naming

- **A display manager in kiosk mode** (LightDM autologin into a session). The
  current design deliberately avoids a display manager entirely, which removes
  a whole component and a whole config format. Good call, kept.
- **A user-level systemd unit** (`systemctl --user`) instead of a system unit.
  Would make `XDG_RUNTIME_DIR`, the Wayland socket and PipeWire correct by
  construction. **Corrected 2026-09-23:** this used to say "exactly the thing
  currently broken by `ProtectHome=true`". `ProtectHome=` is now commented out
  (commented out in `encore-kiosk.service`; the reference used to read `:35`,
  and it is `:58` today) precisely because it broke that, so the symptom
  is gone and the structural point stands on its own — a system unit is still
  hand-building what a user session provides. See `debt.md`, items D-A4 and
  D-A6.

- **A distribution package.** Decided against, by the author, as D-027 on
  2026-09-23: no `.deb` is built and none is planned. Installing is a clone of
  the repository plus `encore-install.sh`; undoing is `encore-uninstall.sh`.
  This is a product decision, not an architecture one, but three architecture
  facts follow from it and are recorded where they bite: `/usr/local/bin` is
  now the correct install path rather than a policy violation
  (`interfaces.md` I-5), nothing declares a dependency version (above), and
  reversibility is kept by our own uninstaller rather than by a package
  manager's file list (`constraints.md` C-3).
