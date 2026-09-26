# ADR-0009 — The installer tells the runner where to connect; the profile never does

- **Date:** 2026-09-23
- **Kind:** reversible (one key pair added to a file that already exists; see
  *Consequences* for the one part that is not)

## Context

ADR-0008 gives the runner a pre-flight that connects to the target before the
client is launched. A pre-flight has to know **where** to connect, and nothing
in the design says where that comes from.

R-5 lets an adopter point a terminal at their own machine, and permits them to
name a port. Today that address lives in exactly one place: `server=` inside
the connection profile (`encore-kiosk.remmina.template:37`, filled in by
`encore-install.sh:121`), where a port is written into the same string as the
host.

`boundaries.md` part 4 says the runner **must not know** the host, the username
or the password — it finds a profile by glob (`encore-kiosk.sh:6`) and never
reads its contents. That separation is what lets one set of shipped files serve
every household: everything that differs between terminals is written by the
installer (boundary 5) and nothing else has to understand it.

So the pre-flight needs a fact that today only the profile holds, and the
runner is the one part forbidden to read the profile.

## Options

**A — the runner reads the host and port out of the profile, and nothing else.**
Forever cost: the runner acquires a parser for a file format we do not own.
Remmina's profile is I-6's neighbour and D-024 commits us to whatever the
current release does with it; `server=host:port` also has to be split, and
splitting on `:` is ambiguous for an IPv6 literal — the plan for the probe
refuses to do that for exactly this reason. Worse, "only the host" is a rule
that cannot be enforced: once the runner can open that file, the next change
that wants the username is one line away, and the profile is where the password
lives.

**B — the installer writes the host and port where the runner may read them.**
Forever cost: the address is recorded in two places and can drift if a human
edits one of them. One more key pair on a file that must keep working on
machines converted years earlier.

**C — restate the boundary and let the runner read the profile freely.**
Forever cost: boundary 4 stops being a boundary. The runner becomes a second
part that knows everything about one terminal, which is the property that made
the installer the file with the most knowledge in the product and the one we
have been careful not to duplicate.

## Decision

**Option B. `encore-install.sh` splits the address once, while a person is
present, and records it as two keys in the install record it already writes.
The runner reads those two keys and passes them to the probe. The runner still
never opens the profile.**

The deciding reason is that the split has to happen *somewhere*, and the
installer is the only place where it is safe: it holds the host and port as
separate facts before it ever composes `server=`, and if the address is
malformed it can say so to the administrator standing there, at the moment they
typed it. Every other option performs the same split later, in a component with
nobody watching, against a format we do not own.

The mechanism is **not a new interface.** `/var/lib/encore/encore-install.conf`
(I-7) already exists, is already written by the installer and read by another
component, is already root-owned and mode 644 so the `encore` identity may read
it and may not write it, and I-7 already permits keys to be added. It gains
`RDP_HOST=` and `RDP_PORT=`, the port always written explicitly — `3389` when
the administrator named none — so that no reader ever has to supply a default.

**The boundary does move, and it is restated rather than quietly widened.**
Boundary 4's "must not know the host" becomes:

> The runner may know **where** to connect. It must not know **who** connects
> — no username, no password — and it must never read the profile.

That is the line that was actually load-bearing. The profile is where the
credential is; the address is not a secret and is visible in any packet
capture. Nothing about "one set of shipped files serves every household"
depends on the runner being ignorant of a hostname: it depends on the runner
containing no per-terminal value of its own, and reading two keys out of a file
the installer wrote keeps that intact.

**Decided, not built.** Nothing here exists yet; the installer writes neither
key today and the runner has no pre-flight. It belongs to the runner ticket.

## Consequences

Easier: the runner ticket can be designed — it was blocked on this. The probe
needs no change at all: its `--port` option and its refusal to split on `:`
were already right, and it stays credential-free and profile-free. An
administrator debugging over SSH can read the address the terminal is actually
using without decrypting anything.

Harder: the address exists twice on a converted machine. The installer must
write both from the same input in one step, and re-running the install — which
D-029 already makes the way back from a certificate change — must rewrite both.
A human who hand-edits the profile afterwards gets a terminal that probes one
address and connects to another; nothing detects that. Recorded as debt.

The uninstaller must keep tolerating both keys being absent, because machines
converted before this exists will not have them. That is I-7's existing
failure behaviour and it must not regress.

No longer possible: treating the runner as a component with no knowledge of the
target at all. That property is spent here, once, deliberately, and the
replacement rule is the one written above.

## Revisit when

The runner needs a *third* fact about the terminal that only the profile holds.
That would mean the install record is turning into a second copy of the
profile, and the right answer then is to ask why the profile is the primary
record at all — not to add a fourth key.
