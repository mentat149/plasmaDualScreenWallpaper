# plasmaDualScreenWallpaper
A simple Python script to create a slideshow from multi-screen wallpapers that span across multiple monitors

## Install

1. Clone the directory:  
```
git clone https://github.com/mentat149/plasmaDualScreenWallpaper
```  
2. Open install.sh and edit the variables at the top.  
WALLPAPER_DIR - point to folder to grab  
WALLPAPER_TIMER - the time between wallpaper update, set to -1 to ignore if you just want to run once.   Can be run manually via  
```
systemctl --user start wallpaper-update.service
```  
3. cd into directory and run install.sh  
```
source install.sh
```  

## Uninstall

Just run ```source uninstall.sh``` to remove created files.
