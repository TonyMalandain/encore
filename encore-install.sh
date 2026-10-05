#!/bin/sh
# Encore — convert this machine into a kiosk terminal.
#
# Runs as root ON THE TERMINAL, from the directory the files were copied to:
#
#   sudo ~/encore-install.sh
#
# Prompts for the target machine, the connection account and its password.
# The password is read without echo and never appears in shell history.
# It does NOT switch the terminal on — that is a separate, deliberate step
# printed at the end.

set -eu

die() { echo "error: $*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run as root (sudo $0)"

HERE=$(cd "$(dirname "$0")" && pwd)
for f in encore-kiosk.sh encore-kiosk.service encore-kiosk.target \
         encore-kiosk.remmina.template; do
    [ -f "$HERE/$f" ] || die "missing $f in $HERE — run encore-push.sh first"
done

# --- which package manager this machine has ---------------------------------

# Asked as a capability, never as a distribution name (D-036): what this
# machine can do, not what it calls itself. A list of distribution names has to
# be extended for every derivative and is silent when it is short — which is
# exactly how D-A19 happened, one file over.
#
# apt is checked first, so a machine carrying both wins for apt: R-1 is `real`
# for apt and `intended` for dnf, and the ambiguous machine should get the
# family this product has actually been watched working on. Fedora packages
# `apt` and Debian packages `dnf`, so both directions are real.
#
# TWO places in this file branch on the family: this block, which holds every
# family-dependent *name*, and the packages step, which holds the two commands.
# A third is a defect — add a variable here instead.
#
# >>> family block — exercised off-target by docs/tests.md test 14a
if command -v apt-get >/dev/null 2>&1; then
    PKG_FAMILY=apt
    RDP_PLUGIN=remmina-plugin-rdp
    PULSE_SHIM=pipewire-pulse
    SSH_UNIT=ssh
    SSH_INSTALL="apt install openssh-server"
    # Empty on purpose — Debian and Ubuntu ship the real libopenh264 in main
    # and have no stub beside it. See the dnf side for what this is for.
    H264_DECODER=
elif command -v dnf >/dev/null 2>&1; then
    # `dnf`, not `dnf5`: `dnf` exists across the whole family and is a symlink
    # to dnf5 where dnf5 is what the machine has (Fedora 44, 2026-10-04).
    PKG_FAMILY=dnf
    RDP_PLUGIN=remmina-plugins-rdp
    PULSE_SHIM=pipewire-pulseaudio
    SSH_UNIT=sshd
    SSH_INSTALL="dnf install openssh-server"
    # NOT REDUNDANT, AND NOT A TIDY-UP CANDIDATE. `libfreerdp3` has
    # `NEEDED libopenh264.so.8`, so rpm requires it automatically and the
    # install is always clean — but on a fresh Fedora dnf satisfies that
    # requirement from Fedora's own repositories with `noopenh264`, which is a
    # **stub that provides the library and decodes nothing**. The link
    # resolves, nothing fails, and the session is unusable: a stub that
    # satisfies the dependency and silently does not work. Naming the real
    # package swaps the stub out — `openh264` carries
    # `Obsoletes: noopenh264 < 1:0`, so no --allowerasing is needed — and it
    # comes from `fedora-cisco-openh264`, enabled by default, so this adds no
    # third-party repository. Measured on Fedora 44, 2026-10-05.
    #
    # This makes **software** decoding work. The client is built
    # `WITH_VAAPI=OFF` and links no libva; nothing here is hardware
    # acceleration (D-037's withdrawal).
    H264_DECODER=openh264
else
    die "no supported package manager found: this needs apt-get or dnf (R-1)"
fi

# Each name appears once. Seven are wanted by both families — two of those
# differ by family name, five are identical, measured on Fedora 44 on
# 2026-10-04 and recorded in docs/architecture/stack.md. $H264_DECODER is the
# first one only *one* family needs, and it is still a variable in this one
# list rather than a second list or a branch further down, so that adding a
# package and forgetting a branch stays impossible. It is empty on apt, and an
# empty variable inside this unquoted expansion splits to nothing at all
# rather than to an empty argument — watched, test 14a check 3.
PACKAGES="remmina $RDP_PLUGIN cage kbd pipewire $PULSE_SHIM wireplumber $H264_DECODER"
# <<< family block

# Said out loud, before anything is installed: on a machine carrying both
# package managers the choice above is a guess, and this is the line that makes
# it a visible guess rather than a confusing failure three steps later.
echo "==> package manager: $PKG_FAMILY"

HOME_DIR=/var/lib/encore
PROFILE="$HOME_DIR/.local/share/remmina/encore-kiosk.remmina"
PREF="$HOME_DIR/.config/remmina/remmina.pref"
CONF="$HOME_DIR/encore-install.conf"

# When this run began, in the form journalctl --since understands. The only
# journal entries that can mention our password are ones this run produced,
# so every check below reads from here forward instead of the whole journal.
STARTED=$(date '+%Y-%m-%d %H:%M:%S')

# What this machine was before we touched it. Captured now, before anything
# changes, and written down so the uninstaller can put it back years later
# without anyone having to remember.
PREVIOUS_DEFAULT=$(systemctl get-default 2>/dev/null || echo "")

# --- your way back in -------------------------------------------------------

# Once the capability is on, the screen belongs to the remote session: no
# desktop, no terminal window, no menu. If something then goes wrong, SSH is
# how anyone gets in to look. A text console still exists, but it means being
# at the machine and knowing to reach for it.
if ! systemctl is-active --quiet ssh 2>/dev/null &&
   ! systemctl is-active --quiet sshd 2>/dev/null; then
    echo
    echo "Note: no SSH server is running. After conversion the screen shows"
    echo "only the remote session, so a text console (Ctrl+Alt+F1..F6) is"
    echo "your way in. SSH is easier:"
    echo
    echo "    $SSH_INSTALL && systemctl enable --now $SSH_UNIT"
    echo
fi

# --- what this terminal connects to ----------------------------------------

printf 'Machine to connect to (hostname or IP): '
read -r RDP_SERVER
[ -n "$RDP_SERVER" ] || die "no machine given"

printf 'Connection account on that machine: '
read -r RDP_USER
[ -n "$RDP_USER" ] || die "no account given"

stty -echo 2>/dev/null || true
printf 'Password for %s (not echoed): ' "$RDP_USER"
read -r RDP_PASS
stty echo 2>/dev/null || true
printf '\n'
[ -n "$RDP_PASS" ] || die "no password given"

# --- 1. packages ------------------------------------------------------------

echo "==> packages"
# The sound server the runner starts for itself inside the kiosk session —
# the pipewire, PulseAudio-shim and wireplumber entries in $PACKAGES. A
# minimal install may not carry them, and without them the terminal is
# silent.
#
# Two commands, not one with a variable in it, so that what runs as root
# on somebody's machine reads as a command. $PACKAGES is unquoted on
# purpose: the word splitting is how a list of names becomes that many
# arguments — seven on apt, eight on dnf, which carries $H264_DECODER.
#
# There is no `dnf` line matching `apt-get update`, and adding one would
# be a mistake: `apt-get install` does not refresh and fails outright on a
# stale list, while dnf refreshes expired metadata as part of `install`.
# A `dnf makecache` would buy nothing and add a network step that can fail
# on its own — one unreachable optional repository would abort, under
# `set -e`, a conversion that `dnf install` would have completed.
case "$PKG_FAMILY" in
    apt) apt-get update -qq
         apt-get install -y -qq $PACKAGES ;;
    dnf) dnf install -y -q $PACKAGES ;;
