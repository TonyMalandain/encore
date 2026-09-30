#!/bin/sh
export GDK_BACKEND=wayland
export HOME=/var/lib/encore

# Every line this file writes about sound starts with one of exactly two
# prefixes, and nothing else in the system writes either:
#
#   encore: sound: <what happened>
#   encore: SOUND UNAVAILABLE: <why there is no sound, in one line>
#
# There is no path out of start_sound that writes neither, which is what makes
#   journalctl -t encore-kiosk -b | grep 'SOUND UNAVAILABLE'
# a complete answer rather than a hopeful one. It is `-t` and not `-u` because
# PAMName=login moves these processes out of the unit's cgroup; see the comment
# beside SyslogIdentifier in encore-kiosk.service.
HELPER_PIDS=

log() { printf 'encore: %s\n' "$*" >&2; }

stop_helpers() {
    [ -n "$HELPER_PIDS" ] || return 0
    # Deliberately unquoted: HELPER_PIDS is a space-separated list of PIDs.
    kill $HELPER_PIDS 2>/dev/null || true
    HELPER_PIDS=
}

# Wait up to $2 seconds for the path $1 to exist. Returns 1 on timeout.
wait_for() {
    _waited=0
    while [ ! -e "$1" ]; do
        [ "$_waited" -lt "$2" ] || return 1
        sleep 1
        _waited=$((_waited + 1))
    done
    return 0
}

