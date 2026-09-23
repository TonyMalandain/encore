#!/bin/sh
# Encore — copy what a terminal needs onto the machine being converted.
#
# Runs on the machine holding this repository, NOT on the terminal.
#
#   ./encore-push.sh tony@ubuntu-test
#
# Copies by name, never recursively. The repository root also holds live
# connection profiles and a remmina.pref that git ignores but a recursive
# copy would sweep up — and those two together are the stored password in
# plain text.

set -eu

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
    echo "usage: $0 <user>@<terminal>" >&2
    exit 2
fi

HERE=$(dirname "$0")
cd "$HERE"

FILES="encore-kiosk.sh
encore-kiosk.service
encore-kiosk.target
encore-kiosk.remmina.template
encore-install.sh
encore-uninstall.sh"

for f in $FILES; do
    if [ ! -f "$f" ]; then
        echo "missing: $f" >&2
        exit 1
    fi
done

# shellcheck disable=SC2086
scp $FILES "$TARGET:~/"

echo
echo "Copied to $TARGET:~/"
echo "Next, on that machine:  sudo ~/encore-install.sh"
