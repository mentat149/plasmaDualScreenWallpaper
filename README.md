# plasmaDualScreenWallpaper
A simple Python script to create a slideshow from multi-screen wallpapers that span across multiple monitors

## Install

1. Clone the repo and cd into directory:  
```
git clone https://github.com/mentat149/plasmaDualScreenWallpaper
cd plasmaDualScreenWallpaper
```  

2. Run the installer script:  
```
source install.sh /path/to/wallpapers [timer]
```
Change the path to where you want it to grab the wallpapers from and set time in minutes (default 60).

## Uninstall

Just run ```source uninstall.sh``` to remove created files.

## Single Image

If you don't want a slideshow and just want to set a single wallpaper, just run the python script on its own:  
```
python wallpaper.py /path/to/image.jpg
```