esac

# --- 2. the user the terminal runs as ---------------------------------------

echo "==> user"
if id encore >/dev/null 2>&1; then
    echo "    encore already exists, leaving it alone"
else
    useradd --system --create-home --home-dir "$HOME_DIR" \
            --shell /usr/sbin/nologin encore
fi
usermod -aG video,input,render encore

# --- 3. directories ---------------------------------------------------------

echo "==> directories"
# install -d applies -o, -g and -m to the LAST component only: the ancestors it
# creates on the way are root-owned and 0755. So every level inside the
# identity's own home is created explicitly here, one at a time.
for d in "$HOME_DIR/.local" "$HOME_DIR/.local/share" "$HOME_DIR/.local/state" \
         "$HOME_DIR/.local/share/remmina" \
         "$HOME_DIR/.config" "$HOME_DIR/.config/remmina"; do
    install -d -o encore -g encore -m 700 "$d"
done

# Checked because the failure is silent: a directory the terminal cannot write
# into looks exactly like one it has not needed yet.
for d in "$HOME_DIR/.local" "$HOME_DIR/.local/share" "$HOME_DIR/.local/state" \
         "$HOME_DIR/.config"; do
    [ "$(stat -c %U "$d")" = encore ] || die "$d is owned by $(stat -c %U "$d"), not encore"
