from dotenv import load_dotenv
from listener import StreamListener
from pymongo import MongoClient

import tweepy
import os
import time


def connect_to_twitter():
    consumer_key = os.getenv('CONSUMER_KEY')
    consumer_secret = os.getenv('CONSUMER_SECRET')
    access_token = os.getenv('ACCESS_TOKEN')
    access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    if not api:
        print('Twitter authenitcation failed.')
        return False

    return auth, api


def connect_to_mongodb():
    client = MongoClient('localhost', 27017)  # connect to localhost MongoDB
    database = client['webscience']  # create database called webscience
    collection = database['tweets']  # create tweets collection
    collection.insert_one({"x": 11})  # insert test data


def create_stream(auth, api):
    locations = [-10.392627, 49.681847, 1.055039, 61.122019]  # UK and Ireland

    words = [
        'Rugby', '6 Nations', 'Six Nations', 'Guinness Six Nations',
        'Guinness 6 Nations', 'Murrayfield', 'BT Murrayfield', 'Twickenham',
        'Principality Stadium', 'Aviva Stadium', 'Stade de France',
        'Stadio Olimpico', 'Stuart Hogg', 'Finn Russell', 'Wayne Barnes',
        'Scrum', 'Try', 'Penalty', 'Drop goal', 'Doddie Weird Cup', 'Scotland',
        'Ireland', 'Wales', 'England', 'France', 'Italy'
    ]

    listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
    streamer = tweepy.Stream(auth=auth, listener=listener)
    streamer.filter(
        locations=locations, track=words, languages=['en'], is_async=True
    )

    results = True
    counter = 0
    geo_code = '55.8554403,-4.3024977,50km'  # Glasgow geo code with 50km radius

    while results:
        if counter < 180:  # number of requests allowed for Twitter
            try:
                results = api.search(
                    geocode=geo_code, count=100, lang="en", max_id=None
                )
            except Exception as e:
                print(e)

            counter += 1
        else:
            # sleep for 15 minutes to meet Twitter rate limit
            time.sleep(15 * 60)


if __name__ == '__main__':
    load_dotenv()

    auth, api = connect_to_twitter()

    if auth:
        connect_to_mongodb()
        create_stream(auth, api)
