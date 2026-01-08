#!/usr/bin/env bash

INSTALL_DIR="${HOME}/.local/share/dualWallpaper"
SYSTEMD_DIR="${HOME}/.config/systemd/user"

systemctl --user disable --now wallpaper-update.timer

if [ -f ${SYSTEMD_DIR}/wallpaper-update.service ]; then
    rm ${SYSTEMD_DIR}/wallpaper-update.service
    echo "Deleting file ${SYSTEMD_DIR}/wallpaper-update.service"
fi

if [ -f ${SYSTEMD_DIR}/wallpaper-update.timer ]; then
    rm ${SYSTEMD_DIR}/wallpaper-update.timer
    echo "Deleting file ${SYSTEMD_DIR}/wallpaper-update.timer"
fi

if [ -d ${INSTALL_DIR} ]; then
    rm -r ${INSTALL_DIR}
    echo "Deleting directory ${INSTALL_DIR}"
fi