# The sound server is started here, inside the kiosk's own PAM session, rather
# than as a system unit beside it. /run/user/<uid> exists only while a session
# for this identity exists, and this unit restarts whenever a connection drops
# (R-18, D-020, D-026) — so a sibling unit would race the runtime directory on
# every reconnect. Started here, the helpers start with the session, die with
# it, and share its cgroup.
#
# `wireplumber -p main-embedded` is the upstream profile for running with no
# session bus and no login-session integration. That is the whole point: the
# alternative — letting the session class be lifted so the machine starts sound
# for us — also starts a session bus, a keyring, a file broker and a package
# prompt that can draw on the screen, which R-16, D-012 and R-6 exclude. See
# BACKLOG.md item 5 and D-034.
#
# start_sound ALWAYS returns 0. A terminal with no sound is a terminal; a
# terminal that will not connect is not (R-6 and R-8 over R-12).
start_sound() {
    if [ -z "${XDG_RUNTIME_DIR:-}" ]; then
        log "SOUND UNAVAILABLE: XDG_RUNTIME_DIR is not set, so there is nowhere for the sound server to put its socket"
        return 0
    fi

    # On a machine where this fault does not exist, something already runs a
    # sound server for this identity. Starting a second one beside a working
    # one is the one way this change could break a machine that was fine.
    if [ -e "$XDG_RUNTIME_DIR/pulse/native" ]; then
        log "sound: a PulseAudio-protocol socket already exists; leaving it alone"
        return 0
    fi

    for _bin in /usr/bin/pipewire /usr/bin/pipewire-pulse /usr/bin/wireplumber; do
        if [ ! -x "$_bin" ]; then
            log "SOUND UNAVAILABLE: $_bin is missing — install pipewire, pipewire-pulse and wireplumber"
            return 0
        fi
    done

    # "Compiled with libwireplumber 0.5.13" -> "0.5.13". Profiles arrived in
    # 0.5; there is no -p flag at all in 0.4, so the process would exit at once
    # with an unknown-option error and nothing would say why. Refusing on a
    # version we cannot read is the safe direction: the cost is a terminal with
    # no sound and a loud line, rather than three processes failing silently.
    _wp=$(wireplumber --version 2>/dev/null | sed -n 's/^Compiled with libwireplumber //p' | head -n1)
    _wp_major=${_wp%%.*}
    _wp_rest=${_wp#*.}
    _wp_minor=${_wp_rest%%.*}
    if [ -z "$_wp" ] ||
       [ -z "$_wp_major" ] || [ -n "$(printf '%s' "$_wp_major" | tr -d '0-9')" ] ||
       [ -z "$_wp_minor" ] || [ -n "$(printf '%s' "$_wp_minor" | tr -d '0-9')" ]; then
        log "SOUND UNAVAILABLE: could not read wireplumber's version (it said '$_wp'); 0.5 or newer is needed"
        return 0
    fi
    if [ "$_wp_major" -eq 0 ] && [ "$_wp_minor" -lt 5 ]; then
        log "SOUND UNAVAILABLE: wireplumber $_wp is too old — 'wireplumber -p main-embedded' needs 0.5 or newer"
        return 0
    fi

    # </dev/null because the unit sets StandardInput=tty for libseat, and a
    # helper that inherits that tty can be stopped by SIGTTIN. Output goes to
    # stderr, which is the journal: a log file would outlive the uninstaller
    # (R-11).
    /usr/bin/pipewire </dev/null >&2 2>&1 &
    HELPER_PIDS="$HELPER_PIDS $!"

    # Five seconds is a guess, not a measurement, and it is bounded on purpose:
    # this delay is a black screen in front of a child.
    if ! wait_for "$XDG_RUNTIME_DIR/pipewire-0" 5; then
        log "SOUND UNAVAILABLE: pipewire did not create $XDG_RUNTIME_DIR/pipewire-0 within 5 seconds"
        stop_helpers
        return 0
    fi

    /usr/bin/pipewire-pulse </dev/null >&2 2>&1 &
    HELPER_PIDS="$HELPER_PIDS $!"
    /usr/bin/wireplumber -p main-embedded </dev/null >&2 2>&1 &
    HELPER_PIDS="$HELPER_PIDS $!"

    if ! wait_for "$XDG_RUNTIME_DIR/pulse/native" 5; then
        # The helpers are left running: their own output is already in the
        # journal above, and it is the evidence for why this failed.
        log "SOUND UNAVAILABLE: no PulseAudio-protocol socket at $XDG_RUNTIME_DIR/pulse/native within 5 seconds of starting the sound server"
        return 0
    fi

    log "sound: server ready at $XDG_RUNTIME_DIR/pulse/native"

    # Best effort, and nothing branches on it: this is the line that will
    # diagnose old hardware with no usable output device (D-009's accepted
    # cost). Zero sinks is a terminal with no sound, so it is reported as one.
    if command -v pw-dump >/dev/null 2>&1; then
        _sinks=$(pw-dump 2>/dev/null | grep -c '"Audio/Sink"' || true)
        if [ "${_sinks:-0}" -eq 0 ]; then
            log "SOUND UNAVAILABLE: the sound server is running but has no output device"
        else
            log "sound: $_sinks output device(s) present"
        fi
    else
        log "sound: pw-dump is not installed, so the number of output devices was not counted"
    fi

    return 0
}

# Belt and braces, not the mechanism: the helpers live in the unit's cgroup, so
# systemd tears them down on stop and on every restart without being asked.
# This stops a runner that exits on its own leaving three processes behind for
# the seconds before systemd notices.
trap stop_helpers INT TERM EXIT

# Once, before the loop: the helpers are long-lived and must not be restarted
# per iteration.
start_sound

# Find the first available .remmina profile, if one exists
PROFILE=$(find "$HOME/.local/share/remmina" -maxdepth 1 -name "*.remmina" | head -n 1)

while true; do
    if [ -n "$PROFILE" ] && [ -f "$PROFILE" ]; then
        # stdbuf because output to a pipe is fully buffered and is then lost
        # when the process is killed, which is why the client's own diagnosis
        # of a failed connection has never reached the journal.
        stdbuf -oL -eL remmina --enable-fullscreen --disable-toolbar --enable-extra-hardening -c "$PROFILE"
    else
        # Fallback to standard UI if no specific profile is loaded yet
        stdbuf -oL -eL remmina -k
    fi
    sleep 2
done
