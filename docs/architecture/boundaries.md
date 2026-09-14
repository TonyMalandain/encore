# Boundaries — what owns what

Five parts. The first four are ours. The fifth is deliberately not.

---

## 1. The activation switch — `kiosk.target`

**Owns:** whether the machine is a terminal right now, and the ordering
against `multi-user.target`.

**Must not know:** anything about remote desktops, profiles, or credentials. It
is a systemd target and nothing else. If it ever grows product knowledge, the
off-switch stops being a single, cheap, reversible act and R-11 is at risk.

**Current state** (`kiosk.target:5`): `Wants=remmina-kiosk.service`. `Wants` is
a weak dependency — the target is considered reached even if the service failed
to start. See `debt.md`, item D-A3.

---

## 2. The runner — `remmina-kiosk.service`

**Owns:** identity (`User=kiosk`), the console it takes (`/dev/tty7`), the seat
it acquires (`PAMName=login`), the sandbox, and the restart policy.

**Must not know:** which host is being connected to, or anything in the
profile. The unit is identical on every terminal; everything that differs
between houses lives in the profile. This is the boundary that makes R-5
(configuration names the machine) possible without forking the shipped files.

**Current state:** holds no host-specific data. Boundary is respected.

---

## 3. The display cage — `cage`

**Owns:** there being exactly one window, full screen, with no desktop, no
panel, and no launcher around it.

**Must not know:** what is inside the window. `cage -s` is invoked with the
script as its only child (`remmina-kiosk.service:12`); it has no opinion about
remote desktops.

**This is the module carrying R-6 on its own.** If the thing inside the window
ever draws its own menus, settings, or file chooser, `cage` will not stop it —
the cage bounds the desktop, not the application. See `debt.md`, item D-A1.

---

## 4. The session loop — `remmina-kiosk.sh`

**Owns:** finding the profile, launching the client, and getting back to a
remote login screen after any exit.

**Must not know:** the host, the username or the password. It discovers a
profile by glob (`remmina-kiosk.sh:6`) and never reads its contents. That is
the right boundary and it is currently respected.

**Breach to watch:** the script and the unit both promise recovery
(`remmina-kiosk.sh:8` `while true` versus `remmina-kiosk.service:13`
`Restart=always`). Two owners of one job means neither is accountable. See
`debt.md`, item D-A2.

---

## 5. The machine being connected to — **not ours**

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

## The boundary the architecture does not yet have

There is **no configuration boundary**. Today the profile is hand-placed at
`/var/lib/kiosk/.local/share/remmina/*.remmina`, which means the product only
exists on machines the author touched personally. R-5 and R-4 both depend on
this boundary existing. It is the largest structural hole and is tracked in
`debt.md` as item D-A7.
