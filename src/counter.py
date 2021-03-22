from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
database = client['webscience']


def count_tweets(collection_name):
    # Get database collection from parameter
    collection = database[collection_name]

    print()
    print('Collection:', collection_name)
    print()

    # Count the retweets, quotes and normal Tweets
    tweets = collection.aggregate(
        [{
            '$group': {
                '_id': '$tweet_type',
                'count': {
                    '$sum': 1
                }
            }
        }]
    )

    # Print the values for each type of Tweet
    for tweet_type in list(tweets):
        print(tweet_type['_id'] + ': ' + str(tweet_type['count']))

    # Get total number of Tweets in that collection
    total_tweets = collection.count_documents(filter={})

    print('TOTAL:', total_tweets)
    print()

    # Count the number of verified users
    verified = collection.count_documents(filter={'verified': True})
    print('Verified:', verified)

    # Count the number of images, videos and gifs
    all_media = collection.aggregate(
        [
            {
                '$group':
                    {
                        '_id': '',
                        'images': {
                            '$sum': '$image_number'
                        },
                        'videos': {
                            '$sum': '$video_number'
                        },
                        'gifs': {
                            '$sum': '$gif_number'
                        }
                    }
            }
        ]
    )

    for media in list(all_media):
        print('Number of images:', media['images'])
        print('Number of videos:', media['videos'])
        print('Number of gifs:', media['gifs'])

    # Count number of geo enabled tweets
    geo_enabled = collection.count_documents(filter={'geoenabled': True})
    print('Geo tagged tweets:', geo_enabled)

    # Count the number of tweets with location or place objects
    locations_or_places = collection.count_documents(
        filter={
            "$or": [{
                'location': {
                    '$ne': None
                }
            }, {
                'place_name': {
                    '$ne': None
                }
            }]
        }
    )
    print('Locations or places:', locations_or_places)


def count_redundancies():
    streamer = database['hybridStreamer']
    rest = database['hybridRest']

    redundancies = 0

    # For each tweet in the hybridStreamer collection
    for tweet in streamer.find(filter={}):
        # Find the tweet in the hybridRest collection
        redundant = rest.find_one(filter={'_id': tweet['_id']})

        # If found, tweet is redundant so add 1 to count
        if redundant:
            redundancies += 1

    return redundancies


if __name__ == '__main__':
    count_tweets('streamer')
    count_tweets('hybridStreamer')
    count_tweets('hybridRest')

    print()
    print('Redundant:', count_redundancies())
    print()
