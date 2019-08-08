### 1. Notice:

1. please keep of positive word array in "preprocessing/pca_model_training.ipynb","preprocessing/data_stimulation.ipynb/" consistent

### 2. Configuration file:

1. please create one python file under main folder `main/config.py` with Yelp API information([Yelp Fusion API](https://www.yelp.com/developers/documentation/v3))

```
api_key = <your api key>
client_id = <your client id>
app_name = <the name of your app>
```
2. remove all current data files under `main/model/`(they will be generated again)

### 3. Database Setup:

1. create a database called `UrbanConnector` in MySQL

2. import file `/database/database_setup.sql` to create three tables:`AllRecommendations`,`RecommendationsSevenDays`,`UserRating`

3. change database setting and connect to database: 

	A. If you want to run this individual file and test the program with terminal, then modify the corresponding part in [main/main.py](https://github.com/Alicia1529/Recommender-system-development-and-deployment-for-elderly-mobility-in-NYC/blob/12fa12d4ec46f4045517532d894e3ae1a49e2240/main/main.py#L280-L287) 
	
	B. To change the database of the webservice, modify [main/app.py](https://github.com/Alicia1529/Recommender-system-development-and-deployment-for-elderly-mobility-in-NYC/blob/12fa12d4ec46f4045517532d894e3ae1a49e2240/main/app.py#L18-L24)

	
4. (Optional)Test if the database is set up correctly(all modifications to the database):
	
	1. [update the RecommendationsSevenDays table](https://github.com/Alicia1529/Recommender-system-development-and-deployment-for-elderly-mobility-in-NYC/blob/12fa12d4ec46f4045517532d894e3ae1a49e2240/main/main.py#L90-L94)
	
		test: `DELETE FROM RecommendationsSevenDays WHERE recommendation_time < (NOW() - INTERVAL 7 DAY)`

	2. [query recommendations for this user in the past 7 days](https://github.com/Alicia1529/Recommender-system-development-and-deployment-for-elderly-mobility-in-NYC/blob/12fa12d4ec46f4045517532d894e3ae1a49e2240/main/main.py#L103-L105)

	3. make recommendations and update both AllRecommendations RecommendationsSevenDays 
	[query](https://github.com/Alicia1529/Recommender-system-development-and-deployment-for-elderly-mobility-in-NYC/blob/12fa12d4ec46f4045517532d894e3ae1a49e2240/main/main.py#L149-L150)
	[execution1](https://github.com/Alicia1529/Recommender-system-development-and-deployment-for-elderly-mobility-in-NYC/blob/12fa12d4ec46f4045517532d894e3ae1a49e2240/main/main.py#L165-L175)
	[execution2](https://github.com/Alicia1529/Recommender-system-development-and-deployment-for-elderly-mobility-in-NYC/blob/12fa12d4ec46f4045517532d894e3ae1a49e2240/main/main.py#L212-L222)
		```
		#notice that context is in json format
		INSERT INTO `AllRecommendations`(`user_id`, `restaurant_id`, `recommendation_time`,`context`,`local_time`) VALUES (1231241412,brLV35q22JnxSekUm1Wt8A,2019-08-08 00:45:00,[1370.3069959094935, 3.5, 156, 1, 0.3678531037837738, 0.0245118791941913, 0.2884336991225436, -0.05679204451798186, 0.6186320352542078, 0.04952941385891926, 0.9322101108964919, -0.08197835826599327, 0.172544659806304, -0.2907603034548553, 0.052044121638843165, 0.36213477381726544, 0.02664460900300173, -0.12316523118316319, -0.04440593093193514, -0.12558986115695092, -0.026363099056166482, 0.06656524824647395, 0.0036090332773570824, -0.048723771666322656, -0.021830542997385245, -0.016607904142542648, 0.0175328386382096, 0.010678038991785925, 0.00031283715293467003, -0.015936172591742823, -0.007663354654449245, 0.006364743050601441, -0.018076355316729666, 0.013047002112322082, 0.0031238381114750296, 0.0012586542667849707, -0.004989686603965165, 0.019779303407707022, -0.004699269738667344, -0.012336437534250358, 0.008833647420428102, -0.001540721732683503, 0.003366412234424986, 0.019760043150998323, 0.006335963334146817, 0.00010389827537397681, -0.001825597229205127, 0.005353118672087066, 0.00468141683544218, 0.007346067350638506, 0.007177251878558236, -0.0013478173909830557, 0.00952805237548515, -0.0061604682930519765],2019-08-08T00:44:58-04:00);
		```

		INSERT INTO `RecommendationsSevenDays`(user_id, restaurant_id, recommendation_time) VALUES (1231241412,brLV35q22JnxSekUm1Wt8A,2019-08-08 00:45:00)

	4. [update user profile according to the response](https://github.com/Alicia1529/Recommender-system-development-and-deployment-for-elderly-mobility-in-NYC/blob/12fa12d4ec46f4045517532d894e3ae1a49e2240/main/main.py#L248-L256)

```
INSERT INTO UserRating(user_id,restaurant_id,recommendation_time,user_selection_time,reward) VALUES(1231241412,brLV35q22JnxSekUm1Wt8A,2019-08-08 00:45:00,CURRENT_TIMESTAMP,1.0)
```

### 4. Preprocessing:

1. get_restaurant_data.py: get around 50K restaurant records from Yelp API to train PCA model and for offline evaluation.

	output: /data/restaurants_information/...(12 files)

2. pca_model_training.py: convert text data(restaurant info) to feature matrix and train PCA model to 54-dimension. 

	output: /main/pca_model.sav

3. offline_evaluation_data_simulation.ipynb: generated synthetic data (food preference) to test the algorithm, but much of the part is similar to pca_model_training program.

	output: /data/simulated_arm_contexts.pyc 
		
### 5. Main:

1. yelDataCollection.py: make request to Yelp API and retrieve candidate restaurants information.
(multithreading to increase the speed)

run it directlly will give you some restaurants that satisfy your setting

2. featureExtraction.py: convert the text data to feature matrix.

3. linUCB.py: main recommendation algorithm using contextual bandit algorithm
you can run it directly to see the result of an offline evaluation

4. main.py: main functions to implement the recommendation algorithm, like get and save matrices, make recommendations and update the result.

5. app.py: web framework

	
### 6. Two main services:

1. get recommendations -> return three restaurants(sometimes less than 3 because this are not enough restaurants)

```
@app.route('/getRecommendation:<user_profile>+<user_id>+<local_time>+<longitude>+<latitude>+<radius>+<price>', methods=['GET'])
def getRecommendation(user_profile, user_id, time, longitude, latitude, radius, price):
# user_profile: string, eg: 'senior'
# user_id: string, eg:'123124'
# local_time: string-UTC timezone and ISO format, eg: '2019-08-07T23:44:16-04:00' (strict format)
# longitude: string, eg: '-73.984345'
# latitude: string, eg: '40.693899'
# radius(meters): string, eg: '1000' -> later to int 
# price: string, eg: '1','2','3','4'   ->later to int
```

sample request:
```
"GET /getRecommendation:senior+1231241412+2019-08-07T23:44:16-04:00+-73.984345+40.693899+2000+1 HTTP/1.1" 200 -
```
sample response:
```
1. success: retrieve three restaurants(sometimes is there is not enough restaurants, maybe only 1 or 2)
Response {type: "cors", url: "http://localhost:8000/getRecommendation:senior+1231241412+12:06+-73.984345+40.693899+500+1", redirected: false, status: 200, ok: true, …}
bodyUsed: true
headers: Headers {}
ok: true
redirected: false
status: 200
statusText: "OK"
type: "cors"
url: "http://localhost:8000/getRecommendation:senior+1231241412+12:06+-73.984345+40.693899+500+1"
body:{
    "success": [
      {
        "categories": [
          {
            "alias": "sandwiches", 
            "title": "Sandwiches"
          }, 
          {
            "alias": "desserts", 
            "title": "Desserts"
          }
        ], 
        "coordinates": {
          "latitude": 40.7158, 
          "longitude": -73.99169
        }, 
        "display_phone": "(646) 504-8132", 
        "distance": 2502.9117980819724, 
        "id": "gHdejB1Mx2P5UjAgZ6BT2w", 
        "location": "35 Orchard St", 
        "name": "Cheeky Sandwiches", 
        "phone": "+16465048132", 
        "price": "$", 
        "rating": 4.5, 
        "recommendation_time": "2019-08-07 12:08:15", 
        "review_count": 1118
      }, 
      {
        "categories": [
          {
            "alias": "falafel", 
            "title": "Falafel"
          }, 
          {
            "alias": "egyptian", 
            "title": "Egyptian"
          }, 
          {
            "alias": "sandwiches", 
            "title": "Sandwiches"
          }
        ], 
        "coordinates": {
          "latitude": 40.670295715332, 
          "longitude": -73.9790954589844
        }, 
        "display_phone": "(718) 768-4961", 
        "distance": 2661.7532896052808, 
        "id": "QZcRSVUltJ6YreTeDx52lQ", 
        "location": "226 7th Ave", 
        "name": "Mr Falafel", 
        "phone": "+17187684961", 
        "price": "$", 
        "rating": 4.0, 
        "recommendation_time": "2019-08-07 12:08:15", 
        "review_count": 184
      }, 
      {
        "categories": [
          {
            "alias": "chinese", 
            "title": "Chinese"
          }, 
          {
            "alias": "hkcafe", 
            "title": "Hong Kong Style Cafe"
          }
        ], 
        "coordinates": {
          "latitude": 40.71725, 
          "longitude": -73.99254
        }, 
        "display_phone": "(212) 966-8269", 
        "distance": 2687.6984035164082, 
        "id": "agCuWjaUJ8xBO_PDDQRiGw", 
        "location": "85 Eldridge St Lower E", 
        "name": "S Wan Cafe \u6d0b\u7d2b\u8346", 
        "phone": "+12129668269", 
        "price": "$", 
        "rating": 4.5, 
        "recommendation_time": "2019-08-07 12:08:15", 
        "review_count": 117
      }
    ]
  }
  
2.error: because the distance or price restriction is too tight, none of the restaurants satisfy the requirement
Response {type: "cors", url: "http://localhost:8000/getRecommendation:senior+1231241412+12:08+-73.984345+40.693899+1+1", redirected: false, status: 200, ok: true, …}
body: (...)
bodyUsed: true
headers: Headers {}
ok: true
redirected: false
status: 200
statusText: "OK"
type: "cors"
url: "http://localhost:8000/getRecommendation:senior+1231241412+12:08+-73.984345+40.693899+1+1"
body:{
"error": "please relax restrictions of radius or price prference"
}

3.error: because there are no qualified destinations
Response {type: "cors", url: "http://localhost:8000/getRecommendation:senior+1231241412+12:08+-73.984345+40.693899+1+1", redirected: false, status: 200, ok: true, …}
body: (...)
bodyUsed: true
headers: Headers {}
ok: true
redirected: false
status: 200
statusText: "OK"
type: "cors"
url: "http://localhost:8000/getRecommendation:senior+1231241412+12:08+-73.984345+40.693899+1+1"
body:{
"error": "no qualified destinations"
}

4.otherwise error
```


2. send users' feedback about the recommended restaurants

```
@app.route('/feedback:<user_profile>+<user_id>+<local_time>+<restaurant_id>+<recommendation_time>+<reward>',methods=['GET'])
def feedback(user_profile, user_id, local_time, restaurant_id, recommendation_time, reward):
# user_profile: string, eg: 'senior'
# user_id: string, eg:'123124'
# local_time: string-UTC timezone and ISO format, eg: '2019-08-07T23:44:16-04:00' (strict format)
# restaurant_id: string, eg: 'B0R-buSLWRbGFWpmqk_WZQ'
# recommendation_time: string, eg: '2019-08-07 2023:44:19+1', but in the request it replace empty space with %
# reward: string, eg: '-0.1','0','1' -> later to float
```


sample request:
```
"GET /feedback:senior+1231241412+2019-08-07T23:48:57-04:00+B0R-buSLWRbGFWpmqk_WZQ+2019-08-07%2023:44:19+1 HTTP/1.1" 200 -

"GET /feedback:senior+1231241412+2019-08-07T23:48:58-04:00+B0R-buSLWRbGFWpmqk_WZQ+2019-08-07%2023:44:19+-0.1 HTTP/1.1" 200 -
```
sample response:

```
1.success 200
Response {type: "cors", url: "http://localhost:8000/feedback:senior+1231241412+2…00+lQ7H-COT5duZQQ0XqGFPDg+2019-08-08%2000:06:16+1", redirected: false, status: 200, ok: true, …}
body: ReadableStream
locked: false
__proto__: ReadableStream
bodyUsed: false
headers: Headers {}
ok: true
redirected: false
status: 200
statusText: "OK"
type: "cors"
url: "http://localhost:8000/feedback:senior+1231241412+2019-08-08T00:07:31-04:00+lQ7H-COT5duZQQ0XqGFPDg+2019-08-08%2000:06:16+1"
__proto__: Response

2.error  500 
 printed line: "Try to insert a record, but doesn't conform to the foreign key policy"
```

### 7. Others:
To install the dependencies, run: `pip install -r requirements.txt`

To start the web services, run under main folder `python app.py`
