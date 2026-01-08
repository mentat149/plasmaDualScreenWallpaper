#!/usr/bin/env bash

usage() {
    echo "Usage: source install.sh INPUT_DIR [TIMER]"
    echo ""
    echo "INPUT_DIR     Required: wallpaper directory"
    echo "TIMER         Optional: time between wallpaper changes - default 60"
    echo ""
    echo "Example: source install.sh /home/user/Pictures 30"
}


if [ ! -d "$1" ]; then
    echo "Error: Directory $dir not found"
    echo
    usage
    return 1
fi

WALLPAPER_DIR=$1

if [ -z "$2" ]; then
    WALLPAPER_TIMER=60
else
    WALLPAPER_TIMER=$2
fi

echo "Settings:"
echo "Setting folder to ${WALLPAPER_DIR}"
echo "Timer set to ${WALLPAPER_TIMER} minutes"

INSTALL_DIR="${HOME}/.local/share/dualWallpaper"
SYSTEMD_DIR="${HOME}/.config/systemd/user"

if [ ! -d ${INSTALL_DIR} ]; then
    mkdir -p  ${INSTALL_DIR}
fi
if [ ! -d ${SYSTEMD_DIR} ]; then
    mkdir -p  ${SYSTEMD_DIR}
fi

cp ./dualWallpaper.py ${INSTALL_DIR}

sed "s|{WALLPAPER_DIR}|${WALLPAPER_DIR}|g" wallpaper-update.service > ${SYSTEMD_DIR}/wallpaper-update.service

if [ $WALLPAPER_TIMER -eq -1 ]; then
    systemctl daemon-reload --user
    systemctl start --user wallpaper-update.service
else
    sed "s/{WALLPAPER_TIMER}/${WALLPAPER_TIMER}/g" wallpaper-update.timer > ${SYSTEMD_DIR}/wallpaper-update.timer
    systemctl daemon-reload --user
    systemctl enable --now wallpaper-update.timer --user
fi
