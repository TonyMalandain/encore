#!/bin/sh
# Encore — give the machine back.
#
# Runs as root ON THE TERMINAL:
#
#   sudo ~/encore-uninstall.sh
#
# Removes everything this product put on the machine: the units, the runner,
# the system user, and with it the connection profile, the stored password and
# the key that decrypts it. Packages installed at setup are NOT removed — they
# are ordinary software the machine may want for other reasons, and removing
# them is the one step that could break something unrelated.
#
# This is what R-11 promises and what Test 4 checks.

set -eu

die() { echo "error: $*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run as root (sudo $0)"

CONF=/var/lib/encore/encore-install.conf

# What should this machine turn back into? Three sources, in order of how much
# they deserve to be trusted: what the installer wrote down at the time, what
# the operator picks from the targets this machine actually has, or nothing.
# Never a guess, and never an environment variable — an uninstall can happen
# years and several administrators after the install.
restore_target() {
    if [ -r "$CONF" ]; then
        RECORDED=$(sed -n 's/^PREVIOUS_DEFAULT_TARGET=//p' "$CONF" | head -n1)
        if [ -n "$RECORDED" ] && [ "$RECORDED" != "encore-kiosk.target" ] &&
           systemctl cat "$RECORDED" >/dev/null 2>&1; then
            echo "$RECORDED"
            return 0
        fi
    fi
    return 1
}

choose_target() {
    echo "No usable record of what this machine booted into before." >&2
    echo "Targets on this machine that can be booted into:" >&2
    # Deliberately NOT every isolatable target. A machine has two dozen of
    # them, and most — poweroff, halt, reboot, emergency, rescue — would be a
    # disaster as a permanent default. Only the two a machine can sensibly
    # live in are offered.
    i=0
    CHOICES=""
    for t in graphical.target multi-user.target; do
        systemctl cat "$t" >/dev/null 2>&1 || continue
        [ "$(systemctl show -p AllowIsolate --value "$t" 2>/dev/null)" = "yes" ] || continue
        i=$((i + 1))
        CHOICES="$CHOICES $t"
        case "$t" in
            graphical.target)  WHAT="a desktop with a login screen" ;;
            multi-user.target) WHAT="text console only, no desktop" ;;
        esac
        printf '  %d) %-20s %s\n' "$i" "$t" "$WHAT" >&2
    done
    [ "$i" -gt 0 ] || return 1
    printf 'Which one? [1-%d, or blank to leave the default alone] ' "$i" >&2
    read -r PICK
    [ -n "$PICK" ] || return 1
    echo "$CHOICES" | tr ' ' '\n' | sed -n "$((PICK + 1))p"
}

echo "This removes the encore user, its home directory, the stored password"
echo "and the key that protects it. It cannot be undone."
printf 'Continue? [y/N] '
read -r ANSWER
case "$ANSWER" in
    y|Y|yes|YES) ;;
    *) echo "nothing done"; exit 0 ;;
esac

# --- stop it being the machine's default ------------------------------------

REBOOT_NEEDED=no
CURRENT=$(systemctl get-default 2>/dev/null || echo "")
if [ "$CURRENT" = "encore-kiosk.target" ]; then
    if TARGET=$(restore_target); then
        echo "==> restoring the default target recorded at install: $TARGET"
    elif TARGET=$(choose_target) && [ -n "$TARGET" ]; then
        echo "==> restoring $TARGET"
    else
        TARGET=""
        echo "WARNING: the default target is still encore-kiosk.target." >&2
        echo "         Set it yourself before rebooting, or this machine" >&2
        echo "         comes back up trying to be a terminal:" >&2
        echo "           systemctl set-default <target>" >&2
    fi
    if [ -n "$TARGET" ]; then
        systemctl set-default "$TARGET" >/dev/null
        REBOOT_NEEDED=yes
    fi
fi

# --- stop and forget the units ----------------------------------------------

echo "==> units"
systemctl stop encore-kiosk.service 2>/dev/null || true
systemctl disable --quiet encore-kiosk.service 2>/dev/null || true
rm -f /etc/systemd/system/encore-kiosk.service \
      /etc/systemd/system/encore-kiosk.target
rm -f /usr/local/bin/encore-kiosk.sh
systemctl daemon-reload

# --- the user, and everything it owned --------------------------------------

echo "==> user and credentials"
if id encore >/dev/null 2>&1; then
    userdel -r encore 2>/dev/null || die "could not remove the encore user"
