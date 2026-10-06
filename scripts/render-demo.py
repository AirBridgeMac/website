"""Render a silent, synthetic feature walkthrough for the website."""

import argparse
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SIZE = (1280, 720)
FPS = 60
SCENES = [
    ("intro", 0.8),
    ("files", 4.15),
    ("clipboard", 3.45),
    ("notifications", 3.25),
    ("mirroring", 4.25),
    ("outro", 1.35),
]
STARTS = []
elapsed = 0.0
for _, duration in SCENES:
    STARTS.append(elapsed)
    elapsed += duration
DURATION = elapsed

BG = "#11151c"
PANEL = "#1d2430"
PANEL_2 = "#27313e"
STROKE = "#3c4b5d"
WHITE = "#f6f8fc"
MUTED = "#abb8ca"
BLUE = "#69b8ff"
PURPLE = "#ad9cff"
CYAN = "#84e1f2"
FONT_PATH = "/System/Library/Fonts/SFNS.ttf"
FONTS = {n: ImageFont.truetype(FONT_PATH, n) for n in (11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 24, 26, 29, 38, 48, 72)}
LOGO = Image.open(ROOT / "public/images/logo.webp").convert("RGBA")

MAC_CANVAS = "#f7f7f9"
MAC_SURFACE = "#ffffff"
MAC_INK = "#1c1e24"
MAC_MUTED = "#626873"
MAC_LINE = "#e3e5e9"
MAC_ACCENT = "#7755ac"
MAC_SOFT = "#ebe5f4"
ANDROID_BG = "#151618"
ANDROID_SURFACE = "#23252a"
ANDROID_INK = "#f0f1f4"
ANDROID_MUTED = "#acb0ba"
ANDROID_ACCENT = "#c0a6f0"
ANDROID_LINE = "#303237"
MAC_FRAME = (72, 258, 808, 645)
MAC_TARGET = (72, 215, 728, 680)
PHONE_FRAME = (922, 235, 1198, 660)
PHONE_TARGET = (934, 215, 1178, 690)


class DeviceDraw:
    """Reflow device geometry while keeping type at its original proportions."""

    def __init__(self, draw, source, target):
        self.draw = draw
        self.source = source
        self.target = target

    def point(self, x, y):
        sx1, sy1, sx2, sy2 = self.source
        tx1, ty1, tx2, ty2 = self.target
        return (round(tx1 + (x - sx1) * (tx2 - tx1) / (sx2 - sx1)),
                round(ty1 + (y - sy1) * (ty2 - ty1) / (sy2 - sy1)))

    def box(self, box):
        return (*self.point(box[0], box[1]), *self.point(box[2], box[3]))

    def rounded_rectangle(self, box, **kwargs):
        self.draw.rounded_rectangle(self.box(box), **kwargs)

    def rectangle(self, box, **kwargs):
        self.draw.rectangle(self.box(box), **kwargs)

    def ellipse(self, box, **kwargs):
        self.draw.ellipse(self.box(box), **kwargs)

    def arc(self, box, **kwargs):
        self.draw.arc(self.box(box), **kwargs)

    def line(self, points, **kwargs):
        mapped = [self.point(points[i], points[i + 1]) for i in range(0, len(points), 2)]
        self.draw.line(mapped, **kwargs)

    def polygon(self, points, **kwargs):
        self.draw.polygon([self.point(x, y) for x, y in points], **kwargs)

    def text(self, xy, value, **kwargs):
        self.draw.text(self.point(*xy), value, **kwargs)


class DeviceImage:
    def __init__(self, image, mapped_draw):
        self.image = image
        self.mapped_draw = mapped_draw

    def alpha_composite(self, overlay, xy):
        self.image.alpha_composite(overlay, self.mapped_draw.point(*xy))


def mac_draw(draw):
    return DeviceDraw(draw, MAC_FRAME, MAC_TARGET)


def phone_draw(draw):
    return DeviceDraw(draw, PHONE_FRAME, PHONE_TARGET)


def clamp(value):
    return max(0.0, min(1.0, value))


def ease(value):
    value = clamp(value)
    return value * value * (3 - 2 * value)


def tween(a, b, value):
    return a + (b - a) * ease(value)


def text(draw, xy, value, size=20, fill=WHITE, anchor=None):
    draw.text(xy, value, font=FONTS[size], fill=fill, anchor=anchor)


