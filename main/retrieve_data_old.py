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
from feature_selection import featureSelection
from linUCB import linUCB

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
API_KEY= config.api_key


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.


# Defaults
DEFAULT_TIME = time.strftime('%H:%M')  #get current time
DEFAULT_LONGITUDE = -73.984345
DEFAULT_LATITUDE = 40.693899
DEFAULT_RADIUS = 500 #meters
DEFAULT_PRICE = 2 #means "$$". the program reads $$ as 3754, so need to use int to represent it
DEFAULT_OFFSET = 0 #meters
SEARCH_LIMIT = 50
SORT_BY = "distance" # best_match, rating, review_count or distance

#Price
PRICE = {1:"1",2:"1, 2",3:"1, 2, 3",4:"1, 2, 3, 4"}

def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    start_time = time.time()
    response = requests.request('GET', url, headers=headers, params=url_params)
    end_time = time.time()
    print("time cost",end_time-start_time)

    return response.json()


def search(api_key, current_time, longitude,latitude, radius, price, offset):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
        longitude (decimal): decimal	Required if location is not provided. Longitude of the location you want to search nearby.
        latitude (decimal): decimal	Required if location is not provided. Latitude of the location you want to search nearby.
    Returns:
        dict: The JSON response from the request.
    """

    #############################################
    #decide term eg: breakfast, brunch, lunch, dinner
    if current_time <= "10:30":
        term = "breakfast brunch"
    elif current_time <= "14:00":
        term = "brunch lunch"
    else:
        term = "dinner"

    #############################################
    #filter price
    price = PRICE[price]

    url_params = {
        'term': term.replace(' ', '+'),
        'longitude': longitude,
        'latitude': latitude,
        "radius": radius,
        "open_now":True,
        "price": price,        
        'limit': SEARCH_LIMIT,
        "offset":offset,
        "sort_by":SORT_BY
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def get_business(api_key, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)


def query_api(current_time, longitude, latitude, radius, price):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
        longitude (decimal): decimal	Required if location is not provided. Longitude of the location you want to search nearby.
        latitude (decimal): decimal	Required if location is not provided. Latitude of the location you want to search nearby.
    """
    restaurants = []

    response = search(API_KEY, current_time, longitude, latitude, radius, price, DEFAULT_OFFSET)

    total = response.get("total")

    if total!=0:

        businesses = response.get('businesses')
        restaurants.extend(businesses)

        for num in range(SEARCH_LIMIT,total+1,SEARCH_LIMIT):
            response = search(API_KEY, current_time, longitude, latitude, radius, price, num)
            businesses = response.get('businesses')
            restaurants.extend(businesses)
    # print(restaurants)
    print("total",total,"\n")

    return restaurants
    ####################################################

    context_pool = featureSelection(restaurants)

    context_size = len(context_pool[0])-1-1 # remove reward and arm
    
    A, b, prediction = linUCB(None, None, [], context_pool, 0.01, context_size)



    output = []
    iteration = 0
    while iteration<3 and restaurants: #either find 3 restaurants or not enough qualified restaurants
        idx = random.randint(0,len(restaurants)-1)
        recommendation = {"name":restaurants[idx]["name"],'price':restaurants[idx]['price'],
        'review_count':restaurants[idx]['review_count'],
        'rating':restaurants[idx]['rating'],
        'categories':restaurants[idx]['categories'],
        'phone':restaurants[idx]['phone'],
        'display_phone':restaurants[idx]['display_phone'],
        'location':restaurants[idx]['location']['address1'],
        "coordinates":restaurants[idx]["coordinates"],
        'distance':restaurants[idx]['distance']}
        output.append(recommendation)
        print()
        restaurants.pop(idx)
        iteration+=1
    result = json.dumps(output)
    print(result)

            
    # print(businesses)

    # if not businesses:
    #     print(u'No businesses for {0} in [{1},{2}] found.'.format(term,longitude, latitude))
    #     return

    # business_id = businesses[0]['id']

    # print(u'{0} businesses found, querying business info ' \
    #     'for the top result "{1}" ...'.format(
    #         len(businesses), business_id))
    # response = get_business(API_KEY, business_id)

    # print(u'Result for business "{0}" found:'.format(business_id))
    # pprint.pprint(response, indent=2)


def get_data():
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--time', dest='current_time', default=DEFAULT_TIME,
                        type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-long', '--longitude', dest='longitude',
                        default=DEFAULT_LONGITUDE, type=float,
                        help='Search longtitude (default: %(default)s)')
    parser.add_argument('-lat', '--latitude', dest='latitude',
                        default=DEFAULT_LATITUDE, type=float,
                        help='Search latitude (default: %(default)s)')
    parser.add_argument('-r', '--radius', dest='radius',
                        default=DEFAULT_RADIUS, type=int,
                        help='Search radius (default: %(default)s)')
    parser.add_argument('-p', '--price', dest='price',
                        default=DEFAULT_PRICE, type=int,
                        help='Search price (default: %(default)s)')
    input_values = parser.parse_args()

    try:
        query_api(input_values.current_time, input_values.longitude, input_values.latitude, input_values.radius, input_values.price )
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )


if __name__ == '__main__':
    main()
