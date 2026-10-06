"""Optimize synthetic product captures and compose the site's device artwork.

Usage: python3 scripts/prepare-assets.py --captures DIR --logo FILE --phone FILE
The supplied captures must be test fixtures, never a personal desktop or phone.
Pillow is only needed when updating artwork, not for the website build.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

parser = argparse.ArgumentParser()
parser.add_argument("--captures", type=Path, required=True)
parser.add_argument("--logo", type=Path, required=True)
parser.add_argument("--phone", type=Path, required=True)
args = parser.parse_args()
out = Path(__file__).resolve().parents[1] / "public" / "images"
out.mkdir(parents=True, exist_ok=True)


def rounded(image, radius):
    mask = Image.new("L", image.size)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, image.width, image.height), radius, fill=255)
    image.putalpha(mask)
    return image


def shadow(canvas, box, radius):
    layer = Image.new("RGBA", canvas.size)
    ImageDraw.Draw(layer).rounded_rectangle(box, radius, fill=(12, 22, 28, 55))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(22)))


phone = Image.open(args.phone).convert("RGBA")
logo = Image.open(args.logo).convert("RGBA")
logo.thumbnail((160, 160), Image.Resampling.LANCZOS)
logo.save(out / "logo.webp", quality=95)
logo.resize((48, 48), Image.Resampling.LANCZOS).save(out / "favicon.png")

for theme in ("light", "dark"):
    for screen in ("transfers", "mirroring"):
        source = args.captures / f"chromium-{theme}-{screen}.png"
        image = Image.open(source).convert("RGB")
        image.save(out / f"mac-{screen}-{theme}.webp", quality=92)
    canvas = Image.new("RGBA", (1440, 820))
    screenshot = Image.open(args.captures / f"chromium-{theme}-devices.png").convert("RGBA")
    screenshot = screenshot.resize((1000, round(screenshot.height * 1000 / screenshot.width)), Image.Resampling.LANCZOS)
    surface = (246, 246, 249, 255) if theme == "light" else (24, 25, 30, 255)
    window = Image.new("RGBA", (1024, screenshot.height + 50), surface)
    window.alpha_composite(screenshot, (12, 38))
    draw = ImageDraw.Draw(window)
    for x, color in ((26, "#ec7771"), (47, "#e8bf69"), (68, "#78b88e")):
        draw.ellipse((x, 14, x + 11, 25), fill=color)
    rounded(window, 22)
    shadow(canvas, (74, 33, 1098, 33 + window.height), 26)
    canvas.alpha_composite(window, (74, 14))
    screen = phone.resize((280, round(phone.height * 280 / phone.width)), Image.Resampling.LANCZOS)
    device = Image.new("RGBA", (304, screen.height + 48), (34, 38, 40, 255))
    rounded(screen, 30)
    device.alpha_composite(screen, (12, 24))
    draw = ImageDraw.Draw(device)
    draw.ellipse((146, 8, 156, 18), fill="#0c0e10")
    rounded(device, 40)
    phone_y = 14 + window.height - device.height
    shadow(canvas, (1058, phone_y + 25, 1362, phone_y + 25 + device.height), 42)
    canvas.alpha_composite(device, (1058, phone_y))
    canvas.save(out / f"hero-{theme}.webp", quality=94)

print(f"Prepared website artwork in {out}")
