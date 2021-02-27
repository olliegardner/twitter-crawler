from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pymongo import MongoClient
from threading import Thread
from tweet_utils import process_tweet

import datetime
import json
import os
import tweepy

# UK and Ireland locations
locations = [-10.392627, 49.681847, 1.055039, 61.122019]

# Track words to do with 6 nations rugby
track_words = [
    'Rugby', '6 Nations', 'Six Nations', 'Guinness Six Nations',
    'Guinness 6 Nations', 'Murrayfield', 'BT Murrayfield', 'Twickenham',
    'Principality Stadium', 'Aviva Stadium', 'Stade de France',
    'Stadio Olimpico', 'Stuart Hogg', 'Finn Russell', 'Wayne Barnes', 'Scrum',
    'Try', 'Penalty', 'Drop goal', 'Doddie Weird Cup', 'Scotland', 'Ireland',
    'Wales', 'England', 'France', 'Italy'
]

executor = ThreadPoolExecutor()


class StreamListener(tweepy.StreamListener):
    """
    Class provided by tweepy to access the Twitter Streaming API.
    """
    def __init__(self):
        self.running = True

        self.api = tweepy.API(
            auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True
        )

        client = MongoClient('localhost', 27017)  # Connect to localhost MongoDB
        database = client['webscience']  # Create database called webscience
        self.collection = database['tweets']  # Create tweets collection

        executor.submit(self.run_for_one_hour)

    def run_for_one_hour(self):
        start = datetime.datetime.now()
        end = start + datetime.timedelta(hours=1)

        print('Twitter crawler will run until ' + str(end))

        while True:
            if datetime.datetime.now() >= end:
                self.running = False
                print('Twitter crawler 1 hour duraction over.')
                return False

    def on_connect(self):
        # Called initially to connect to the Streaming API
        print('Connected to the Twitter streaming API.')

    def on_error(self, status_code):
        # If an error occurs, display the status code
        print('An error has occured: ' + repr(status_code))
        return False

    def on_data(self, data):
        try:
            # Load the json data
            tweet = json.loads(data)

            processed_tweet = process_tweet(tweet)

            if processed_tweet:
                self.collection.insert_one(processed_tweet)
        except KeyboardInterrupt:
            return False

        return self.running


if __name__ == '__main__':
    load_dotenv()

    auth = tweepy.OAuthHandler(
        os.getenv('CONSUMER_KEY'), os.getenv('CONSUMER_SECRET')
    )
    auth.set_access_token(
        os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET')
    )

    try:
        listener = StreamListener()

        stream = tweepy.Stream(
            auth=auth, listener=listener, tweet_mode='extended'
        )
        stream.filter(
            locations=locations,
            track=track_words,
            languages=['en'],
            is_async=True
        )
    except KeyboardInterrupt:
        print('Stopping Twitter crawler. Please wait...')
