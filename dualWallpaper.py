#!/usr/bin/env python3
"""
Complete Plasma wallpaper spanning script.
Crops one big panoramic image across all monitors automatically.
"""

import dbus
import json
import re
import pathlib
import os
import shutil
from PIL import Image
import sys
import random
import glob

# === CONFIGURATION ===
TEMP_DIR = str(pathlib.Path.home())+"/.local/share/dualWallpapers/wallpaper_crops"

def get_random_picture(directory):
    """Find all image files in directory and subdirectories, return random one"""
    # Common image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff'}
    image_files = []
    # Method 1: Using pathlib (modern, recommended)
    for ext in image_extensions:
        images = pathlib.Path(directory).rglob(f'*{ext}')
        image_files.extend(images)
    # Convert Path objects to strings
    image_files = [str(img) for img in image_files]
    if not image_files:
        return None
    return random.choice(image_files)

def resize_to_virtual_canvas(img, virtual_width, virtual_height):
    """Resize image to exactly fill virtual canvas."""
    orig_w, orig_h = img.size
    print(f"   Original: {orig_w}x{orig_h}")

    # Scale to fill canvas (may crop)
    scale_w = virtual_width / orig_w
    scale_h = virtual_height / orig_h
    scale = max(scale_w, scale_h)

    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    # Center crop to exact size
    left = (new_w - virtual_width) // 2
    top = (new_h - virtual_height) // 2
    right = left + virtual_width
    bottom = top + virtual_height

    final = resized.crop((left, top, right, bottom))
    print(f"   Resized to virtual canvas: {virtual_width}x{virtual_height}")
    return final

def get_monitor_geometries_and_desktops():
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

def apply_spanning_wallpaper():
    # Setup
    if os.path.isdir(sys.argv[1]):
        old_image = ''
        if os.path.exists(TEMP_DIR):
            try:
                old_image = pathlib.Path(os.listdir(TEMP_DIR)[0]).stem.replace('_crop_00','')
            except:
                pass
            shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR, exist_ok=True)
        BIG_IMAGE = get_random_picture(sys.argv[1])
        if not pathlib.Path(BIG_IMAGE).is_file():
            raise FileNotFoundError(f"❌ Big image not found: {BIG_IMAGE}")

        if old_image == pathlib.Path(BIG_IMAGE).stem:
            BIG_IMAGE = get_random_picture(sys.argv[1])
            if not pathlib.Path(BIG_IMAGE).is_file():
                raise FileNotFoundError(f"❌ Big image not found: {BIG_IMAGE}")
    elif os.path.isfile(sys.argv[1]):
        BIG_IMAGE = sys.argv[1]
        if not pathlib.Path(BIG_IMAGE).is_file():
            raise FileNotFoundError(f"❌ Big image not found: {BIG_IMAGE}")
    else:
        raise FileNotFoundError(f"❌ Big image not found: {BIG_IMAGE}")

    print("📊 Detecting monitors...")
    desktop_info = get_monitor_geometries_and_desktops()
    if not desktop_info:
        raise RuntimeError("❌ No valid monitors detected")

    print(f"✅ Found {len(desktop_info)} monitors:")
    for i, info in enumerate(desktop_info):
        print(f"  Monitor {i}: Desktop {info['desktop_id']} (screen {info['screen']}) "
              f"x={info['x']}, {info['width']}x{info['height']}")

    min_x = min([ i['x'] for i in desktop_info ])
    max_x = max([ i['x']+i['width'] for i in desktop_info ])
    min_y = min([ i['y'] for i in desktop_info ])
    max_y = max([ i['y']+i['height'] for i in desktop_info ])
    TARGET_VIRTUAL_WIDTH  = max_x-min_x
    TARGET_VIRTUAL_HEIGHT = max_y-min_y
    # Load and resize big image
    print(f"\n🖼️  Loading: {BIG_IMAGE}")
    big_img = Image.open(BIG_IMAGE)
    big_img = resize_to_virtual_canvas(big_img, TARGET_VIRTUAL_WIDTH, TARGET_VIRTUAL_HEIGHT)

    image_prefix = pathlib.Path(BIG_IMAGE).stem
    # Update virtual size based on actual monitors (if different)
    total_width = sum(info['width'] for info in desktop_info)
    if total_width != TARGET_VIRTUAL_WIDTH:
        print(f"⚠️  Monitor total width {total_width} ≠ target {TARGET_VIRTUAL_WIDTH}")
        TARGET_VIRTUAL_WIDTH = total_width

    # Crop for each monitor
    print("\n✂️  Cropping images...")
    crop_paths = []
    for i, info in enumerate(desktop_info):
        left = info['x']
        top = info['y']
        right = left + info['width']
        bottom = top + info['height']

        cropped = big_img.crop((left, top, right, bottom))
        crop_path = f"{TEMP_DIR}/{image_prefix}_crop_{i:02d}.jpg"
        cropped.save(crop_path)
        crop_paths.append(crop_path)
        print(f"   Monitor {i} → {crop_path} ({cropped.size[0]}x{cropped.size[1]})")

    # Set wallpapers using exact desktop IDs
    print("\n🎨 Setting wallpapers...")
    desktop_ids_js = json.dumps([str(info['desktop_id']) for info in desktop_info])
    images_js = json.dumps([f"file://{p}" for p in crop_paths])

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

    session_bus = dbus.SessionBus()
    plasma = session_bus.get_object("org.kde.plasmashell", "/PlasmaShell")
    iface = dbus.Interface(plasma, dbus_interface="org.kde.PlasmaShell")

    result = iface.evaluateScript(JS_SET)
    print("DBUS output:", result)
    print("\n🎉✅ SPANNING WALLPAPER APPLIED TO ALL MONITORS!")

if __name__ == "__main__":
    try:
        apply_spanning_wallpaper()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
