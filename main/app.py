from flask import Flask, render_template, request, session, url_for, redirect,make_response,jsonify
import pymysql.cursors
import main
import json
from flask_cors import CORS,cross_origin

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = '2y14ZhoB0P'


conn = pymysql.connect(host='localhost',
                    port = 8889,
                    user='root',
                    password='root',
                    db='UrbanConnectorTest',
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor)

__ALPHA__ = 2
@app.route('/')
def default():
    return "Urban Connector"


@app.route('/getRecommendation:<user_id>+<time>+<longitude>+<latitude>+<radius>+<price>', methods=['GET'])
def getRecommendation(user_id,time,longitude,latitude,radius,price):
    longitude = float(longitude)
    latitude = float(latitude)
    radius = int(radius)
    price = int(price)
    return main.makeRecommendation(user_id,time,longitude,latitude,radius,price,__ALPHA__,conn)

@app.route('/feedback:<user_id>+<time>+<restaurant_id>+<reward>',methods=['GET'])
def feedback(user_id,time,restaurant_id,reward):
    reward = int(reward)
    main.updateReward(user_id,time,restaurant_id,reward,__ALPHA__,conn)
    response = make_response(jsonify({"statusCode": 200}))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'

    return response

if __name__ == "__main__":
    app.run('127.0.0.1', 8000, debug = True)
