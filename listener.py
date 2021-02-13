from pymongo import MongoClient
from tweet_utils import process_tweet

import tweepy
import json

client = MongoClient('localhost', 27017)  # connect to localhost MongoDB
database = client['webscience']  # create database called webscience
collection = database['tweets']  # create tweets collection


class StreamListener(tweepy.StreamListener):
    """
    class provided by tweepy to access the Twitter Streaming API.
    """
    def on_connect(self):
        # called initially to connect to the Streaming API
        print('Connected to the streaming API')

    def on_error(self, status_code):
        # if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False

    def on_data(self, data):
        # load the json data
        tweet = json.loads(data)

        processed_tweet = process_tweet(tweet)

        # print(processed_tweet)

        if processed_tweet:
            collection.insert_one(processed_tweet)
