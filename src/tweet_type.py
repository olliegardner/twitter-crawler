from enum import Enum


# Enum for type of Tweet
class TweetType(Enum):
    TWEET = 1
    RETWEET = 2
    QUOTE = 3