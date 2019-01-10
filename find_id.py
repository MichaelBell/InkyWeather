#!/usr/bin/env python

import requests, json
from utils import find_id

# You can use this function to automatically find your location
# based on your IP address
def get_location():
    res = requests.get('http://ipinfo.io')
    if(res.status_code == 200):
        json_data = json.loads(res.text)
        print json_data
        return json_data['loc']
    return "53,-1"

if __name__ == "__main__":
    print "Please enter your latitude, longitude e.g. 53.123, -1.520"
    loc = raw_input("Or just press Enter to guess based on your IP: ")
    loc = loc.strip()
    if loc == "":
        loc = get_location()

    loc = loc.split(',')
    loc = (float(loc[0]), float(loc[1]))

    print "Finding location ID for ({}, {})".format(*loc)
    print "Location ID: " + find_id(*loc)
