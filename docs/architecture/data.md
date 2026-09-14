# Data — what exists, where it lives, who owns it

The product stores almost nothing. That is a deliberate property, and it is
what makes R-11 (deactivating returns the machine to what it was) cheap.

---

## The complete inventory

| Data | Where | Owner | Survives deactivation? |
|---|---|---|---|
| Connection profile (host, username, encrypted password) | `/var/lib/kiosk/.local/share/remmina/*.remmina` | the terminal administrator | yes — orphaned, harmless, but the credential is still on disk |
| Remmina's encryption key (`secret=`) | `/var/lib/kiosk/.config/remmina/remmina.pref` | Remmina, created on first run | yes |
| Which target the machine boots to | `/etc/systemd/system/default.target` (a symlink) | systemd | no — that is the off-switch |
| The unit and target files | `/etc/systemd/system/` | the package | yes, inert |
| The script | `/usr/local/bin/remmina-kiosk.sh` | the package | yes, inert |
| The `kiosk` user and its home | `/etc/passwd`, `/var/lib/kiosk` | the package | yes |
| Logs | the journal, via `StandardOutput=journal` | systemd | yes |

**There is no database, no state file, no cache the product manages, and
nothing that needs backing up or migrating.** Keep it that way. Any proposal
that introduces persistent product state should be measured against R-11 first.

---

## The one secret, and the honest description of how protected it is

R-14 says the connection credential is "kept encrypted… not readable by anyone
who picks the machine up." **The current mechanism does not deliver that.**

Remmina's native storage encrypts the password with 3DES using a 256-bit key
that it writes, base64-encoded, into `remmina.pref` — in the same directory as
the profile. Anyone who can read `/var/lib/kiosk` can recover the plaintext in
a few lines of Python; there is a Metasploit module that does exactly this.
It is obfuscation against a shoulder-surfer, not protection against someone who
has the machine.

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

## The profile cannot be copied without its key file

The two rows at the top of the inventory are **one unit, not two**. The
password in the profile is decrypted with the key in `remmina.pref`; copy the
profile alone and the terminal gets an undecryptable password and a connection
failure with no clear error message.

This has two consequences, and both were found while writing install steps on
2026-09-13.

1. **It is the most likely way a first install fails for a non-obvious
   reason**, so it belongs in any written installation instructions
   (`README.md`).
2. **It makes the credential-at-rest position worse than `debt.md` item D-A5
   describes.** ADR-0001's deciding reason is that Remmina's GUI builds a
   configuration file you can copy — but "build it in the UI and copy it" in
   fact means copying the secret *and its key* together, so the exposure
   follows the profile onto every machine it touches, not just the terminal.

Source: [Remmina FAQ](https://remmina.org/faq/); profile format read at
`group_rdp_server_server.remmina:2`.

---

## Data we deliberately do not hold

- **No person's identity or password.** The account login is typed into the far
  machine's login screen and never passes through anything we wrote (D-011,
  D-015).
- **No inventory, telemetry, or record of use.** D-012 rules out managing the
  terminal, so we do not collect anything about it.
- **No clipboard or file history** — though note that the current profile
  *does* leave the RDP clipboard channel enabled. See `constraints.md`.
