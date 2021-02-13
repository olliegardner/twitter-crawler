import tweepy
import json


class StreamListener(tweepy.StreamListener):
    """
    Class provided by tweepy to access the Twitter Streaming API.
    """
    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("Connected to the streaming API")

    def on_error(self, status_code):
        # If an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False

    def on_data(self, data):
        # Load the json data
        t = json.loads(data)
        print(t)
