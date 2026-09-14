# Stack — every choice, and why

The whole system is assembly of parts that already exist on the target machine.
Nothing here was written by us except sixteen lines of shell. **That is the
single best property this architecture has**, and it should be defended: the
problem statement says the pieces are "all free and all present on an ordinary
Linux system", and the product is the assembly, not the parts.

| Part | Version pinned? | Role | Decision |
|---|---|---|---|
| systemd | no | activation, supervision, sandboxing | ADR-0003 |
| cage | no | single-window Wayland compositor | ADR-0002 |
| Remmina | no | remote desktop client | ADR-0001 |
| FreeRDP (via Remmina) | no | the RDP protocol | ADR-0004 |
| POSIX `sh` | n/a | the sixteen-line runner | — |
| PAM (`PAMName=login`) | n/a | acquiring a logind seat so libseat can take the console | — |

**Nothing is version-pinned anywhere.** For a project that installs onto
machines we have never seen, that is a real exposure: a Remmina behaviour
change upstream silently changes what a child sees. Packaging (R-4) is the
place to declare minimum versions, and it must.

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
mirror. Checked 2026-09-13.

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
  construction — which is exactly the thing currently broken by
  `ProtectHome=true`. Worth revisiting; see `debt.md`, item D-A6.
