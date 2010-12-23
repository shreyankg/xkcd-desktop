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

import os.path
import urllib
import json
from subprocess import call
import Image, ImageDraw, ImageFont

TMPFILE = "/tmp/xkcd.png"
XKCD_URL = "http://xkcd.com/info.0.json"
BACKGROUND = "#ffffffffffff"

FONT = os.path.join(os.path.dirname(__file__)
    , "Humor-Sans.ttf")
HEAD = 25
FOOT = 15
FORMAT = "PNG"
TEXT_COLOR = "#000000"

def wrap(text, width):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    w = reduce(lambda line, word, width=width: '%s%s%s' %
        (line,
        ' \n'[(len(line)-line.rfind('\n')-1
             + len(word.split('\n',1)[0]
                  ) >= width)],
        word),
        text.split(' ')
    )
    return w.split('\n')

# Gather JSON data from xkcd.com
fd = urllib.urlopen(XKCD_URL)
json_data = json.load(fd)
url = json_data['img']
title = json_data['title']
footer = wrap(json_data['alt'], 80)

# Download image
call(["wget", 
    "-O",
    TMPFILE,
    url])

# Image processing to put text onto the image

# Initiatize font objects
header_font = ImageFont.truetype(FONT, HEAD)
footer_font = ImageFont.truetype(FONT, FOOT)

# Calculate text sizes
head_size = header_font.getsize(title)
foot_sizes_hor = [footer_font.getsize(foot)[0] for foot in footer]
foot_size_ver = footer_font.getsize("test")[1]

# Open original image
xkcd = Image.open(TMPFILE)

# Calculate size of the new image
new_size = (
    max(foot_sizes_hor + [xkcd.size[0], head_size[0]]),
    (xkcd.size[1] + head_size[1] + 
        (foot_size_ver + 5)*len(footer) + 20))

# New image instance
out = Image.new('RGB', new_size, '#ffffff')

# Start drawing
draw = ImageDraw.Draw(out)

head_position = (
    (new_size[0] - head_size[0])/2,
    5)

draw.text(head_position, title, font=header_font, fill=TEXT_COLOR)

# For each line in footer
for index, foot in enumerate(footer):
    foot_position_hor = (new_size[0] - foot_sizes_hor[index])/2
    foot_position_ver = xkcd.size[1] + head_size[1] + (index *
        (foot_size_ver + 5)) + 15
    foot_position = (foot_position_hor, foot_position_ver)
    draw.text(foot_position, foot, font=footer_font, fill=TEXT_COLOR)

# Delete draw object 
del draw 

# Paster original image
xkcd_position = ((new_size[0] -xkcd.size[0])/2,
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
    BACKGROUND])
call(["gconftool-2",
    "-t",
    "str",
    "--set",
    "/desktop/gnome/background/secondary_color",
    BACKGROUND])
call(["gconftool-2",
    "-t",
    "str",
    "--set",
    "/desktop/gnome/background/picture_filename",
    TMPFILE])