def card(draw, box, fill=PANEL, outline=STROKE, radius=16, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def logo(image, box):
    x, y, side = box
    mark = LOGO.resize((side, side), Image.Resampling.LANCZOS)
    image.alpha_composite(mark, (x, y))


def base():
    image = Image.new("RGBA", SIZE, BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, SIZE[0], 7), fill=BLUE)
    logo(image, (72, 39, 48))
    text(draw, (131, 63), "AirBridge", 24, anchor="lm")
    text(draw, (1192, 63), "MAC + ANDROID", 15, MUTED, anchor="rm")
    draw.line((72, 105, 1208, 105), fill=STROKE, width=2)
    return image, draw


def title(draw, number, heading, detail):
    text(draw, (72, 116), f"0{number} / 04", 16, BLUE)
    text(draw, (72, 148), heading, 38)
    text(draw, (72, 193), detail, 16, MUTED)


def mac(image, draw, mode, transfer=None, mirror_active=False):
    draw = mac_draw(draw)
    image = DeviceImage(image, draw)
    card(draw, (72, 258, 808, 645), MAC_CANVAS, "#d9dbe1", 18, 2)
    draw.rectangle((73, 298, 807, 624), fill=MAC_CANVAS)
    for i, color in enumerate(("#f07673", "#efc464", "#70c890")):
        draw.ellipse((95 + i * 20, 278, 106 + i * 20, 289), fill=color)
    if mode == "Desktop":
        draw.rectangle((74, 299, 806, 623), fill="#e6e9f1")
        draw.rectangle((74, 468, 806, 623), fill="#d9dfe9")
        text(draw, (175, 285), "Finder", 13, MAC_INK, anchor="lm")
        card(draw, (325, 582, 559, 619), "#ffffffcc", "#c9ced7", 12, 1)
        for i, color in enumerate((MAC_ACCENT, "#7895b6", "#9e83bf", "#c98f74")):
            card(draw, (342 + i * 53, 588, 368 + i * 53, 614), color, None, 6, 0)
        return
    if mode in ("Finder", "Notes"):
        text(draw, (440, 285), mode, 14, MAC_MUTED, anchor="mm")
        card(draw, (86, 308, 235, 628), "#f0f0f3", MAC_LINE, 16, 1)
        labels = ("Recents", "Documents", "Downloads", "Pictures") if mode == "Finder" else ("All Notes", "Today", "Shared")
        selected = "Documents" if mode == "Finder" else "Today"
        for i, label in enumerate(labels):
            y = 350 + i * 46
            if label == selected:
                card(draw, (99, y - 10, 221, y + 22), MAC_SOFT, None, 15, 0)
            text(draw, (113, y + 6), label, 15, MAC_ACCENT if label == selected else MAC_MUTED, anchor="lm")
        text(draw, (261, 348), "Documents" if mode == "Finder" else "Today's note", 26, MAC_INK)
        draw.line((261, 390, 775, 390), fill=MAC_LINE, width=1)
        return
    card(draw, (86, 308, 235, 628), "#f3f3f6", MAC_LINE, 17, 1)
    logo(image, (101, 325, 30))
    text(draw, (140, 343), "AirBridge", 19, MAC_INK, anchor="lm")
    for i, label in enumerate(("Devices", "Transfers", "Mirroring", "Settings")):
        y = 393 + i * 43
        if label == mode:
            card(draw, (98, y - 13, 223, y + 21), MAC_SOFT, None, 17, 0)
        icon_color = MAC_ACCENT if label == mode else MAC_INK
        if label == "Devices":
            card(draw, (112, y - 7, 124, y + 13), None, icon_color, 3, 2)
            draw.ellipse((117, y + 8, 119, y + 10), fill=icon_color)
        elif label == "Transfers":
            draw.line((114, y - 5, 114, y + 10), fill=icon_color, width=2)
            draw.line((112, y - 3, 114, y - 5, 116, y - 3), fill=icon_color, width=2)
            draw.line((123, y - 5, 123, y + 10), fill=icon_color, width=2)
            draw.line((121, y + 8, 123, y + 10, 125, y + 8), fill=icon_color, width=2)
        elif label == "Mirroring":
            card(draw, (110, y - 6, 126, y + 7), None, icon_color, 2, 2)
            draw.line((115, y + 10, 121, y + 10), fill=icon_color, width=2)
        else:
            draw.line((111, y - 4, 126, y - 4), fill=icon_color, width=2)
            draw.line((111, y + 5, 126, y + 5), fill=icon_color, width=2)
            draw.ellipse((114, y - 7, 119, y - 2), fill=icon_color)
            draw.ellipse((120, y + 2, 125, y + 7), fill=icon_color)
        text(draw, (137, y + 4), label, 15, MAC_ACCENT if label == mode else MAC_INK, anchor="lm")
    text(draw, (102, 588), "Studio Mac", 13, MAC_INK)
    draw.ellipse((102, 612, 108, 618), fill="#416e5e")
    text(draw, (116, 613), "Ready to receive", 11, MAC_MUTED, anchor="lm")
    text(draw, (260, 326), mode, 26, MAC_INK)
    if mode == "Transfers":
        card(draw, (641, 320, 778, 353), "#eaeaf0", None, 17, 0)
        text(draw, (709, 336), "Open in Finder", 13, MAC_INK, anchor="mm")
        card(draw, (260, 381, 440, 416), "#eaeaf0", None, 18, 0)
        card(draw, (265, 385, 310, 412), MAC_SURFACE, None, 14, 0)
        for x, label in ((287, "All"), (349, "Received"), (411, "Sent")):
            text(draw, (x, 399), label, 12, MAC_INK, anchor="mm")
        card(draw, (616, 381, 778, 416), MAC_SURFACE, MAC_LINE, 18, 1)
        text(draw, (634, 398), "Search transfers", 12, MAC_MUTED, anchor="lm")
        text(draw, (260, 438), "Activity", 17, MAC_INK)
        text(draw, (768, 440), "1" if transfer else "0", 12, MAC_MUTED, anchor="rm")
        if transfer:
            name, status, progress = transfer
            card(draw, (260, 470, 778, 552), MAC_SURFACE, None, 17, 0)
            card(draw, (276, 489, 313, 531), "#f1edf7", None, 10, 0)
            text(draw, (294, 510), "F", 20, MAC_ACCENT, anchor="mm")
            text(draw, (329, 495), name, 17, MAC_INK)
            text(draw, (329, 522), "From Studio Mac" if status == "Sent" else "From Android", 13, MAC_MUTED)
            text(draw, (755, 495), status, 13, MAC_ACCENT if progress is not None else "#416e5e", anchor="rt")
            if progress is not None:
                draw.line((329, 537, 744, 537), fill=MAC_LINE, width=4)
                draw.line((329, 537, 329 + int(415 * progress), 537), fill=MAC_ACCENT, width=4)
    elif mode == "Mirroring":
        card(draw, (433, 372, 580, 453), "#303443", "#8a8f9a", 10, 5)
        if mirror_active:
            text(draw, (506, 397), "Studio Mac", 13, WHITE, anchor="mm")
            for i, color in enumerate((ANDROID_ACCENT, "#8bcab3", "#a1b7e1")):
                card(draw, (455 + i * 36, 411, 484 + i * 36, 438), color, None, 6, 0)
        else:
            logo(image, (485, 389, 43))
        card(draw, (548, 419, 596, 474), "#303443", "#8a8f9a", 9, 4)
        logo(image, (558, 429, 28))
        text(draw, (307, 502), "Wireless mirroring", 17, MAC_INK)
        text(draw, (758, 505), "Wi-Fi", 12, MAC_MUTED, anchor="rm")
        text(draw, (307, 545), "Phone", 14, MAC_INK)
        card(draw, (544, 529, 767, 565), MAC_SURFACE, MAC_LINE, 18, 1)
        text(draw, (560, 547), "Android phone", 13, MAC_INK, anchor="lm")
        draw.line((307, 575, 767, 575), fill=MAC_LINE, width=1)
        text(draw, (307, 599), "Mirroring" if mirror_active else "Not mirroring", 13, MAC_MUTED, anchor="lm")
        card(draw, (636, 581, 767, 616), "#eaeaf0" if mirror_active else "#262831", None, 18, 0)
        text(draw, (701, 598), "Stop" if mirror_active else "Start mirroring", 13, MAC_INK if mirror_active else MAC_SURFACE, anchor="mm")


