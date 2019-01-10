#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import json
import time
import urllib
import argparse
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont
#from font_fredoka_one import FredokaOne
from font_source_sans_pro import SourceSansProBold

from utils import get_api_key

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

print("""Inky pHAT: Weather
""")

# Command line arguments to set display colour

parser = argparse.ArgumentParser()
parser.add_argument('--colour', '-c', type=str, required=True, choices=["red", "black", "yellow"], help="ePaper display colour")
args = parser.parse_args()

# Set up the display

colour = args.colour
inky_display = InkyPHAT(colour)
inky_display.set_border(inky_display.BLACK)

# Details to customise your weather display

DATAPOINT_ID   = '351765'
DATAPOINT_KEY  = get_api_key()
USE_LOCAL_TEMP = False

# Python 2 vs 3 breaking changes
def encode(qs):
    val = ""
    try:
        val = urllib.urlencode(qs).replace("+", "%20")
    except AttributeError:
        val = urllib.parse.urlencode(qs).replace("+", "%20")
    return val


# Query the MetOffice weather API
def get_weather():
    uri = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/" + DATAPOINT_ID + "?res=3hourly&key=" + DATAPOINT_KEY

    res = requests.get(uri)
    if res.status_code == 200:
        json_data = json.loads(res.text)
        return json_data

    return {}

def get_local_temp():
    uri = "http://zeropi:8080/status"

    res = requests.get(uri)
    if res.status_code == 200:
        json_data = json.loads(res.text)
        if 'Temp' in json_data:
            return int(json_data['Temp'])

    return -255

def create_mask(source, mask=(inky_display.WHITE, inky_display.BLACK, inky_display.RED)):
    """Create a transparency mask.

    Takes a paletized source image and converts it into a mask
    permitting all the colours supported by Inky pHAT (0, 1, 2)
    or an optional list of allowed colours.

    :param mask: Optional list of Inky pHAT colours to allow.

    """
    mask_image = Image.new("1", source.size)
    w, h = source.size
    for x in range(w):
        for y in range(h):
            p = source.getpixel((x, y))
            if p in mask:
                mask_image.putpixel((x, y), 255)

    return mask_image


# Dictionaries to store our icons and icon masks in
icons = {}
masks = {}

# Get the weather data for the given location
weather = get_weather()

# This maps the weather codes from the Yahoo weather API
# to the appropriate weather icons
icon_map = {
    "snow": [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
    "rain": [9, 10, 11, 12, 13, 14, 15],
    "cloud": [2, 3],
    "overcast": [5, 6, 7, 8],
    "sun": [0, 1],
    "storm": [28, 29, 30]
}

# Placeholder variables
wind = 0
temperature = 0
feelslike = 0
precip = 0
weather_icon = None

# Pull out the appropriate values from the weather data
if "Period" in weather["SiteRep"]["DV"]["Location"]:
    print "Displaying weather for: " + weather["SiteRep"]["DV"]["Location"]["name"]
    period = weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"]
    if len(period) > 2: results = period[2]
    else: results = weather["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"][2 - len(period)]
    temperature = int(results["T"])
    feelslike = int(results["F"])
    wind = int(results["S"])
    precip = int(results["Pp"])
    code = int(results["W"])

    for icon in icon_map:
        if code in icon_map[icon]:
            weather_icon = icon
            break

    if wind > 20: 
        weather_icon = "wind"

else:
    print("Warning, no weather information found!")

# Create a new canvas to draw on
img = Image.open("resources/backdrop.png")
draw = ImageDraw.Draw(img)

# Load our icon files and generate masks
for icon in glob.glob("resources/icon-*.png"):
    icon_name = icon.split("icon-")[1].replace(".png", "")
    icon_image = Image.open(icon)
    icons[icon_name] = icon_image
    masks[icon_name] = create_mask(icon_image)

# Load the FredokaOne font
font = ImageFont.truetype(SourceSansProBold, 24)
font_small = ImageFont.truetype(SourceSansProBold, 13)

# Draw lines to frame the weather data
draw.line((69, 36, 69, 81))       # Vertical line
draw.line((31, 35, 184, 35))      # Horizontal top line
draw.line((69, 58, 174, 58))      # Horizontal middle line
draw.line((169, 58, 169, 58), 2)  # Red seaweed pixel :D

# Write text with weather values to the canvas
if USE_LOCAL_TEMP:
    datetime = time.strftime("%H:%M")

    draw.text((110, 8), datetime, inky_display.WHITE, font=font)
    local_temp = get_local_temp()
    if local_temp > -255:
        draw.text((50, 8), u"{}°".format(local_temp), inky_display.RED, font=font)
else:
    datetime = time.strftime("%d/%m %H:%M")
    draw.text((45, 8), datetime, inky_display.WHITE, font=font)

draw.text((75, 32), u"{}°".format(temperature), inky_display.WHITE, font=font)
draw.text((75, 55), u"{}°".format(feelslike), inky_display.RED, font=font)

wind_msg = "{}".format(wind)
w, h = font.getsize(wind_msg)
draw.text((115, 32), wind_msg, inky_display.RED, font=font)
draw.text((115+w+1, 42), "mph", inky_display.RED, font=font_small)

precip_msg = "{}".format(precip)
w, h = font.getsize(precip_msg)
draw.text((115, 55), precip_msg, inky_display.WHITE, font=font)
draw.text((115+w, 59), "%", inky_display.WHITE, font=font_small)


# Draw the current weather icon over the backdrop
if weather_icon is not None:
    img.paste(icons[weather_icon], (28, 36), masks[weather_icon])

else:
    draw.text((28, 36), "?", inky_display.RED, font=font)

# Display the weather data on Inky pHAT
inky_display.set_image(img)
inky_display.show()
