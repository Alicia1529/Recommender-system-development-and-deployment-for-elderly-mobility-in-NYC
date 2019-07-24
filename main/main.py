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
import pickle
from collections import Counter 
import pymysql.cursors

#import api key
import config
from featureSelection import featureSelection
from linUCB import linUCB
from dataCollection import query_api
import helperFunction

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

# make three predictions
def makeRecommendation(user_id,time,longitude,latitude,radius,price,alpha,conn):
    cursor = conn.cursor()

    #delete recommendation made before 7 days
    query = "DELETE FROM Recommendation WHERE timestamp < (NOW() - INTERVAL 7 DAY)"
    cursor.execute(query)
    conn.commit()
    # get all restaurants recommended in recent 7 days
    query = 'SELECT * FROM Recommendation WHERE user_id = %s'
    cursor.execute(query, (user_id))
    previousRecommendations = cursor.fetchall()
    previousRecommendations  = list(map(lambda x:x["restaurant_id"],previousRecommendations))

    print("-----------------------")
    print(time,longitude,latitude,radius,price)

    restaurants = query_api(time,longitude,latitude,radius,price)
    context_pool = featureSelection(restaurants)
    context_size = len(context_pool[0])-1 # remove arm
    id2context = {}

    for each in context_pool:
        id2context[each[0]] = each[1:]

    A, b = helperFunction.getMatrices(time)
    # A and b both have three matrices, one for morning, one for afternoon and one for evening
    # now, get the matrices according to time 
    # if there is no matrcies stored, then start  with None

    A, b, predictions = linUCB(A, b, [], context_pool, alpha, context_size)

    output = []

    query = 'INSERT INTO `Recommendation`(`user_id`, `restaurant_id`,`context`, `timestamp`) VALUES (%s,%s,%s,CURRENT_TIMESTAMP)'

    for each in predictions:
        if each not in previousRecommendations:
            # update the database with userid, restaurant_id, context information, time
            context = json.dumps(id2context[each]) 
            cursor.execute(query,(user_id,each,context))
            conn.commit()

            restaurant = list(filter(lambda x:x["id"]==each,restaurants))[0]
            restaurant_info = {"name":restaurant["name"],
            'id':restaurant["id"],
            'price':restaurant['price'],
            'review_count':restaurant['review_count'],
            'rating':restaurant['rating'],
            'categories':restaurant['categories'],
            'phone':restaurant['phone'],
            'display_phone':restaurant['display_phone'],
            'location':restaurant['location']['address1'],
            "coordinates":restaurant["coordinates"],
            'distance':restaurant['distance']}
            output.append(restaurant_info)
        if len(output) >=3:
            break

    output = json.dumps(output)
    return output

def updateReward(user_id,time,restaurant_id,reward,alpha,conn):
    cursor = conn.cursor()
    #delete recommendation made before 7 days
    query = "DELETE FROM Recommendation WHERE timestamp < (NOW() - INTERVAL 7 DAY)"
    cursor.execute(query)
    conn.commit()

    query = "SELECT context FROM recommendation where user_id = %s and restaurant_id = %s"
    cursor.execute(query, (user_id,restaurant_id))
    context = json.loads(cursor.fetchone()["context"])

    #store this feedback to history schema
    query = "INSERT INTO history(user_id,restaurant_id,reward) VALUES(%s,%s,%s)"
    cursor.execute(query, (user_id,restaurant_id,reward))
    conn.commit()

    result = [reward,restaurant_id,context]

    A, b = helperFunction.getMatrices(time)
    # A and b both have three matrices, one for morning, one for afternoon and one for evening
    # now, get the matrices according to time 
    # if there is no matrcies stored, then start  with None

    A, b, _ = linUCB(A, b, [result], [], alpha, len(context)) #it's learning 
    helperFunction.saveMatrices(A, b, time)


if __name__ == "__main__":
     
    conn = pymysql.connect(host='localhost',
                        port = 8889,
                        user='root',
                        password='root',
                        db='UrbanConnectorTest',
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)

    # Defaults
    DEFAULT_USER_ID = "1231241412" #get current time
    DEFAULT_TIME = time.strftime('%H:%M')  #get current time
    DEFAULT_LONGITUDE = -73.984345
    DEFAULT_LATITUDE = 40.693899
    DEFAULT_RADIUS = 1000 #meters
    DEFAULT_PRICE = 2 #means "$$". the program reads $$ as 3754, so need to use int to represent it
    alpha = 2

    CONTINUE = True

    while CONTINUE:
        output = makeRecommendation(DEFAULT_USER_ID,DEFAULT_TIME,DEFAULT_LONGITUDE,DEFAULT_LATITUDE,DEFAULT_RADIUS,DEFAULT_PRICE,alpha,conn)
        print(output)
        answer = input("Please give your choice:\n")
        if answer == "END":
            CONTINUE = False #end the program
        elif answer == "NONE":
            pass
        else:
            updateReward(DEFAULT_USER_ID,DEFAULT_TIME,answer,1,alpha,conn) 
    
    conn.close()
    