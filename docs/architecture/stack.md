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
| POSIX `sh` | n/a | — | the runner (16 lines) and the install/uninstall scripts (~170 and ~140) | — |
| PAM (`PAMName=login`) | n/a | — | acquiring a logind seat so libseat can take the console | — |
| CPython | no, **but ≥ 3.10 is required** (corrected 2026-09-23 down from 3.14) | 3.14.7, and the suite also runs on 3.11.16 and 3.10.21 (and OpenSSL 3.5.7 beneath it) | the certificate probe (~500 lines), standard library only — no third-party module, ever | ADR-0008 |

The "version seen working" column is one observation: a clean Ubuntu 26.04
x86_64 VM on 2026-09-23. It is not a support matrix and nothing else has ever
been tried.

**`kbd` was added to this table on 2026-09-23.** It is installed by
`encore-install.sh:83` and the unit depends on `chvt` at `:16` and `:18`. It
had been missing from the record entirely, which means the stack had five parts
in this file and six on a real machine.

**Nothing is version-pinned anywhere, and under D-027 nothing ever will be by a
resolver.** This section used to say "packaging (R-4) is the place to declare
minimum versions, and it must". There is no packaging (D-027, 2026-09-23), so
the only place left is `encore-install.sh` — and it does not check a version of
anything (`:79-83`). Two consequences follow, and both are now the installer's
or nobody's:

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
  (`encore-kiosk.service:35`) precisely because it broke that, so the symptom
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
