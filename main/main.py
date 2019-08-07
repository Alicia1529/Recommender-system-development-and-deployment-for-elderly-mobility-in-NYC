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
import datetime

#import api key
import config
from featureExtraction import featureExtraction
from linUCB import linUCB
from yelpDataCollection import query_api

from flask import Flask, render_template, request, session, url_for, redirect,make_response,jsonify

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

# update `RecommendationsSevenDays` table every morning, more info can be found in main/app.py(about the frequency and time)
# remove those that are longer than 7 days


def getMatrices(user_profile,time):
    A = None
    b = None

    if time <= "10:30":
        try:
            A = pickle.load(open("model/"+user_profile+"_A1.pyc","rb"))
            b = pickle.load(open("model/"+user_profile+"_b1.pyc","rb"))
        except:
            pass
    elif time<= "14:00":
        try:
            A = pickle.load(open("model/"+user_profile+"_A2.pyc","rb"))
            b = pickle.load(open("model/"+user_profile+"_b2.pyc","rb"))
        except:
            pass
    else:
        try:
            A = pickle.load(open("model/"+user_profile+"_A3.pyc","rb"))
            b = pickle.load(open("model/"+user_profile+"_b3.pyc","rb"))
        except:
            pass
    return A,b



def saveMatrices(user_profile, A, b, time):
    if time <= "10:30":
        pickle.dump(A,open("model/"+user_profile+"_A1.pyc","wb"))
        pickle.dump(b,open("model/"+user_profile+"_b1.pyc","wb"))

    elif time<= "14:00":
        pickle.dump(A,open("model/"+user_profile+"_A2.pyc","wb"))
        pickle.dump(b,open("model/"+user_profile+"_b2.pyc","wb"))

    else:
        pickle.dump(A,open("model/"+user_profile+"_A3.pyc","wb"))
        pickle.dump(b,open("model/"+user_profile+"_b3.pyc","wb"))


def updateDatabase(conn):
    print(datetime.datetime.now(),"Update the database...")
    cursor = conn.cursor()
    #delete recommendation made before 7 days
    # query = "DELETE FROM RecommendationsSevenDays WHERE recommendation_time < (NOW() - INTERVAL 1 second)"
    query = "DELETE FROM RecommendationsSevenDays WHERE recommendation_time < (NOW() - INTERVAL 7 DAY)"
    cursor.execute(query)
    conn.commit()

# make three predictions
def makeRecommendation(user_profile,user_id,time,longitude,latitude,radius,price,alpha,conn):
    cursor = conn.cursor()

    # get all restaurants recommended in recent 7 days
    # avoid making them again
    query = 'SELECT * FROM RecommendationsSevenDays WHERE user_id = %s'
    cursor.execute(query, (user_id))
    previousRecommendations = cursor.fetchall()
    previousRecommendations  = list(map(lambda x:x["restaurant_id"],previousRecommendations))

    # retrieve restaurants according to api
    restaurants = query_api(time,longitude,latitude,radius,price)

    # there are too no restaurants available because the radius is too small or the price preference is very strict
    if len(restaurants) == 0:
        response = make_response(jsonify({"status": 400},{"error":"Please relax restrictions of radius or price prference"}))
        print("-----------response")
        
        return jsonify({"error":"please relax restrictions of radius or price prference"}),200

    # convert the text data to feature matrix
    context_pool = featureExtraction(restaurants)
    context_size = len(context_pool[0])-1 # remove arm
    id2context = {}

    # record the context information
    for each in context_pool:
        id2context[each[0]] = each[1:]

    A, b = getMatrices(user_profile,time)
    # A and b both have three matrices, one for morning, one for afternoon and one for evening
    # now, get the matrices according to time 
    # if there is no matrcies stored, then start  with None

    # run the recommendation algorithm with retrived restauratn data as input and get ranked list of restaurants according to their UCB values
    A, b, predictions = linUCB(A, b, [], context_pool, alpha, context_size)

    output = []

    query0 = 'INSERT INTO `AllRecommendations`(`user_id`, `restaurant_id`, `recommendation_time`,`context`,`local_time`) VALUES (%s,%s,%s,%s,%s)'
    query1 = 'INSERT INTO `RecommendationsSevenDays`(user_id, restaurant_id, recommendation_time) VALUES (%s,%s,%s)'
    
    for each in predictions:
        if each not in previousRecommendations:
            # update the database with userid, restaurant_id, context information, time
            current_time = datetime.datetime.now() 
            #datetime.datetime(2019, 8, 1, 11, 24, 11, 956507)
            f = '%Y-%m-%d %H:%M:%S'
            # format the current time to a timetampe for mysql
            CURRENT_TIME = current_time.strftime(f) 
            # get the current time now.strftime(f) 

            context = json.dumps(id2context[each]) 
            
            # first: update the database for all recommendations  
            # this has to be made ealier than the second one, because there are the primary key 
            cursor.execute(query0,(user_id,each,CURRENT_TIME,context,time))

            # update the database for the past 7 days storage
            cursor.execute(query1,(user_id,each,CURRENT_TIME))
            
            # they have to use the same user_id,each, current_time because they are key and are referencing each other
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
            'distance':restaurant['distance'],
            'recommendation_time':CURRENT_TIME}
            output.append(restaurant_info)
            # the recommendation_time has to be returned and used for update the feedback 
            # this is part of the primary key

        if len(output) >=3:
            break

    # corner case: what if all restaurants are recommended before
    # then ignore the repetition restriction 
    if len(output) == 0:
        for each in predictions[:3]:

                # update the database with userid, restaurant_id, context information, time
                current_time = datetime.datetime.now() 
                #datetime.datetime(2019, 8, 1, 11, 24, 11, 956507)
                f = '%Y-%m-%d %H:%M:%S'
                # format the current time to a timetampe for mysql
                CURRENT_TIME = current_time.strftime(f) 
                # get the current time now.strftime(f) 

                context = json.dumps(id2context[each]) 
                
                # first: update the database for all recommendations  
                # this has to be made ealier than the second one, because there are the primary key 
                cursor.execute(query0,(user_id,each,CURRENT_TIME,context,time))

                # update the database for the past 7 days storage
                cursor.execute(query1,(user_id,each,CURRENT_TIME))
                
                # they have to use the same user_id,each, current_time because they are key and are referencing each other
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
                'distance':restaurant['distance'],
                'recommendation_time':CURRENT_TIME}
                output.append(restaurant_info)
                # the recommendation_time has to be returned and used for update the feedback 
                # this is part of the primary key

    return jsonify({"success":output})

