from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from threading import Thread
from tweet_utils import process_tweet

import datetime
import json
import os
import sys
import time
import tweepy

# UK and Ireland locations
locations = [-10.392627, 49.681847, 1.055039, 61.122019]

# Track words from clustering
track_words = [
    'ireland', 'ireveng', 'england', 'guinnesssixnations', 'penalty',
    'sixnationsrugby', 'teamofus', 'shouldertoshoulder', 'game', 'half'
]

# Connect to local MongoDB, get database and collections
client = MongoClient('localhost', 27017)
database = client['webscience']
hybrid_rest = database['hybridRest']
hybrid_streamer = database['hybridStreamer']

# Variable tracks whether the script is running or not
running = True

executor = ThreadPoolExecutor()


class StreamListener(tweepy.StreamListener):
    """
    Class provided by Tweepy to access the Twitter Streaming API.
    """
    def on_connect(self):
        # Called initially to connect to the Streaming API
        print('Connected to the Twitter streaming API.')

    def on_error(self, status_code):
        # If an error occurs, display the status code
        print('An error has occured: ' + repr(status_code))
        return False

    def on_data(self, data):
        global running

        try:
            # Load the json data
            tweet = json.loads(data)
            # Convert the Tweet to the desired format
            processed_tweet = process_tweet(tweet, 'text')

            # If Tweet isn't none
            if processed_tweet and running:
                # Add to MongoDB
                hybrid_streamer.insert_one(processed_tweet)
        except KeyboardInterrupt:
            # Cancel script if keyboard interrupt
            return False

        return running


def rest_api(api):
    counter = 0
    results = True
    global running

    while results and running:
        # Used to handle Twitter REST API restrictions
        if counter < 180:
            try:
                # Search for Tweets using REST API with keywords from clustering and UK geo filter
                results = api.search(
                    q=' OR '.join(track_words),
                    geocode='51.450798,-0.137842,10km',
                    count=100,
                    lang='en',
                    tweet_mode='extended'
                )

                # For each Tweet in the result
                for tweet in results:
                    # Load Tweet from the json
                    tweet = json.loads(json.dumps(tweet._json))
                    # Convert Tweet to desired format
                    processed_tweet = process_tweet(tweet, 'full_text')

                    if processed_tweet and running:
                        try:
                            # Insert Tweet into MongoDB
                            hybrid_rest.insert_one(processed_tweet)
                        except DuplicateKeyError:
                            continue
            except Exception as e:
                print(e)

            counter += 1
        else:
            # Crawler sleep for 15 minutes to meet Twitter restrictions
            time.sleep(15 * 60)


def run_for_one_hour():
    # Get time 1 hour from runtime
    start = datetime.datetime.now()
    end = start + datetime.timedelta(hours=1)
    global running

    print('Twitter hybrid crawler will run until ' + str(end))

    while True:
        if datetime.datetime.now() >= end:
            # 1 hour has ended, set script to no longer running
            running = False

            try:
                # Exit the program
                sys.exit()
            except SystemExit:
                print('Twitter crawler finished scraping.')

            return False


if __name__ == '__main__':
    # Load Twitter API keys from .env file
    load_dotenv()

    auth = tweepy.OAuthHandler(
        os.getenv('CONSUMER_KEY'), os.getenv('CONSUMER_SECRET')
    )
    auth.set_access_token(
        os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET')
    )

    # Access REST API with Twitter credentials
    api = tweepy.API(
        auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True
    )

    # Execute in new thread
    executor.submit(run_for_one_hour)

    try:
        # Call the Streaming API
        listener = StreamListener()

        stream = tweepy.Stream(
            auth=auth, listener=listener, tweet_mode='extended'
        )
        # Filter the stream based on track words and UK location
        stream.filter(
            locations=locations,
            track=track_words,
            languages=['en'],
            is_async=True
        )

        # Call the REST API
        rest_api(api)
    except KeyboardInterrupt:
        print('Stopping hybrid Twitter crawler. Please wait...')
