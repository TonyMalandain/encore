# Why not use something that already exists

A stranger's first fair question is why this exists at all, when turning old
computers into thin clients is a solved problem with several mature answers.
Answering it honestly is part of what R-13 asks for, so the answer lives here
rather than being left for each reader to work out.

The short version: the existing answers are built for a different size of
problem, and every one of them asks for the machine itself. This project asks
for an evening and gives the machine back.

## The fleet platforms

The established way to run thin clients is a platform that takes over the
whole arrangement: a central server holds one image of what a terminal should
be, and the terminals fetch it when they start. That is genuinely better once
there are enough terminals, because changing them all means changing one
thing.

It is the wrong shape here for one reason, which is D-016: this product is
built for two or three machines in one household. Adopting a fleet platform
means standing up and maintaining the infrastructure the terminals boot from,
and in practice learning an unfamiliar system to do it. At three machines that
is more work than the afternoon of hand-assembly the project exists to
replace, and it is work that never ends.

**The honest counterweight, which should not be argued away:** a fleet
platform would have supplied central configuration — one place to change every
terminal — for nothing. That is exactly the largest hole in this product, and
D-016 names it as an accepted cost. This project is not avoiding that work. It
is choosing to do a small, local version of it, and betting that the small
version stays small.

## The purpose-built distributions and images

Several projects ship a whole operating system, or an image written to the
machine, that turns it into a terminal. They work, and for someone standing up
a room full of identical machines they are the sensible choice.

They are ruled out by the promise this product is built around: the old
machine keeps being itself, and switching the capability off gives it back
(R-11, D-007). An image cannot offer "give me my machine back", because there
is no machine left to give back. A household deciding whether to convert the
old laptop in the cupboard is deciding whether that laptop survives the
experiment, and every answer that reimages it turns the decision into a
one-way bet — which the problem statement says is the reason people sensibly
decline to try.

## The remote desktop client's own kiosk mode

The closest existing thing is a kiosk mode shipped by the remote desktop
client this product already relies on. It was the best candidate, and it was
checked properly rather than dismissed.

It is ruled out on the display stack: it is built for the older of the two
display technologies in the Linux world, and D-003 fixes this product on the
newer one. That is a hard incompatibility, not a preference, so its health as
a project does not enter into it. The client underneath it — the part this
product actually depends on — was checked separately and is actively
maintained.

## What this list is not

It is not a claim that this product is better than any of them. It is a claim
that it is smaller, and that smallness is the point: three machines, one
household, one evening, and an undo. Anyone whose situation is bigger than
that should use one of the platforms above, and D-016 says when that moment
arrives.

The named comparison, with versions and verified links, belongs to the
engineering record rather than here, because names and versions age and the
reasoning above does not.
