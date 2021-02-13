import re
import emoji


def strip_emojis(text):
    clean_text = re.sub(emoji.get_emoji_regexp(), r"", text)
    clean_text.encode('ascii', errors='ignore').decode()

    return clean_text


def process_tweet(tweet):
    place_name, place_country, place_country_code, place_coords = None, None, None, None

    try:
        text = tweet['text']  # entire body of the Tweet

        if tweet['truncated']:
            text = tweet['extended_tweet']['full_text']
        elif text.startswith('RT'):
            if tweet['retweeted_status']['truncated']:
                text = tweet['retweeted_status']['extended_tweet']['full_text']
            else:
                text = tweet['retweeted_status']['full_text']

        text = strip_emojis(text)

        entities = tweet['entities']

        mentions = [
            mention['screen_name'] for mention in entities['user_mentions']
        ]

        hashtags = [hashtag['text'] for hashtag in entities['hashtags']]

        coordinates = tweet['coordinates']
        if coordinates:
            coordinates = coordinates['coordinates']

        if not text.startswith('RT'):
            if tweet['place']:
                place_name = tweet['place']['full_name']
                place_country = tweet['place']['country']
                place_country_code = tweet['place']['country_code']
                place_coords = tweet['place']['bounding_box']['coordinates']

        return {
            'id': tweet['id_str'],
            'date': tweet['created_at'],
            'username': tweet['user']['screen_name'],
            'text': text,
            'geoenabled': tweet['user']['geo_enabled'],
            'coordinates': coordinates,
            'location': tweet['user']['location'],
            'place_name': place_name,
            'place_country': place_country,
            'country_code': place_country_code,
            'place_coordinates': place_coords,
            'mentions': mentions,
            'hashtags': hashtags,
            'source': tweet['source']
        }

    except Exception as e:
        # error with JSON so ignore this tweet
        return None