def phone(image, draw, mode="home", file=None, progress=None, complete=False):
    draw = phone_draw(draw)
    image = DeviceImage(image, draw)
    card(draw, (922, 235, 1198, 660), "#25272d", "#737985", 39, 4)
    card(draw, (934, 248, 1186, 648), ANDROID_BG, None, 29, 0)
    draw.rounded_rectangle((1026, 255, 1094, 268), radius=7, fill="#090b0f")
    draw.rounded_rectangle((1020, 638, 1099, 642), radius=2, fill="#acb0ba")
    if mode == "share":
        logo(image, (950, 283, 29))
        text(draw, (987, 299), "AirBridge", 20, ANDROID_INK, anchor="lm")
        text(draw, (951, 348), "1 file", 15, ANDROID_MUTED)
        text(draw, (951, 383), "Studio Mac", 18, ANDROID_INK)
        if complete:
            text(draw, (951, 436), file or "Project notes.pdf", 16, ANDROID_INK)
            text(draw, (951, 470), "Sent to Mac", 14, ANDROID_ACCENT)
            card(draw, (950, 516, 1170, 559), ANDROID_SURFACE, None, 21, 0)
            text(draw, (1060, 537), "Done", 16, ANDROID_INK, anchor="mm")
        elif progress is not None:
            text(draw, (951, 425), "Sending to Mac", 14, ANDROID_MUTED)
            text(draw, (951, 458), file or "Project notes.pdf", 16, ANDROID_INK)
            draw.line((951, 493, 1170, 493), fill=ANDROID_LINE, width=4)
            draw.line((951, 493, 951 + int(219 * progress), 493), fill=ANDROID_ACCENT, width=4)
            text(draw, (951, 516), f"{int(progress * 100)}%", 13, ANDROID_ACCENT)
        else:
            card(draw, (950, 413, 1170, 461), "#f0edf6", None, 23, 0)
            text(draw, (1060, 437), "Send file", 16, "#25222c", anchor="mm")
            text(draw, (951, 508), file or "Project notes.pdf", 16, ANDROID_INK)
        return
    if mode in ("chat", "messages"):
        text(draw, (951, 297), "Messages", 20, ANDROID_INK)
        draw.line((950, 322, 1170, 322), fill=ANDROID_LINE, width=1)
        text(draw, (951, 359), "Alex", 16, ANDROID_MUTED)
        card(draw, (958, 469, 1170, 521), ANDROID_SURFACE, None, 18, 0)
        text(draw, (972, 492), "Message", 14, ANDROID_MUTED, anchor="lm")
        return
    text(draw, (950, 296), "AirBridge", 22, ANDROID_INK)
    card(draw, (1101, 279, 1132, 310), "#292b30", None, 16, 0)
    card(draw, (1140, 279, 1171, 310), "#292b30", None, 16, 0)
    for x, y in ((1111, 290), (1119, 290), (1111, 298), (1119, 298)):
        draw.rectangle((x, y, x + 3, y + 3), fill=ANDROID_MUTED)
    draw.arc((1149, 287, 1163, 303), start=40, end=300, fill=ANDROID_MUTED, width=2)
    draw.line((1162, 289, 1163, 296, 1157, 294), fill=ANDROID_MUTED, width=2)
    logo(image, (1037, 330, 49))
    text(draw, (1060, 392), "Studio Mac", 19, ANDROID_INK, anchor="mm")
    text(draw, (1060, 415), "Connected on Wi-Fi", 12, "#8bcab3", anchor="mm")
    card(draw, (950, 436, 1078, 469), "#f0edf6", None, 17, 0)
    text(draw, (1014, 452), "Send files", 14, "#25222c", anchor="mm")
    card(draw, (1087, 436, 1170, 469), ANDROID_SURFACE, None, 17, 0)
    text(draw, (1128, 452), "Mirror", 14, ANDROID_INK, anchor="mm")
    text(draw, (951, 492), "Recent files", 15, ANDROID_INK)
    text(draw, (1170, 493), "View all", 11, ANDROID_MUTED, anchor="rt")
    if file:
        card(draw, (950, 516, 979, 548), "#302b38", None, 8, 0)
        text(draw, (965, 532), "F", 16, ANDROID_ACCENT, anchor="mm")
        text(draw, (989, 522), file, 13, ANDROID_INK)
        text(draw, (989, 543), "Received from Mac", 11, ANDROID_MUTED)
    else:
        text(draw, (951, 528), "No received files yet", 12, ANDROID_MUTED)
    draw.line((951, 562, 1170, 562), fill=ANDROID_LINE, width=1)
    text(draw, (951, 582), "Clipboard sync", 13, ANDROID_MUTED)
    text(draw, (1170, 582), "On", 12, ANDROID_ACCENT, anchor="rt")
    card(draw, (950, 602, 1170, 634), "#292b30", "#36383e", 17, 1)
    for x, label in ((986, "Devices"), (1060, "Files"), (1134, "Settings")):
        icon_color = ANDROID_ACCENT if label == "Devices" else ANDROID_MUTED
        if label == "Devices":
            card(draw, (x - 6, 605, x + 6, 615), None, icon_color, 2, 1)
        elif label == "Files":
            card(draw, (x - 6, 605, x + 6, 615), None, icon_color, 2, 1)
            draw.line((x - 2, 608, x + 3, 608), fill=icon_color, width=1)
        else:
            draw.line((x - 7, 608, x + 7, 608), fill=icon_color, width=1)
            draw.line((x - 7, 613, x + 7, 613), fill=icon_color, width=1)
        text(draw, (x, 626), label, 11, ANDROID_INK if label == "Devices" else ANDROID_MUTED, anchor="mm")


