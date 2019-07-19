from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import main

app = Flask(__name__)
app.secret_key = '2y14ZhoB0P'


@app.route('/')
def default():
    return "Urban Connector"


@app.route('/getRecommendation:<user_id>+<time>+<longitude>+<latitude>+<radius>+<price>')
def getRecommendation(user_id,time,longitude,latitude,radius,price):
    longitude = float(longitude)
    latitude = float(latitude)
    radius = float(radius)
    price = int(price)
    return main.makeRecommendation(user_id,time,longitude,latitude,radius,price)

@app.route('/feedback:<user_id>+<time>+<restaurant_id>+<reward>')
def feedback(user_id,time,restaurant_id,reward):
    reward = int(reward)
    main.updateReward(user_id,time,restaurant_id,reward)

if __name__ == "__main__":
    app.run('127.0.0.1', 8000, debug = True)
