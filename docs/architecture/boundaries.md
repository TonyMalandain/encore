# Boundaries — what owns what

Six parts. The first five are ours. The sixth is deliberately not.

**Names corrected 2026-09-23** to the ones D-022 and D-023 fixed on 2026-09-13
and the code shipped on 2026-09-14. Every `file:line` below was re-checked
against the file on 2026-09-23, not merely renamed.

---

## 1. The activation switch — `encore-kiosk.target`

**Owns:** whether the machine is a terminal right now, and the ordering
against `multi-user.target`.

**Must not know:** anything about remote desktops, profiles, or credentials. It
is a systemd target and nothing else. If it ever grows product knowledge, the
off-switch stops being a single, cheap, reversible act and R-11 is at risk.

**Current state** (`encore-kiosk.target:5`): `Wants=encore-kiosk.service`.
`Wants` is a weak dependency — the target is considered reached even if the
service failed to start. That was item D-A3 in `debt.md`; ADR-0007 closed it
deliberately in favour of `Wants=`, with the reason written down.

---

## 2. The runner — `encore-kiosk.service`

**Owns:** identity (`User=encore`, `Group=encore`, `encore-kiosk.service:7-8`),
the console it takes (`/dev/tty7`, `:27-28`), the foreground console at start
and stop (`chvt`, `:16` and `:18`), the seat it acquires (`PAMName=login`,
`:9`), the sandbox (`:34-36`), and the restart policy (`:19-22`).

**Must not know:** which host is being connected to, or anything in the
profile. The unit is identical on every terminal; everything that differs
between houses lives in the profile. This is the boundary that makes R-5
(configuration names the machine) possible without forking the shipped files.

**Current state:** holds no host-specific data. Boundary is respected.

**One thing it does know that is not about this machine** (`:13-15`): three
absolute paths to Remmina's keyring plugin, one per architecture triplet. That
is knowledge of a *component*, not of a host, so the boundary above survives —
but it means replacing the client is not only ADR-0001's decision to revisit,
it is three lines in the unit as well.

---

## 3. The display cage — `cage`

**Owns:** there being exactly one window, full screen, with no desktop, no
panel, and no launcher around it.

**Must not know:** what is inside the window. `cage -s` is invoked with the
script as its only child (`encore-kiosk.service:17`); it has no opinion about
remote desktops.

**This is the module carrying R-6 on its own.** If the thing inside the window
ever draws its own menus, settings, or file chooser, `cage` will not stop it —
the cage bounds the desktop, not the application. Observed on 2026-09-14 and
again on 2026-09-23: it does not stop the client's connection editor, its file
chooser, or a clickable certificate dialog. See `debt.md`, item D-A1.

**The `-s` in `cage -s` is a policy decision nobody recorded.** It permits
virtual-console switching. It is therefore the one character that decides the
R-6 / D-017 trade, and the product manager has it as an open question with the
author (`docs/product/NOTES.md`, 2026-09-21). It is named here so it stops
looking like a formatting detail.

---

## 4. The session loop — `encore-kiosk.sh`

**Owns:** finding the profile, launching the client, and getting back to a
remote login screen after any exit.

**Must not know:** the host, the username or the password. It discovers a
profile by glob (`encore-kiosk.sh:6`) and never reads its contents. That is
the right boundary and it is currently respected.

**Breach to watch:** the script and the unit both promise recovery
(`encore-kiosk.sh:8` `while true` versus `encore-kiosk.service:19`
`Restart=always`). Two owners of one job means neither is accountable. ADR-0007
decided that systemd owns it and the loop goes; **that decision is not yet
built** — the loop is still there. See `debt.md`, item D-A2.

---

## 5. The configuration step — `encore-install.sh` / `encore-uninstall.sh`

**This boundary did not exist when this document was written. It does now**
(added 2026-09-23; the bottom of this file used to say the architecture had no
configuration boundary at all).

**Owns:** everything that differs between one terminal and the next, and
everything about getting the files onto a machine and off it again. Under
D-027 there will never be a package, so this is the whole of installation:

- the identity and its home (`encore-install.sh:88-94`, `:99-100`)
- the one profile, installed from the template at a **pinned filename** and
  then checked to be the only one (`:118-124`, `:131-132`)
- the password and the key that protects it, both created on this machine
  (`:137-149`) — this is D-025 delivered
- the files themselves and the unit enablement (`:154-158`)
- what the machine was before it was touched (`:105-112`), read back by
  `encore-uninstall.sh:29-39` — this is R-11 stopping being a promise kept by
  somebody's memory

**Must not know:** anything about how the session is drawn. It must not learn
about compositors, consoles or restart policy — those belong to parts 2, 3 and
4, and the installer is already the file with the most knowledge in the
product.

**It does know one thing about the machine, and it should:** whether an SSH
server is running (`:51-60`). It prints a note and does not block. That is a
deliberate line — the product tells the administrator how the way back in
works and does not take the decision from them.

**Boundary risk, named rather than fixed:** the installer knows the profile's
*filename*, the runner knows only a *glob*. Two different views of the same
contract, and the glob is the weaker one (see `interfaces.md` I-3).

---

## 6. The machine being connected to — **not ours**

**Owns:** who signs in, whether they succeed, what their session contains, how
many people work at once, and every file anyone has. This is D-015 and D-002.

**We must not know:** anything about it beyond a hostname, a username, and a
password held in the profile. The product must never grow a feature that
requires the far machine to be configured a particular way. Doing so would
double the surface a stranger has to trust and would make every adopter's host
our support burden.

**The line, exactly:** our job ends when pixels arrive. The login screen the
person types into is already on the far side of the boundary.

---

## What the architecture still does not have a boundary for

**Nothing owns telling anybody that a terminal is stuck.** The unit cannot
report it (the loop never exits), the journal did not record it when it
happened (observed 2026-09-23: a failed connection produced a clickable dialog
on the screen and nothing but "started" and "session opened" in the journal),
and no component exists whose job is to say so. That is not a missing feature —
whether anyone is owed a signal is a product question (Q-5 in `NOTES.md`) — but
it is a missing owner, and it is why the failure above was invisible from every
channel an administrator has.
