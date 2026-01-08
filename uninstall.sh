#!/usr/bin/env bash

INSTALL_DIR="${HOME}/.local/share/dualWallpaper"
SYSTEMD_DIR="${HOME}/.config/systemd/user"



if [ -f ${SYSTEMD_DIR}/wallpaper-update.service ]; then
    echo "Deleting file ${SYSTEMD_DIR}/wallpaper-update.service"
    rm ${SYSTEMD_DIR}/wallpaper-update.service
fi

if [ -f ${SYSTEMD_DIR}/wallpaper-update.timer ]; then
    echo "Deleting file ${SYSTEMD_DIR}/wallpaper-update.timer"
    systemctl --user disable --now wallpaper-update.timer
    rm ${SYSTEMD_DIR}/wallpaper-update.timer
fi

if [ -d ${INSTALL_DIR} ]; then
    echo "Deleting directory ${INSTALL_DIR}"
    rm -r ${INSTALL_DIR}
fi
