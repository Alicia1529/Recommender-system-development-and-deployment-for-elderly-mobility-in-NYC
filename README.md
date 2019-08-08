### Notice:

1. please keep of positive word array in "preprocessing/pca_model_training.ipynb","preprocessing/data_stimulation.ipynb/" consistent


### Database Setup:

1. create a database called `UrbanConnector` in MySQL

2. import file "/database/database_setup.sql" to create two tables

3. change the database setting in the following files to your own database:

	A. main/app.py line11-17

	B. main/main.py line 171-180 if you want to run this individual file and test the program with terminal


### Preprocessing:

1. get_restaurant_data.py: get around 5w restaurant records from Yelp API to train PCA model and for offline evaluation

	output: /data/restaurants_information/...(12 files)

2. pca_model_training.py: convert text data(restaurant info) to feature matrix and train PCA model to reduce the dimension to 

	output: /main/pca_model.sav (but now it's moved to /main folder)

3. offline_evaluation_data_simulation.ipynb: generated synthetic data (food preference) to test the algorithm, but much of the part is similar to pca_model_training program

	output: /simulated_arm_contexts.pyc (but now it's moved to /data folder)
		
### Main:

1. yelDataCollection.py: used to make request to Yelp API and retrieve candidate restaurants information.
(multithreading to increase the speed)

run it directlly will give you some restaurants that satisfy your setting

2. featureExtraction.py: convert the text data to feature matrix.

3. linUCB.py: main recommendation algorithm using contextual bandit algorithm
you can run it directly to see the result of an offline evaluation

4. main.py: main functions to implement the recommendation algorithm, like get and save matrices, make recommendations and update the result.

5. app.py: web framework

	
### Two main services:

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
"GET /getRecommendation:senior+1231241412+2019-08-07T23:44:16-04:00+-73.984345+40.693899+2000+1 HTTP/1.1" 200 -


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

"GET /feedback:senior+1231241412+2019-08-07T23:48:57-04:00+B0R-buSLWRbGFWpmqk_WZQ+2019-08-07%2023:44:19+1 HTTP/1.1" 200 -

"GET /feedback:senior+1231241412+2019-08-07T23:48:58-04:00+B0R-buSLWRbGFWpmqk_WZQ+2019-08-07%2023:44:19+-0.1 HTTP/1.1" 200 -


To install the dependencies, run: `pip install -r requirements.txt`

To start the web services, run under main folder `python app.py`