done

# What the machine was, recorded where the uninstaller will look for it.
# Root-owned and world-readable: the encore user must never be able to edit
# the note that decides what this machine turns back into.
cat > "$CONF" <<EOF
# Written by encore-install.sh — read by encore-uninstall.sh.
# What this machine booted into before Encore was installed.
PREVIOUS_DEFAULT_TARGET=$PREVIOUS_DEFAULT
INSTALLED_ON=$(date -Is 2>/dev/null || date)
EOF
chown root:root "$CONF"
chmod 644 "$CONF"
echo "    was: ${PREVIOUS_DEFAULT:-unknown}"

# --- 4. the connection profile ----------------------------------------------

echo "==> profile"
install -o encore -g encore -m 600 \
        "$HERE/encore-kiosk.remmina.template" "$PROFILE"

sed -i \
    -e "s|^server=.*|server=$RDP_SERVER|" \
    -e "s|^username=.*|username=$RDP_USER|" \
    "$PROFILE"

if grep -q CHANGEME "$PROFILE"; then
    die "profile still contains CHANGEME — template and script disagree"
fi

# sound=remote is one word from sound=local and sends the session's audio to
# the OTHER machine — a terminal in a child's room playing into an adult's.
# Checked by name, here, because the runner is not allowed to know anything in
# the profile (ADR-0009). Written as `if` blocks, not `grep … && die`: under
# `set -eu` a bare `grep … && die` exits the script when the grep finds
# nothing, which is the success case.
if ! grep -q '^sound=local$' "$PROFILE"; then
    die "profile does not say sound=local — the terminal would be silent (D-009)"
fi
if grep -q '^sound=remote' "$PROFILE"; then
    die "profile says sound=remote — that sends the session's audio to the OTHER machine (D-009 forbids it)"
fi

# Exactly one profile, or the runner picks an unpredictable target.
COUNT=$(find "$HOME_DIR/.local/share/remmina" -maxdepth 1 -name '*.remmina' | wc -l)
[ "$COUNT" -eq 1 ] || die "expected 1 profile, found $COUNT"

# --- 5. the password, and the key that protects it --------------------------

# The keyring plugin must be out of reach while the password is written, or the
# client insists on a secret service that an unattended terminal has nobody to
# unlock. Found, not computed: deriving the path from `uname -m` produced a
# Debian multiarch path on every machine and matched nothing on Fedora, which
# puts the file in /usr/lib64 (D-A19). Asking the machine where the file is
# costs one find and makes no claim about any distribution's layout.
#
# WHERE THIS LINE SITS IS PART OF THE FIX. It must run AFTER the packages step
# and BEFORE the password is written, and it reads as though it belongs 140
# lines up with the other variable assignments — which is where it was first
# put, and that reinstated the whole defect. The path it replaced was a static
# string built from `uname -m`, correct whether or not the file existed, so
# order never mattered; a filesystem query is only truthful once the
# filesystem can answer. On a first conversion the client is not installed
# yet, and the plugin arrives WITH it: `remmina-plugins-secret` is a weak
# dependency of `remmina` on both families and both package managers install
# weak dependencies by default. Searching before the packages step therefore
# finds nothing on exactly the machine this is for, suppresses nothing, and
# dies at "no password stored in the profile". docs/tests.md test 14a check 6
# is the regression check; do not tidy this back up the file.
#
# Each path is prefixed `-` so systemd tolerates one that has gone; empty means
# the plugin really is not installed, so there is nothing to hide. A root that
# does not exist — /usr/lib64 on many apt machines — is find's complaint to
# stderr and nothing more; the surviving root is still searched and the
# pipeline still exits 0, which `set -e` needs.
SECRET_PLUGINS=$(find /usr/lib /usr/lib64 -name 'remmina-plugin-secret.so' \
                 2>/dev/null | sed 's|^|-|' | tr '\n' ' ')

