# ADR-0002 — `cage` is the single-window Wayland compositor
- **Date:** 2026-09-13 (recorded; the choice was made earlier and undated)
- **Kind:** reversible

> **Reconstructed from code.** `remmina-kiosk.service:12` runs
> `/usr/bin/cage -s -- /usr/local/bin/remmina-kiosk.sh`. No reason was written
> down.

## Context
D-003 fixes the display server as Wayland. R-6 and C-2 require that the person
at the terminal sees one thing, full screen, with no desktop, no panel, no
launcher and no window controls. A graphical client needs *some* compositor to
draw into; the question is which, and how much of a desktop comes with it.

## Options

**`cage`** — a kiosk compositor whose entire purpose is running one application
full-screen with nothing around it. Roughly the smallest thing that can host a
Wayland client.
*Forever cost:* a small project with a small maintainer pool; no version is
pinned anywhere (see `stack.md`); it gives us no session services, so
`XDG_RUNTIME_DIR`, seat acquisition and audio sockets are all ours to arrange
by hand — which is exactly where D-A4 and D-A6 came from.

**A full desktop session locked down** (GNOME kiosk mode, or Sway with a
stripped config).
*Forever cost:* a whole desktop's worth of settings, keybindings, notification
daemons and dialogs, every one of which is a surface a child can reach and we
must individually disable. C-2 is an absolute, and absolutes are much harder to
defend on a large surface.

## Decision
`cage`, because the requirement is literally "one window and no way out" and
`cage` is the component whose only job is that. Locking a desktop down is
subtractive and never finishes; starting from nothing is additive and does.

## Consequences
**Easier:** R-6 at the desktop layer is free rather than a list of settings.
The moving-part count stays at four.

**Harder:** there is no session infrastructure. Everything a logind user
session would have provided — runtime directory, seat, audio sockets — is now
hand-built in the unit file, and the audio requirement (R-12, C-5) has to be
solved without a session manager's help.

**No longer possible:** showing anything alongside the session — a status bar,
a "not configured" banner, a reconnect message — without adding a component.
Note this collides with the recommended fix for item D-A1 in `debt.md`.

## Revisit when
The terminal needs to display anything of its own, or when audio (R-12) proves
unworkable without a full session — at which point a minimal Sway or a real
user session buys something concrete.
