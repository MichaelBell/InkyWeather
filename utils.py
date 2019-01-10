#!/usr/bin/env python

import requests, json, sys
from math import sqrt

def get_api_key():
	api_key = ""
	with open('api_key.txt') as api_file:
		api_key = api_file.readline()

	return api_key.strip()

def find_id(lat, lon):
	r=requests.get('http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist?key=' + get_api_key())

	locs=json.loads(r.content)['Locations']['Location']

	my_loc = (lat, lon)

	best_dist = 1000
	best_loc = locs[0]

	for l in locs:
		dist = sqrt((float(l['latitude']) - my_loc[0])**2 + (float(l['longitude']) - my_loc[1])**2)
		if dist < best_dist:
			best_dist = dist
			best_loc = l
	return best_loc['id']

if __name__ == '__main__' and len(sys.argv) > 2:
	print find_id(float(sys.argv[1]), float(sys.argv[2]))