echo "==> password"
systemd-run --quiet --pipe --uid=encore \
    -p "InaccessiblePaths=$SECRET_PLUGINS" \
    -E HOME="$HOME_DIR" \
    remmina --update-profile "$PROFILE" \
            --set-option password="$RDP_PASS" >/dev/null 2>&1 \
    || die "setting the password failed"

RDP_PASS=

grep -q '^secret=' "$PREF" \
    || die "no key in $PREF — the password cannot be decrypted"
grep -q '^password=.\+' "$PROFILE" \
    || die "no password stored in the profile"

# --- 6. the files -----------------------------------------------------------

echo "==> units"
install -m 755 "$HERE/encore-kiosk.sh" /usr/local/bin/encore-kiosk.sh
install -m 644 "$HERE/encore-kiosk.service" "$HERE/encore-kiosk.target" \
        /etc/systemd/system/

# The unit hides the plugin by naming literal paths, and the leading `-` on
# each tells systemd to tolerate a path that is not there. That is what lets
# one unit cover several layouts — and it is also what hid every path being
# wrong on Fedora, in a unit that started perfectly clean (D-A19). So the
# coverage is checked here, on the machine, where it can be asked rather than
# assumed. $SECRET_PLUGINS is unquoted on purpose: the word splitting is the
# mechanism. It is empty when the plugin is not installed, and the loop then
# does nothing, which is correct — there is nothing to hide.
for p in $SECRET_PLUGINS; do
    grep -qF -- "InaccessiblePaths=$p" /etc/systemd/system/encore-kiosk.service ||
        die "encore-kiosk.service does not hide ${p#-} — the terminal would stop at a keyring prompt nobody can answer. Add to the unit: InaccessiblePaths=$p"
done

systemctl daemon-reload
systemctl enable --quiet encore-kiosk.service

# --- what the terminal cannot hide -----------------------------------------

echo
echo "Installed. The terminal is NOT switched on yet."
echo
echo "  Switch on now, until reboot:   systemctl isolate encore-kiosk.target"
echo "  Switch on from every boot:     systemctl set-default encore-kiosk.target && reboot"
echo
echo "  Undo everything:               sudo $HERE/encore-uninstall.sh"
echo

# Said here because this is the only moment a person is standing at the
# machine. The runner decides for itself on every start, so a later backport of
# wireplumber 0.5 turns sound on with nothing to re-run — BACKLOG.md item 5
# forbids freezing the audio stack at install time. This reports; it gates
# nothing.
WP_VERSION=$(wireplumber --version 2>/dev/null \
             | sed -n 's/^Compiled with libwireplumber //p' | head -n1 || true)
WP_MAJOR=${WP_VERSION%%.*}
WP_REST=${WP_VERSION#*.}
WP_MINOR=${WP_REST%%.*}
SOUND_OK=yes
if [ -z "$WP_VERSION" ] ||
   [ -z "$WP_MAJOR" ] || [ -n "$(printf '%s' "$WP_MAJOR" | tr -d '0-9')" ] ||
   [ -z "$WP_MINOR" ] || [ -n "$(printf '%s' "$WP_MINOR" | tr -d '0-9')" ]; then
    SOUND_OK=no
elif [ "$WP_MAJOR" -eq 0 ] && [ "$WP_MINOR" -lt 5 ]; then
    SOUND_OK=no
fi
if [ "$SOUND_OK" = no ]; then
    echo "NOTE: this machine will have no sound."
    echo "      wireplumber here is '${WP_VERSION:-not readable}'; 0.5 or newer is needed."
    echo "      The terminal works and connects exactly as it would otherwise —"
    echo "      it is silent. Install wireplumber 0.5 or newer and restart the"
    echo "      terminal and sound comes on; nothing here has to be re-run."
    echo
fi

# The password reached a command line inside a transient unit. Say so rather
# than pretending the prompt made it private.
if journalctl -S "$STARTED" --no-pager -q 2>/dev/null \
   | grep -q 'set-option password'; then
    echo "WARNING: the password appears in the journal."
    echo "         Rotate it on $RDP_SERVER, or clear the journal."
fi