def updateReward(user_profile,user_id,time,restaurant_id,recommendation_time,reward,alpha,conn):
    cursor = conn.cursor()

    query = "SELECT context FROM AllRecommendations where user_id = %s and restaurant_id = %s and recommendation_time = %s"
    cursor.execute(query, (user_id,restaurant_id,recommendation_time))
    a = cursor.fetchone()
    context = json.loads(a["context"])

    #store this feedback to UserRating
    query = "INSERT INTO UserRating(user_id,restaurant_id,recommendation_time,user_selection_time,reward) VALUES(%s,%s,%s,CURRENT_TIMESTAMP,%s)"
    cursor.execute(query, (user_id,restaurant_id,recommendation_time,reward))
    conn.commit()

    result = [reward,restaurant_id,context]

    A, b = getMatrices(user_profile,time)
    # A and b both have three matrices, one for morning, one for afternoon and one for evening
    # now, get the matrices according to time 
    # if there is no matrcies stored, then start  with None

    A, b, _ = linUCB(A, b, [result], [], alpha, len(context)) #it's learning 
    helperFunction.saveMatrices(user_profile,A, b, time)


if __name__ == "__main__":
     
    conn = pymysql.connect(host='localhost',
                        port = 8889,
                        user='root',
                        password='root',
                        db='UrbanConnector',
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)

    # Defaults
    DEFAULT_USER_ID = "1231241412" #get current time
    DEFAULT_TIME = time.strftime('%H:%M')  #get current time
    DEFAULT_LONGITUDE = -73.984345
    DEFAULT_LATITUDE = 40.693899
    DEFAULT_RADIUS = 1000 #meters
    DEFAULT_PRICE = 2 #means "$$". the program reads $$ as 3754, so need to use int to represent it
    alpha = 0.2

    CONTINUE = True

    while CONTINUE:
        output = makeRecommendation("senior",DEFAULT_USER_ID,DEFAULT_TIME,DEFAULT_LONGITUDE,DEFAULT_LATITUDE,DEFAULT_RADIUS,DEFAULT_PRICE,alpha,conn)
        print(output)
        answer = input("Please give your choice(END means to terminate the program):\n")

        if answer == "END":
            CONTINUE = False #end the program
        elif answer == "NONE":
            pass
        else:
            output = json.loads(output)
            recommendation_time = list(filter(lambda x:x["id"]==answer,output))[0]["recommendation_time"]
            updateReward("senior",DEFAULT_USER_ID,DEFAULT_TIME,answer,recommendation_time,1,alpha,conn) 
    
    conn.close()
    