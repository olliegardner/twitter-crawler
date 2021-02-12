from dotenv import load_dotenv

import tweepy
import os


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

    user = api.get_user('POTUS')

    print(user.name)
    print(user.screen_name)
    print(user.followers_count)

    return True


if __name__ == '__main__':
    load_dotenv()

    if connect_to_twitter():
        print('success')