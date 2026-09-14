# The problem

Children in a household need access to a computer. The obvious answer is to
buy each of them one, which costs real money and adds machines that need
maintaining, patching and eventually replacing. Meanwhile there are old
computers sitting in a cupboard that are far too slow to be pleasant on their
own, and one machine in the house that is powerful enough to carry everybody
at once. The hardware to solve this already exists in the house. What is
missing is a way to join the two ends together.

The pieces to do it are all free and all present on an ordinary Linux system —
a remote desktop client, a way to launch it at boot, a way to keep it running.
Assembling them by hand is the actual problem. It is an afternoon of
fiddling with startup behaviour and display sessions, it has to be repeated
for every machine, and it produces something only the person who built it
understands. This is the author's own experience and is the evidence behind
this document; there are no other users yet.

The result of that hand-assembly is also fragile in a way that matters
specifically because the people using it are children. A **person at the
terminal** who is shown a desktop, a settings panel, or an error dialog will
click on it. If the machine ever drops back to its own local desktop — after a
reboot, after the connection dies, after any hiccup — then it has stopped
being a terminal and quietly become an unmanaged computer in a child's room.
A half-converted machine is worse than an unconverted one, because the
household believes it is under control.

The **terminal administrator** carries the other half of this. Converting a
machine is a commitment: if turning the capability on cannot be undone
cleanly, then every old computer is a one-way bet, and the sensible move is
not to try at all. They also need to keep the off-switch away from the person
at the terminal — a child who can turn the kiosk off has simply been given an
unsupervised computer by another route. And once the capability is on, the
screen belongs to the remote session, so the administrator has to be able to
reach the machine some other way.

What that machine can reach is the other half of the commitment, and it is the
part nobody thinks about until it is too late. A terminal sits unattended in a
child's room, powered on, on the household network, and it needs a stored
secret to open its connection at all. Anything it is allowed to touch beyond
the screen, the keyboard, the sound and the one machine it was pointed at is
something the household has quietly agreed to without being asked. An
administrator deciding whether to convert a machine is really deciding what
that machine is permitted to do while nobody is watching it.

There is a smaller pain that is easy to miss and lands on the **owner of the
machine being connected to**. A terminal with no sound is half a computer, and
audio that comes out on the wrong machine puts a child's noise into an adult's
room. Sound has to work in both directions for a call to be possible at all,
and it has to work without anyone setting it up, because audio configured
machine by machine is audio that ends up missing on one of them. This person asked for nothing and gets nothing from the product
directly; they are simply expected to absorb whatever the terminals do. It is
assumed, not observed, that this would become an irritation quickly.

Finally, none of this is worth writing down carefully if it only ever works in
one house. A **prospective adopter** finding this project has the same
cupboard of old machines and the same afternoon of fiddling ahead of them.
They will decide whether to spend an evening on it by reading, before they
install anything — so being understandable from the outside is not decoration,
it is the difference between the project being usable by anyone else and not.

The problem is solved when someone other than the author can take an old
machine, turn it into a terminal that a child can use unattended, and turn it
back again — without needing to understand how any of it works.