def arrow(draw, x1, y1, x2, y2, color=BLUE):
    draw.line((x1, y1, x2, y2), fill=color, width=4)
    angle = math.atan2(y2 - y1, x2 - x1)
    for offset in (-0.65, 0.65):
        x = x2 - 16 * math.cos(angle + offset)
        y = y2 - 16 * math.sin(angle + offset)
        draw.line((x2, y2, int(x), int(y)), fill=color, width=4)


def files(local):
    image, draw = base()
    title(draw, 1, "Send a file. Keep moving.", "Share from either device on your local network.")
    m = mac_draw(draw)
    if local < 2.1:
        mac(image, draw, "Finder")
        phone(image, draw, "home", file="Weekend photo.jpg" if local >= 1.6 else None)
        text(m, (260, 404), "Selected in Finder", 15, MAC_MUTED)
        card(m, (260, 427, 540, 487), MAC_SURFACE, MAC_LINE, 12, 1)
        card(m, (271, 438, 310, 476), "#f1edf7", None, 9, 0)
        text(m, (290, 457), "F", 20, MAC_ACCENT, anchor="mm")
        text(m, (322, 457), "Weekend photo.jpg", 16, MAC_INK, anchor="lm")
        progress = ease((local - 0.9) / 0.7)
        x = tween(748, 911, progress)
        if 0.9 <= local < 1.6:
            arrow(draw, 748, 475, 910, 475, PURPLE)
            draw.ellipse((int(x - 11), 464, int(x + 11), 486), fill=PURPLE)
        elif local < 0.45:
            card(m, (552, 415, 738, 503), MAC_SURFACE, MAC_LINE, 11, 1)
            text(m, (568, 425), "Share", 15, MAC_INK)
            m.line((565, 459, 725, 459), fill=MAC_LINE, width=1)
            text(m, (568, 467), "AirBridge", 15, MAC_ACCENT)
        elif local < 0.9:
            card(m, (350, 367, 696, 556), MAC_SURFACE, "#d6d8de", 16, 1)
            text(m, (369, 384), "AirBridge", 20, MAC_INK)
            text(m, (369, 422), "Weekend photo.jpg - 2.4 MB", 15, MAC_MUTED)
            card(m, (369, 453, 674, 488), MAC_SURFACE, MAC_LINE, 16, 1)
            text(m, (383, 471), "Android phone", 14, MAC_INK, anchor="lm")
            card(m, (594, 504, 674, 540), "#262831", None, 16, 0)
            text(m, (634, 522), "Send", 14, MAC_SURFACE, anchor="mm")
            text(m, (541, 522), "Cancel", 14, MAC_MUTED, anchor="mm")
    else:
        progress = ease((local - 2.35) / 0.9)
        complete = local >= 3.25
        mac(image, draw, "Transfers", transfer=("Project notes.pdf", "Received" if complete else "Receiving", None if complete else progress) if local >= 2.35 else None)
        phone(image, draw, "share", file="Project notes.pdf", progress=progress if 2.35 <= local < 3.25 else None, complete=complete)
        if not complete:
            arrow(draw, 909, 500, 751, 500, PURPLE)
        if 2.35 <= local < 3.25:
            x = tween(908, 751, progress)
            draw.ellipse((int(x - 11), 489, int(x + 11), 511), fill=PURPLE)
    return image


