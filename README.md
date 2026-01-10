# plasmaDualScreenWallpaper
A simple Python script to create a slideshow from multi-screen wallpapers that span across multiple monitors


I only have 2 monitors side-by-side to test with, but it should work with more. The script looks at the total virtual desktop size, blows up the image to match, with a center crop if needed, and cuts the image based on the position of each monitor.

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

The image can be changed manually at any time by running  
```
systemctl start wallpaper-update.service --user
```

## Uninstall

Just run ```source uninstall.sh``` to remove created files.

## Single Image

If you don't want a slideshow and just want to set a single wallpaper, either set the timer to -1, or run the python script and point it to any image:  
```
python wallpaper.py /path/to/image.jpg
```

