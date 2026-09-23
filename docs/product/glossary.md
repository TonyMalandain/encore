# Glossary

Terms in users' words. The architect may add the code-side name for each.

- **Terminal** — an old computer that has been converted. Sometimes called a
  thin client. It does no work of its own; it shows a session running
  somewhere else.
- **The capability** — the thing the product adds to a machine. It can be
  active or inactive. A machine with it inactive is just an ordinary computer.
- **Activation / deactivation** — switching the capability on or off.
  Deactivation returns the machine to what it was.
- **Kiosk** — the state of a terminal while the capability is active: one
  screen, one thing on it, no way out.
- **The machine being connected to** — the computer that actually runs
  everyone's sessions. Out of scope; the product changes nothing on it.
- **Connection credential** — the one secret a terminal stores. It opens the
  connection and gets you as far as a login screen. It is nobody's identity.
- **Account login** — what a person types at that login screen to actually
  get a session. It belongs to the machine being connected to. The product
  never sees it and does not store it.
- **Terminal administrator** — the person with root on a terminal. The only
  one who can deactivate it.

## Code-side names

Added by the architect. One word, one meaning, across product and code. Where
the code's name differs from the user's word, that is noted as a thing to fix,
not a thing to live with.

| User's word | In the code | Where |
|---|---|---|
| The capability | the `encore-kiosk` target and service (D-022) | `/etc/systemd/system/` |
| Activation | isolating or defaulting to the `encore-kiosk` target | `systemctl set-default` |
| Kiosk | a single-window compositor hosting one client | the `encore-kiosk` service |
| Terminal | the machine running the `encore-kiosk` service | — |
| The identity it runs as | the `encore` user, group and home (D-023) | `/var/lib/encore` |
| The machine being connected to | `server=` in the connection profile | the `.remmina` file |
| Connection credential | `password=` in the connection profile | the `.remmina` file |
| Account login | never appears in the code, by design | — |

**Settled by D-018 and D-022:** a terminal is the machine, the kiosk is the
capability we give it, and everything the product installs is called
`encore-kiosk`. A piece of hardware is never called a kiosk.

**The rename landed on 2026-09-14.** The code had used `kiosk` for the machine,
the user and the home directory, and had carried the remote desktop client's
name in the units — wrong by D-018 and D-022 respectively. Both were one rename
and it is done: the units are `encore-kiosk`, and the identity is `encore`. The
words a reader meets and the words in the code now agree, which is what R-13
needs, because the stranger in `users.md` meets these words before anything
else.

- **Encore** — the name of this product (D-021). What it installs on a machine
  is the kiosk; the machine is a terminal.