def clipboard(local):
    image, draw = base()
    title(draw, 2, "Copy here. Paste there.", "Text copied on Mac is ready on Android.")
    mac(image, draw, "Notes")
    phone(image, draw, "chat")
    m = mac_draw(draw)
    p = phone_draw(draw)
    text(m, (260, 410), "On your Mac", 15, MAC_MUTED)
    card(m, (260, 430, 763, 506), MAC_SURFACE, MAC_LINE, 11, 1)
    message = "Meet at 3:00 by the station."
    visible = int(len(message) * clamp((local - 0.15) / 0.95))
    text(m, (278, 468), message[:visible], 22, MAC_INK, anchor="lm")
    if 1.2 <= local < 2.35:
        card(m, (273, 445, 638, 488), MAC_SOFT, None, 6, 0)
        text(m, (278, 468), message, 22, MAC_INK, anchor="lm")
        card(m, (653, 433, 738, 469), MAC_SURFACE, MAC_LINE, 12, 1)
        text(m, (696, 451), "Copy", 14, MAC_INK, anchor="mm")
    if local >= 1.6:
        arrow(draw, 750, 476, 908, 476, PURPLE)
        x = tween(755, 908, (local - 1.6) / 0.85)
        draw.rounded_rectangle((int(x - 16), 460, int(x + 16), 492), radius=6, fill=PURPLE)
        text(draw, (int(x), 476), "T", 20, BG, anchor="mm")
    if local >= 2.45:
        card(p, (958, 469, 1170, 554), ANDROID_SURFACE, None, 18, 0)
        text(p, (972, 490), "Meet at 3:00 by", 16, ANDROID_INK)
        text(p, (972, 514), "the station.", 16, ANDROID_INK)
    return image


