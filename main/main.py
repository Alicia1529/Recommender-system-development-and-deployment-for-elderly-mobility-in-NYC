# -*- coding: utf-8 -*-
"""
Yelp Fusion API code sample.
This program demonstrates the capability of the Yelp Fusion API
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.
Please refer to http://www.yelp.com/developers/v3/documentation for the API
documentation.
This program requires the Python requests library, which you can install via:
`pip install -r requirements.txt`.
Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib
import time
import random

#import api key
import config
from featureSelection import featureSelection
from linUCB import linUCB
from dataCollection import query_api

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


# Yelp Fusion no longer uses OAuth as of December 7, 2017.
# You no longer need to provide Client ID to fetch Data
# It now uses private keys to authenticate requests (API Key)
# You can find it on
# https://www.yelp.com/developers/v3/manage_app

# Defaults
DEFAULT_TIME = time.strftime('%H:%M')  #get current time
DEFAULT_LONGITUDE = -73.984345
DEFAULT_LATITUDE = 40.693899
DEFAULT_RADIUS = 1000 #meters
DEFAULT_PRICE = 2 #means "$$". the program reads $$ as 3754, so need to use int to represent it
alpha = 2

restaurants = query_api(DEFAULT_TIME, DEFAULT_LONGITUDE, DEFAULT_LATITUDE, DEFAULT_RADIUS,DEFAULT_PRICE )
context_pool = featureSelection(restaurants)
context_size = len(context_pool[0])-1 # remove arm
id2context = {}

for each in context_pool:
    id2context[each[0]] = each[1:]

A, b, prediction = linUCB(None, None, [], context_pool, alpha, context_size)

Continue = True

while Continue:
    predicted_restaurant = list(filter(lambda x:x["id"]==prediction,restaurants))[0]
    print(prediction)
    print(predicted_restaurant)
    reward = int(input("Please give your answer:\n"))
    if reward ==2:
        Continue = False
    context = id2context[prediction]
    result = [reward,prediction,context]


    restaurants = query_api(DEFAULT_TIME, DEFAULT_LONGITUDE, DEFAULT_LATITUDE, DEFAULT_RADIUS,DEFAULT_PRICE )
    context_pool = featureSelection(restaurants)
    context_size = len(context_pool[0])-1 # remove arm
    id2context = {}

    for each in context_pool:
        id2context[each[0]] = each[1:]

    A, b, prediction = linUCB(A, b, [result], context_pool, alpha, context_size) #it's learning 



# output = []
# iteration = 0
# while iteration<3 and restaurants: #either find 3 restaurants or not enough qualified restaurants
#     idx = random.randint(0,len(restaurants)-1)
#     recommendation = {"name":restaurants[idx]["name"],'price':restaurants[idx]['price'],
#     'review_count':restaurants[idx]['review_count'],
#     'rating':restaurants[idx]['rating'],
#     'categories':restaurants[idx]['categories'],
#     'phone':restaurants[idx]['phone'],
#     'display_phone':restaurants[idx]['display_phone'],
#     'location':restaurants[idx]['location']['address1'],
#     "coordinates":restaurants[idx]["coordinates"],
#     'distance':restaurants[idx]['distance']}
#     output.append(recommendation)
#     print()
#     restaurants.pop(idx)
#     iteration+=1
# result = json.dumps(output)
# print(result)
