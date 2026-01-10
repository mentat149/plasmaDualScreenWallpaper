import os
import sys
import pathlib
import re
import dbus
import json
import shutil
from PIL import Image
import random
import glob

def getRandomPicture( directory ):
    # Find all image files in directory and subdirectories, return random one
    extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff'}
    files = []
    for ext in extensions:
        images = pathlib.Path( directory ).rglob( f'*{ext}' )
        files.extend( images )

    files = [ str(img) for img in files ]
    if not files:
        return None
    return random.choice( files )

def resizeToVirtualCanvas(img, virtual_width, virtual_height):
    # resize image based on size of virtual desktop containing all screens
    # this will center and crop the image if the proportions are different
    orig_w, orig_h = img.size
    print(f"   Original: {orig_w}x{orig_h}")

    # scale image proportionally. one dimension will fix exactly, the other will crop
    scale = max( virtual_width/orig_w, virtual_height/orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    left   = ( new_w - virtual_width )//2
    right  = ( new_w + virtual_width )//2
    top    = ( new_h - virtual_height )//2
    bottom = ( new_h + virtual_height )//2

    final = resized.crop( (left, top, right, bottom) )
    print(f"   Resized to virtual canvas: {virtual_width}x{virtual_height}")
    return final


def getMonitorGeometries():
    """Get desktop-monitor mapping via Plasma DBus."""
    JS_GEOM = """
    var all_desktops = desktops();
    var valid = [];
    for (var i = 0; i < all_desktops.length; i++) {
        var d = all_desktops[i];
        if (d.screen != -1) {
            var sg = screenGeometry(d.screen);
            valid.push({
                desktop_id: i,
                screen: d.screen,
                x: sg.x,
                y: sg.y,
                width: sg.width,
                height: sg.height
            });
        }
    }
    valid.sort((a, b) => a.x - b.x);
    print(JSON.stringify(valid));
    """

    session_bus = dbus.SessionBus()
    plasma = session_bus.get_object("org.kde.plasmashell", "/PlasmaShell")
    iface = dbus.Interface(plasma, dbus_interface="org.kde.PlasmaShell")

    result = iface.evaluateScript(JS_GEOM)
    json_match = re.search(r'\[.*\]', result, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))
    print(f"❌ Failed to parse geometries: {result}")
    return []


def applyWallpaper():
    # Take the blown up image that spans the virtual desktop and for each screen present,
    # create a cropped image of the same size and position.
    # The cropped images are then applied as wallpaper to each screen

    tempdir = str(pathlib.Path.home()) + "/.local/share/dualWallpaper/wallpaperCrops"

    # try to get the name of the previous image used if it exists in the temp directory
    # if same one is randomly selected, it'll choose again
    try:
        oldImage = pathlib.Path(os.listdir(tempdir)[0]).stem.partition('_crop')[0]
    except:
        oldImage = ''

    # delete and recreate temp dir
    if os.path.exists( tempdir ):
        shutil.rmtree( tempdir )
    os.makedirs( tempdir, exist_ok=True )

    # if passed argument is a directory, grab a random image, otherwise use argument as image file
    if os.path.isdir( sys.argv[1] ):
        sourceImage = getRandomPicture( sys.argv[1] )
        while oldImage == pathlib.Path( sourceImage ).stem:
            sourceImage = getRandomPicture( sys.argv[1] )
    elif os.path.isfile( sys.argv[1] ):
        sourceImage = sys.argv[1]

    if not pathlib.Path( sourceImage ).is_file():
        raise FileNotFoundError(f"❌ Source image not found: {sourceImage}")

    print("📊 Detecting monitors...")
    desktopInfo = getMonitorGeometries()
    if not desktopInfo:
        raise RuntimeError("❌ No valid monitors detected")

    print(f"✅ Found {len(desktopInfo)} monitors:")
    for i, info in enumerate(desktopInfo):
        print(f"  Monitor {i}: Desktop {info['desktop_id']} (screen {info['screen']}) "
              f"x={info['x']}, {info['width']}x{info['height']}")

    # calculate total virtual desktop size from monitor info
    min_x = min([ i['x']               for i in desktopInfo ])
    max_x = max([ i['x'] + i['width']  for i in desktopInfo ])
    min_y = min([ i['y']               for i in desktopInfo ])
    max_y = max([ i['y'] + i['height'] for i in desktopInfo ])

    # Load and resize big image
    print(f"\n🖼️  Loading: {sourceImage}")
    bigImage = resizeToVirtualCanvas( Image.open( sourceImage ), max_x - min_x, max_y - min_y )
    imagePrefix = pathlib.Path( sourceImage ).stem

    # Crop for each monitor
    print("\n✂️  Cropping images...")
    cropPaths = []
    for i, info in enumerate(desktopInfo):
        left   = info['x']
        top    = info['y']
        right  = left + info['width']
        bottom = top  + info['height']

        cropped = bigImage.crop((left, top, right, bottom))
        cropPath = f"{tempdir}/{imagePrefix}_crop_{i:02d}.png"
        cropped.save(cropPath)
        cropPaths.append(cropPath)
        print(f"   Monitor {i} → {cropPath} ({cropped.size[0]}x{cropped.size[1]})")

    # Set wallpapers using exact desktop IDs
    print("\n🎨 Setting wallpapers...")
    desktop_ids_js = json.dumps([str(info['desktop_id']) for info in desktopInfo])
    images_js = json.dumps([f"file://{p}" for p in cropPaths])

    JS_SET = f"""
    var all_desktops = desktops();
    var target_ids = {desktop_ids_js};
    var images = {images_js};

    for (var i = 0; i < target_ids.length; i++) {{
        var desktop_id = target_ids[i];
        var desktop = all_desktops[desktop_id];
        if (desktop && desktop.screen != -1) {{
            desktop.wallpaperPlugin = "org.kde.image";
            desktop.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
            desktop.writeConfig("Image", images[i]);
            print("✅ Desktop " + desktop_id + " (screen " + desktop.screen + ") ← " + images[i]);
        }} else {{
            print("⚠️  Desktop " + desktop_id + " no longer valid");
        }}
    }}
    print("🎉 All done!");
    """

    sessionBus = dbus.SessionBus()
    plasma = sessionBus.get_object("org.kde.plasmashell", "/PlasmaShell")
    iface = dbus.Interface(plasma, dbus_interface="org.kde.PlasmaShell")

    result = iface.evaluateScript(JS_SET)
    print("DBUS output:", result)
    print("\n🎉✅ SPANNING WALLPAPER APPLIED TO ALL MONITORS!")

if __name__ == "__main__":
    try:
        applyWallpaper()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