def notification(local):
    image, draw = base()
    title(draw, 3, "Stay in the loop.", "Selected Android alerts can appear on your Mac.")
    mac(image, draw, "Desktop")
    phone(image, draw, "messages")
    m = mac_draw(draw)
    p = phone_draw(draw)
    if local >= 0.5:
        dy = int(tween(-98, 0, (local - 0.5) / 0.55))
        card(p, (948, 344 + dy, 1174, 452 + dy), ANDROID_SURFACE, ANDROID_LINE, 16, 1)
        text(p, (963, 370 + dy), "Messages", 15, ANDROID_ACCENT)
        text(p, (963, 399 + dy), "Alex", 20, ANDROID_INK)
        text(p, (963, 427 + dy), "On my way.", 18, ANDROID_INK)
    if local >= 1.65:
        dy = int(tween(-100, 0, (local - 1.65) / 0.6))
        card(m, (426, 382 + dy, 762, 505 + dy), "#fafafd", "#d6d8de", 17, 1)
        logo(DeviceImage(image, m), (444, 399 + dy, 26))
        text(m, (478, 414 + dy), "Messages  |  Android", 14, MAC_MUTED, anchor="lm")
        text(m, (449, 441 + dy), "Alex", 20, MAC_INK)
        text(m, (449, 470 + dy), "On my way.", 18, MAC_INK)
    return image


