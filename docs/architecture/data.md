# Data — what exists, where it lives, who owns it

The product stores almost nothing. That is a deliberate property, and it is
what makes R-11 (deactivating returns the machine to what it was) cheap.

**Names, owners and the "survives" column corrected 2026-09-23.** The paths
carried the pre-D-023 name, and every row said the owner was "the package" —
under D-027 there will never be a package, and the owner is
`encore-install.sh`. The "survives deactivation" column was also conflating two
different acts, which is now split.

---

## The complete inventory

"Deactivate" means setting the default target back. "Uninstall" means running
`encore-uninstall.sh`. They are different acts with different consequences, and
only the second removes the credential.

| Data | Where | Written by | Survives deactivation? | Survives uninstall? |
|---|---|---|---|---|
| Connection profile (host, username, encrypted password) | `/var/lib/encore/.local/share/remmina/encore-kiosk.remmina` | `encore-install.sh:118-124` | yes — the credential is still on disk | no (`encore-uninstall.sh:112-117`) |
| Remmina's encryption key (`secret=`) | `/var/lib/encore/.config/remmina/remmina.pref` | Remmina, on the terminal, during the password step (`encore-install.sh:137-142`) | yes | no |
| What the machine booted into before conversion | `/var/lib/encore/encore-install.conf` | `encore-install.sh:105-112`, root-owned 644 | yes | no — it is consumed first (`encore-uninstall.sh:29-39`) |
| Which target the machine boots to | `/etc/systemd/system/default.target` (a symlink) | `systemctl set-default`, by hand | no — that is the off-switch | restored, not merely removed |
| The unit and target files | `/etc/systemd/system/` | `encore-install.sh:155-156` | yes, inert | no |
| The script | `/usr/local/bin/encore-kiosk.sh` | `encore-install.sh:154` | yes, inert | no |
| The `encore` user and its home | `/etc/passwd`, `/var/lib/encore` | `encore-install.sh:88-94` | yes | no |
| Packages (seven on apt, eight on dnf — `stack.md` has the two-name table) | the system | `encore-install.sh:87` | yes | **yes, deliberately**, and named back to the operator by family (`encore-uninstall.sh`, `>>> leftovers block`) |
| Logs | the journal, via `StandardOutput=journal` | systemd | yes | yes |

**There is no database, no cache the product manages, and nothing that needs
backing up or migrating.** There is now exactly one state file — the install
record — and it exists to remove a dependency on human memory rather than to
hold product state. Keep it that way. Any proposal that introduces further
persistent product state should be measured against R-11 first.

**The install record is a contract, not just data.** It is written by one
script and parsed by another that may be years newer. See `interfaces.md` I-7.

---

## The one secret, and the honest description of how protected it is

R-14 says the connection credential is "kept encrypted… not readable by anyone
who picks the machine up." **The current mechanism does not deliver that.**

Remmina's native storage encrypts the password with 3DES using a 256-bit key
that it writes, base64-encoded, into `remmina.pref` — in an adjacent directory
under the same home. Anyone who can read `/var/lib/encore` can recover the
plaintext in a few lines of Python; there is a Metasploit module that does
exactly this. It is obfuscation against a shoulder-surfer, not protection
against someone who has the machine.

The supported alternative is `remmina-plugin-secret`, which hands the password
to libsecret and a running secret service (gnome-keyring / kwallet). On an
unattended headless terminal there is nobody to unlock a keyring at boot, so
that path needs design work before it can be claimed. See `debt.md`, item
D-A5, and the open question in `NOTES.md`.

**What this means today:** R-14 is marked `intended` in the product record, and
that is correct. Nothing should describe the current state as satisfying it.

Sources: [Remmina FAQ](https://remmina.org/faq/),
[Rapid7 remmina_creds module](https://www.rapid7.com/db/modules/post/multi/gather/remmina_creds/).

---

## The profile cannot be copied without its key file — so we stopped copying it

The first two rows of the inventory are **one unit, not two**. The password in
the profile is decrypted with the key in `remmina.pref`; copy the profile alone
and the terminal gets an undecryptable password and a connection failure with
**no error that names the cause** — a wrong key produces a garbage password,
which is sent and rejected exactly like an ordinary wrong one
(`docs/troubleshooting.md`, "It prompts for a password even though one is
stored").

That was written on 2026-09-13 as the most likely way a first install fails.
**The design now avoids it entirely, and that was confirmed by experiment on
2026-09-23.**

**The key is created on the terminal, during the password step.** The installer
runs the client as the `encore` user with the keyring plugin made inaccessible,
and asks it to store the password into the profile
(`encore-install.sh:137-142`); the client writes a fresh `secret=` into that
machine's own `remmina.pref`. The installer then checks both halves are present
before going any further (`:146-149`). Consequences, and all three are good
ones:

1. **Nothing secret has to travel between machines during setup.** This is
   D-025 delivered rather than intended, and it was the open question in
   `docs/product/NOTES.md` of 2026-09-14 — "must the encryption key travel, or
   can it be born on the terminal?" It can be born on the terminal.
2. **Every terminal has its own key.** Recovering one machine's credential
   tells an attacker nothing about the next machine.
3. **It narrows `debt.md` item D-A5 rather than closing it.** The old text
   said the exposure follows the profile onto every machine it touches; it no
   longer does. What survives is the part that cannot be designed away: on the
   terminal itself, the key and the ciphertext sit under one home directory, so
   anyone who picks the machine up still recovers the password. R-14 stays
   `intended`.

**One new exposure arrived with this, and the installer says so itself.** The
password is passed on a command line inside a transient unit, so it can reach
the journal; `encore-install.sh:173-176` greps for it afterwards and tells the
administrator to rotate it. Honest, and still an exposure — see `debt.md` item
D-A12.

Source: [Remmina FAQ](https://remmina.org/faq/); profile format read at
`encore-kiosk.remmina.template:12`; the on-terminal key confirmed by the
author on a clean Ubuntu 26.04 VM, 2026-09-23. Citation moved on that date off
`group_rdp_server_server.remmina`, an untracked personal profile at the
repository root which is not something we ship.

---

## Data we deliberately do not hold

- **No person's identity or password.** The account login is typed into the far
  machine's login screen and never passes through anything we wrote (D-011,
  D-015).
- **No inventory, telemetry, or record of use.** D-012 rules out managing the
  terminal, so we do not collect anything about it.
- **No clipboard or file history** — though note that the shipped template
  *does* leave the RDP clipboard channel enabled
  (`encore-kiosk.remmina.template:41`), which contradicts D-019. That is a
  known consequence of regenerating the template verbatim from a working
  profile, recorded by the product manager on 2026-09-23. See `debt.md` item
  D-A9.
- **No telemetry from the client either.** The personal `remmina.pref` at the
  repository root turns the client's own news and usage reporting off, but that
  file is not shipped and the installer does not write one — the terminal's
  `remmina.pref` is whatever the client creates during the password step. What
  the client phones home by default on a terminal is unestablished.
