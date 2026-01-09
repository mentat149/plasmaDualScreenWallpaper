#!/usr/bin/env bash

INSTALL_DIR="${HOME}/.local/share/dualWallpaper"
SYSTEMD_DIR="${HOME}/.config/systemd/user"

remove_file() {
    if [ -f $1 ]; then
        echo "Deleting file $1"
        rm $1
    fi
}

if [ -f ${SYSTEMD_DIR}/wallpaper-update.timer ]; then
    systemctl --user disable --now wallpaper-update.timer
fi

remove_file ${SYSTEMD_DIR}/wallpaper-update.service
remove_file ${SYSTEMD_DIR}/wallpaper-update.timer

if [ -d ${INSTALL_DIR} ]; then
    echo "Deleting directory ${INSTALL_DIR}"
    rm -r ${INSTALL_DIR}
fi