def mirroring(local):
    image, draw = base()
    title(draw, 4, "Mirror when you choose.", "Start from Mac, approve on Android, then view your screen.")
    mac(image, draw, "Mirroring", mirror_active=local >= 2.5)
    phone(image, draw, "home")
    m = mac_draw(draw)
    p = phone_draw(draw)
    if 0.8 <= local < 2.5:
        x = int(tween(785, 737, (local - 0.8) / 0.55))
        y = int(tween(635, 599, (local - 0.8) / 0.55))
        m.polygon([(x, y), (x + 6, y + 27), (x + 12, y + 19), (x + 22, y + 18)], fill=MAC_INK)
    if 1.45 <= local < 2.5:
        card(p, (943, 374, 1178, 529), "#2a2c31", "#55555e", 18, 1)
        text(p, (959, 396), "Share your screen?", 18, ANDROID_INK)
        text(p, (959, 425), "AirBridge can show your", 14, ANDROID_MUTED)
        text(p, (959, 447), "screen on your Mac.", 14, ANDROID_MUTED)
        card(p, (959, 475, 1160, 513), ANDROID_ACCENT, None, 20, 0)
        text(p, (1060, 493), "Start now", 15, "#25222c", anchor="mm")
    if local >= 2.5:
        m.rectangle((248, 309, 792, 624), fill=MAC_CANVAS)
        card(m, (365, 368, 649, 562), "#ffffff", "#cfd2da", 14, 2)
        card(m, (375, 379, 639, 551), ANDROID_BG, None, 10, 0)
        text(m, (395, 402), "AirBridge", 16, ANDROID_INK)
        logo(DeviceImage(image, m), (487, 415, 40))
        text(m, (507, 480), "Studio Mac", 17, ANDROID_INK, anchor="mm")
        card(m, (403, 507, 610, 538), "#292b30", None, 15, 0)
        text(m, (507, 523), "Devices     Files     Settings", 12, ANDROID_INK, anchor="mm")
    text(draw, (72, 693), "Requires USB or wireless debugging setup.", 13, MUTED)
    return image


def splash(local, outro=False):
    image, draw = base()
    offset = 0 if outro else int(tween(35, 0, local / 0.5))
    logo(image, (556, 208 + offset, 168))
    text(draw, (640, 432 + offset), "AirBridge", 72, WHITE, anchor="mm")
    text(draw, (640, 498 + offset), "Your Mac. Your Android. Together.", 24, MUTED, anchor="mm")
    if outro:
        text(draw, (640, 590), "airbridge", 18, BLUE, anchor="mm")
    return image


RENDERERS = {
    "intro": lambda local: splash(local),
    "files": files,
    "clipboard": clipboard,
    "notifications": notification,
    "mirroring": mirroring,
    "outro": lambda local: splash(local, True),
}


def frame(at):
    index = next(
        (i for i in range(len(SCENES) - 1) if at < STARTS[i + 1]),
        len(SCENES) - 1,
    )
    name, duration = SCENES[index]
    image = RENDERERS[name](at - STARTS[index])
    fade_start = STARTS[index] + duration - 0.28
    if at > fade_start and index < len(SCENES) - 1:
        next_name = SCENES[index + 1][0]
        following = RENDERERS[next_name](0)
        return Image.blend(image, following, ease((at - fade_start) / 0.28)).convert("RGB")
    return image.convert("RGB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="Write representative stills only")
    args = parser.parse_args()
    if args.preview:
        folder = ROOT / "artifacts/demo-stills"
        folder.mkdir(parents=True, exist_ok=True)
        for name, at in (("intro", STARTS[0] + 0.5),
                         ("files-start", STARTS[1] + 0.3),
                         ("files-share-dialog", STARTS[1] + 0.7),
                         ("files-out", STARTS[1] + 1.35),
                         ("files-received", STARTS[1] + 1.8),
                         ("files-in", STARTS[1] + 3.35),
                         ("clipboard", STARTS[2] + 2.5),
                         ("notifications", STARTS[3] + 2.05),
                         ("mirroring-start", STARTS[4] + 0.5),
                         ("mirroring-approval", STARTS[4] + 1.95),
                         ("mirroring", STARTS[4] + 3.0),
                         ("outro", STARTS[5] + 0.7)):
            frame(at).save(folder / f"{name}.png")
        print(f"Preview stills: {folder}")
        return
    media = ROOT / "artifacts/demo-media"
    media.mkdir(parents=True, exist_ok=True)
    poster = media / "features-demo-poster.webp"
    frame(STARTS[1] + 1.35).save(poster, "WEBP", quality=88, method=6)
    output = media / "airbridge-features.mp4"
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
        "-pix_fmt", "rgb24", "-s", "1280x720", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for number in range(math.ceil(DURATION * FPS)):
            process.stdin.write(frame(number / FPS).tobytes())
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError("ffmpeg failed to render the demo")
    print(f"Rendered {output} ({DURATION:.2f}s at {FPS}fps)")


if __name__ == "__main__":
    main()
