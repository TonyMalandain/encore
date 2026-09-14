#!/bin/sh
export GDK_BACKEND=wayland
export HOME=/var/lib/encore

# Find the first available .remmina profile, if one exists
PROFILE=$(find "$HOME/.local/share/remmina" -maxdepth 1 -name "*.remmina" | head -n 1)

while true; do
    if [ -n "$PROFILE" ] && [ -f "$PROFILE" ]; then
        remmina --enable-fullscreen --disable-toolbar --enable-extra-hardening -c "$PROFILE"
    else
        # Fallback to standard UI if no specific profile is loaded yet
        remmina -k
    fi
    sleep 2
done

