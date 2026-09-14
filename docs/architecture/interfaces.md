# Interfaces — the contracts, and how stable each is

There is no network API and no code-to-code API. Every contract here is a
**file, a path, or a filesystem convention**, which makes them easy to miss and
easy to break silently. They are listed so a change can name its callers.

---

## I-1 — `kiosk.target` is the activation surface

**Contract:** an administrator activates a terminal with
`systemctl isolate kiosk.target` (now) or `systemctl set-default kiosk.target`
(across reboots), and deactivates with `systemctl set-default graphical.target`
(or `multi-user.target`) plus a reboot.

**Callers:** the administrator, by hand. Later, the install package and any
documented procedure (R-13).

**Stability:** **stable and public.** This is the product's whole user
interface for R-4, R-9 and R-11. It appears in documentation a stranger reads.
Changing the target name after publication breaks every written instruction in
the wild.

**Not yet verified:** that `set-default` is the intended mechanism. The unit
files are silent on it. Marked `assumed`.

---

## I-2 — the service takes `/dev/tty7`

**Contract:** `remmina-kiosk.service:19-20` claims `/dev/tty7` and registers
`UtmpIdentifier=tty7`. Consoles 1–6 remain ordinary text logins.

**Callers:** the administrator relying on another console (R-10); the person at
the terminal, who can also press `Ctrl+Alt+F1` and leave the session (R-6).

**Stability:** **fragile.** On many current distributions `tty7` is where a
display manager already sits, and `tty1` is where the default graphical session
lands. If both want the console, one loses. Also, the same mechanism that
serves R-10 exposes R-6 — see the conflict recorded in `constraints.md`.

---

## I-3 — the profile location

**Contract:** the runner takes **the first `*.remmina` file found** at
`/var/lib/kiosk/.local/share/remmina/`, at depth 1
(`remmina-kiosk.sh:6`). Its format is Remmina's own key/value profile.

**Callers:** the configuration step (not built), the packaging (not built), the
administrator placing a file by hand (today).

**Stability:** **unstable, and it is the contract that matters most.** `head -n
1` over `find` has no defined order, so two profiles on one machine give a
nondeterministic target host. Any configuration step built against R-5 must
either pin an exact filename or reject a second profile.

---

## I-4 — the run-as identity and its home

**Contract:** a system user `kiosk`, group `kiosk`, home `/var/lib/kiosk`,
stated in three places: `remmina-kiosk.service:7-8`, `:10-11`, and again in
`remmina-kiosk.sh:3`.

**Callers:** packaging (must create the user and the directory — neither file
does), the profile path in I-3, and Remmina's own config directory.

**Stability:** **stable in intent, duplicated in fact.** `HOME` is set twice.
The script's copy exists because it is also runnable by hand; that is a
reasonable reason, but it must be recorded as a deliberate duplication rather
than left to be "cleaned up" by someone later.

---

## I-5 — the script's executable path

**Contract:** `/usr/local/bin/remmina-kiosk.sh`
(`remmina-kiosk.service:12`).

**Callers:** packaging. `/usr/local/` is reserved for the local administrator
by the Filesystem Hierarchy Standard and Debian policy; a `.deb` shipping into
it is a policy violation. Packaging will have to move this to `/usr/bin/` or
`/usr/libexec/`, which changes this contract. Flagged now so it is not a
surprise later.

---

## I-6 — the RDP connection itself

**Contract:** RDP to the host named in the profile, with the username and the
stored password from that profile.

**Callers:** the machine being connected to, which is out of scope and which we
may not constrain (D-002).

**Stability:** **stable by necessity.** We do not own the far end, so this
contract can change without us being told. The product must treat every failure
of it as normal operation, not as an error (R-8).

**Identity is part of this contract, as of 2026-09-13.** R-16 was clarified to
mean *the* machine it was configured to connect to, not something answering to
its name. The contract is therefore not "RDP to a hostname" but "RDP to a
host whose identity we can check" — and the shipped profile does not check it
(`cert_ignore=1`, `ignore-tls-errors=1` at
`group_rdp_server_server.remmina:39,97`). That makes R-14 and R-16 one
question: a credential handed to an impostor was never protected by being hard
to read. See `debt.md` items D-A8, D-A5 and D-A7 — pinning belongs in the
configuration step, with the credential decision.
(Source: product manager report, 2026-09-13.)
