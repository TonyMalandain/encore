# ADR-0001 — Remmina is the remote desktop client
- **Date:** 2026-09-13 (recorded; the choice was made earlier and undated)
- **Kind:** reversible

> **Reason confirmed by the author on 2026-09-13**, after this ADR was first
> written from a code read. The author's stated reasoning was stronger than the
> reconstruction, and the Decision section below has been rewritten to match it.
> The reconstruction had missed the profile-builder argument entirely, which
> turns out to be the load-bearing one.

## Context
R-6 requires the terminal to show a remote session and nothing else, and R-8
requires it to return there after any failure. Something has to speak a remote
desktop protocol to the configured host and draw the result. It must exist in
the apt archives (D-003) and run on old hardware under Wayland.

## Options

**Remmina** — a general client with a plugin per protocol, packaged everywhere
in the apt family, and with an existing kiosk story.
*Forever cost:* it is a full graphical application with its own UI, its own
preferences, its own profile format and its own credential store. We inherit
all four whether we want them or not — and three of them have already produced
debt (items D-A1, D-A5, D-A7 in `debt.md`). It also does not exit on
disconnect by default, which is the behaviour R-8 depends on
([upstream issue 3113](https://gitlab.com/Remmina/Remmina/-/issues/3113)).

**FreeRDP's `xfreerdp` / `sdl-freerdp` directly** — the protocol library
Remmina already uses, driven from the command line.
*Forever cost:* no profile format, so we would have to invent configuration
storage ourselves; RDP only, so changing protocol later means changing client.
But: no UI to escape from, no credential store to mis-trust, and arguments
instead of a profile file — which removes three of the four inherited costs
above.

## Decision
Remmina, for two reasons given by the author.

1. **It is already packaged on every apt-family distribution**, which matches
   D-003 and means the install adds nothing exotic.
2. **Its own interface builds the configuration files, which can then be
   copied and reused.** An administrator creates a connection in a familiar
   GUI on a machine they already use, confirms it works, and copies the
   resulting file onto the terminal.

The second reason is the one that decides it, and it is worth more than it
first appears. R-5 needs a way to name the machine being connected to, and the
absence of a configuration step is the largest hole in the design (item D-A7 in
`debt.md`). Remmina hands over a *working configuration story for free*: a
tested profile format, and a graphical editor for it that the administrator
already knows. Driving FreeRDP directly means designing that format, building
whatever writes it, and testing it — the alternative is not "fewer parts", it
is "the same parts, written by us".

The author adds that they are not committed to Remmina if something better
appears. See *Revisit when*.

## Consequences
**Easier:** a working prototype with sixteen lines of shell. Protocols other
than RDP are a profile edit, not a rewrite.

**Harder:** every one of Remmina's own surfaces is now ours to suppress. The
no-profile path starts a full application in front of a child (D-A1). Its
credential store is obfuscation, not encryption, and R-14 is written against it
(D-A5). Its profile format is now, by accident, our configuration interface
(I-3, D-A7).

**No longer possible:** claiming a minimal attack surface without qualification
— there is a complete GTK application on the terminal.

## Revisit when
The author is open to changing this, so the triggers are worth being precise
about. Reviewed 2026-09-13; **the answer today is keep Remmina**, because each
trigger below is either not met or would not be improved by switching.

- **The no-profile fallback cannot be made safe.** *Not met.* It is fixable by
  removing the fallback and adding the hardening flags upstream provides. This
  is the strongest argument for leaving Remmina — a client with no UI has no UI
  to escape from — but it is a small fix, not a reason to change client.
- **The credential store forces us off.** *Would not help.* Passing a password
  to FreeRDP on a command line is worse, not better: it is visible to anyone
  who can list processes. The secret still has to live in a file we own.
  Switching moves this problem rather than solving it.
- **The configuration step ends up defining its own format anyway.** *The real
  trigger, and still open.* If the work under D-A7 concludes that Remmina's
  profile format cannot carry what configuration needs — certificate pinning
  and audio defaults are the likely pressure points — then the profile format
  is carrying no weight, the GUI-builder argument collapses with it, and
  driving FreeRDP directly becomes simpler rather than harder. **Decide this
  question inside the configuration design, not before it.**

One thing that would flip it immediately: discovering that the profile cannot
be moved between machines cleanly. The stored password is decrypted with a key
in a *separate* file (`remmina.pref`), so "build it in the UI and copy it" in
fact means copying the secret and its key together. If that proves unworkable
in practice, reason 2 above — the reason that decided this ADR — is gone.
