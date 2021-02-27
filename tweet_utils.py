import re
import emoji
import datetime

from tweet_type import TweetType


def strip_emojis(text):
    clean_text = re.sub(emoji.get_emoji_regexp(), r"", text)
    clean_text.encode('ascii', errors='ignore').decode()

    return clean_text


def process_tweet(tweet):
    place_name, place_country, place_country_code, place_coords, tweet_media = None, None, None, None, None
    images, videos = 0, 0

    try:
        text = tweet['text']  # entire body of the Tweet
        user = tweet['user']
        entities = tweet['entities']

        created = datetime.datetime.strptime(
            tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'
        )

        tweet_type = TweetType.QUOTE if tweet['is_quote_status'
                                             ] else TweetType.TWEET

        if 'media' in entities:
            tweet_media = entities['media']

        if tweet['truncated']:
            if 'full_text' in tweet['extended_tweet']:
                text = tweet['extended_tweet']['full_text']

            if 'media' in tweet['extended_tweet']['entities']:
                tweet_media = tweet['extended_tweet']['entities']['media']
        elif text.startswith('RT'):
            tweet_type = TweetType.RETWEET

            if tweet['retweeted_status']['truncated']:
                if 'full_text' in tweet['retweeted_status']['extended_tweet']:
                    text = tweet['retweeted_status']['extended_tweet'][
                        'full_text']
            else:
                if 'full_text' in tweet['retweeted_status']:
                    text = tweet['retweeted_status']['full_text']

        mentions = [
            mention['screen_name'] for mention in entities['user_mentions']
        ]

        hashtags = [hashtag['text'] for hashtag in entities['hashtags']]

        coordinates = tweet['coordinates']
        if coordinates:
            coordinates = coordinates['coordinates']

        # Can't get location of a retweet
        if not text.startswith('RT'):
            if tweet['place']:
                place_name = tweet['place']['full_name']
                place_country = tweet['place']['country']
                place_country_code = tweet['place']['country_code']
                place_coords = tweet['place']['bounding_box']['coordinates']

        for media in tweet_media or []:
            if media['type'] == 'photo':
                images += 1
            elif media['type'] == 'video':
                videos += 1

        return {
            '_id': tweet['id_str'],
            'created': created,
            'username': user['screen_name'],
            'text': strip_emojis(text),
            'geoenabled': user['geo_enabled'],
            'coordinates': coordinates,
            'location': user['location'],
            'place_name': place_name,
            'place_country': place_country,
            'country_code': place_country_code,
            'place_coordinates': place_coords,
            'mentions': mentions,
            'hashtags': hashtags,
            'source': tweet['source'],
            'verified': user['verified'],
            'image_number': images,
            'video_number': videos,
            'tweet_type': tweet_type.name
        }

    except Exception as e:
        # Error with JSON so ignore this tweet
        print(e)
        return None
