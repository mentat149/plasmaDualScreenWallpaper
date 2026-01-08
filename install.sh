#!/usr/bin/env bash

##### USER SETTINGS - CHANGE THESE BEFORE RUNNING #####

# Absolute directory pointing to directory to pull wallpapers from
WALLPAPER_DIR=${HOME}/nextcloud/personalization/wallpapers/Dual

# Time in minutes between switching backgrounds. Set to -1 to disable timer
# When timer is disabled, run the script manually via 'systemctl --user start wallpaper-update.service'
WALLPAPER_TIMER=15

#######################################################

echo "Settings:"
echo "WALLPAPER FOLDER = ${WALLPAPER_DIR}"
echo "WALLPAPER TIMER = ${WALLPAPER_TIMER} minutes"

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