else
    echo "    no encore user, nothing to remove"
fi
rm -rf /var/lib/encore

# --- say what is left, honestly ---------------------------------------------

# Three of these names differ by family, so the list has to be worked out on the
# machine it is printed on. Printed from one family's names everywhere, it hands
# a Fedora reader two packages that do not exist (`remmina-plugin-rdp`,
# `pipewire-pulse`) and hides one that does (`openh264`) — and this list exists
# precisely so somebody can clean up by hand, which is the one use that a wrong
# name defeats.
#
# Asked as a capability, never as a distribution name, and apt first: D-036, and
# the same order as the installer's family block, so an ambiguous machine is
# told the same story at both ends.
#
# Detected here rather than read back from $CONF, which records nothing about
# the family: a machine's package manager does not change between install and
# uninstall, so there is no later-is-wronger risk to trade away.
#
# `encore-install.sh` is the authority on these names — it is what installed
# them. A disagreement between that file's family block and this list is a
# defect in this list.
#
# Nothing here removes anything. R-11 leaves every package on the machine, and
# this is a message.
#
# >>> leftovers block — exercised off-target by docs/tests.md test 14a
if command -v apt-get >/dev/null 2>&1; then
    LEFT_PACKAGES="remmina remmina-plugin-rdp cage kbd pipewire pipewire-pulse wireplumber"
    LEFT_UNNAMED=
elif command -v dnf >/dev/null 2>&1; then
    LEFT_PACKAGES="remmina remmina-plugins-rdp cage kbd pipewire pipewire-pulseaudio wireplumber openh264"
    LEFT_UNNAMED=
else
    # Neither package manager answers, so this machine cannot be installed by
    # this product today (the installer dies on R-1) — but an uninstall can run
    # years later on a machine that has changed. Say the five names that are the
    # same in both families, and say out loud that the rest are not being
    # guessed. A plausible wrong name is worse than an admitted gap.
    LEFT_PACKAGES="remmina cage kbd pipewire wireplumber"
    LEFT_UNNAMED="the RDP plugin, the PulseAudio shim and any H.264 decoder"
fi
# <<< leftovers block

# Wrapped to 72 columns, which leaves a margin inside the narrowest screen the
# product mentions: README.md sends somebody whose terminal will not start to a
# text console on Ctrl+Alt+F1..F6, and that console is 80. **A package name
# broken across a line wrap is as useless to copy as a package name that does
# not exist**, which is the whole point of getting these names right.
#
# Computed, never hand-placed. The list is built above and grew by one name on
# 2026-10-05; a break written into a string here would have been in the wrong
# place that day and would be again on the ninth name. So the width is a number
# and the break is wherever the next name no longer fits — asserted, not
# trusted, by docs/tests.md test 14a check 7.
WRAP=72
echo
echo "Removed. Still on this machine, deliberately:"
echo "  ordinary packages, which the machine may want for other reasons:"
LINE=
for p in $LEFT_PACKAGES; do
    if [ -z "$LINE" ]; then
        LINE="    $p,"
        continue
    fi
    CAND="$LINE $p,"
    if [ "${#CAND}" -le "$WRAP" ]; then
        LINE="$CAND"
    else
        echo "$LINE"
        LINE="    $p,"
    fi
done
# Every arm above sets at least five names, so there is always a part-filled
# last line to flush. It ends the list, so it loses its trailing comma.
echo "${LINE%,}"
if [ -n "$LEFT_UNNAMED" ]; then
    echo "  and $LEFT_UNNAMED,"
    echo "  which each package manager names differently. This machine has"
    echo "  neither apt-get nor dnf, so they are not named here rather than"
    echo "  guessed: a plausible wrong name is worse than an admitted gap."
fi
echo "  the copied files in your home directory (encore-*.sh, *.service, …)"
echo

LEFT=0
for p in /etc/systemd/system/encore-kiosk.service \
         /etc/systemd/system/encore-kiosk.target \
         /usr/local/bin/encore-kiosk.sh /var/lib/encore; do
    if [ -e "$p" ]; then echo "STILL PRESENT: $p"; LEFT=1; fi
done
if id encore >/dev/null 2>&1; then
    echo "STILL PRESENT: the encore user"
    LEFT=1
fi
[ "$LEFT" -eq 0 ] && echo "Nothing of Encore's remains."

if [ "$REBOOT_NEEDED" = yes ]; then
    echo
    echo "Reboot to come back up as an ordinary machine."
fi
