#!/usr/bin/env python
#
# xkcd.py
# Script to download the latest XKCD comic 
# and place it as your GNOME wallpaper
# 
# Copyright (C) 2010 Shreyank Gupta <sgupta@REDHAT.COM>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib
import json
from subprocess import call
import Image, ImageDraw, ImageFont

TMPFILE = "/tmp/xkcd.png"
XKCD_URL = "http://xkcd.com/835/info.0.json"

FONT = "/usr/share/fonts/truetype/Humor-Sans.ttf"
HEAD = 25
FOOT = 15
FORMAT = "PNG"
TEXT_COLOR = "#000000"

# Gather JSON data from xkcd.com
fd = urllib.urlopen(XKCD_URL)
json_data = json.load(fd)
url = json_data['img']
title = json_data['title']
footer = json_data['alt']

# Download image
call(["wget", 
    "-O",
    TMPFILE,
    url])

# Image processing to put text onto the image
header_font = ImageFont.truetype(FONT, HEAD)
footer_font = ImageFont.truetype(FONT, FOOT)

head_size = header_font.getsize(title)
foot_size = footer_font.getsize(footer)

xkcd = Image.open(TMPFILE)

new_size = (
    max(xkcd.size[0], head_size[0], foot_size[0]),
    (xkcd.size[1] + head_size[1] + foot_size[1] + 20))

out = Image.new('RGB', new_size, '#ffffff')

head_position = (
    abs(xkcd.size[0] - head_size[0])/2,
    5)
foot_position = (
    abs(xkcd.size[0] - foot_size[0])/2,  
    xkcd.size[1] + head_size[1] + 15)

draw = ImageDraw.Draw(out)

draw.text(head_position, title, font=header_font, fill=TEXT_COLOR)
draw.text(foot_position, footer, font=footer_font, fill=TEXT_COLOR)

del draw 
xkcd_position = (min(0, head_position[0], foot_position[0]),
    head_size[1] + 10)
out.paste(xkcd, xkcd_position)
out.save(TMPFILE, FORMAT)  

# Set as desktop background
call(["gconftool-2",
    "-t",
    "str",
    "--set",
    "/desktop/gnome/background/picture_options",
    "centred"])
call(["gconftool-2",
    "-t",
    "str",
    "--set",
    "/desktop/gnome/background/primary_color",
    "#ffffffffffff"])
call(["gconftool-2",
    "-t",
    "str",
    "--set",
    "/desktop/gnome/background/secondary_color",
    "#ffffffffffff"])
call(["gconftool-2",
    "-t",
    "str",
    "--set",
    "/desktop/gnome/background/picture_filename",
    TMPFILE])

