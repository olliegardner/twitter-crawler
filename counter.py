from pymongo import MongoClient


def count_tweets():
    client = MongoClient('localhost', 27017)
    database = client['webscience']
    collection = database['tweets']

    total_tweets = collection.count_documents(filter={})

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

    for tweet_type in list(tweets):
        print(tweet_type['_id'] + ': ' + str(tweet_type['count']))

    print('TOTAL: ' + str(total_tweets))


if __name__ == '__main__':
    count_tweets()