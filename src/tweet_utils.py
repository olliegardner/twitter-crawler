from tweet_type import TweetType

import datetime
import emoji
import os
import re
import wget


def strip_emojis(text):
    # Remove emojis from Tweet text
    clean_text = re.sub(emoji.get_emoji_regexp(), r"", text)
    clean_text.encode('ascii', errors='ignore').decode()

    return clean_text


def process_tweet(tweet, text_index):
    place_name, place_country, place_country_code, place_coords, tweet_media = None, None, None, None, None
    images, videos, gifs = 0, 0, 0

    try:
        text = tweet[text_index]  # Entire body of the Tweet
        user = tweet['user']  # User who tweeted
        entities = tweet['entities']

        # Convert data to format expected by MongoDB
        created = datetime.datetime.strptime(
            tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'
        )

        # Tweet is a quote tweet
        tweet_type = TweetType.QUOTE if tweet['is_quote_status'
                                             ] else TweetType.TWEET

        # If tweet has media files
        if 'media' in entities:
            tweet_media = entities['media']

        # Truncated tweet so get the full expanded text and media files
        if tweet['truncated']:
            if 'full_text' in tweet['extended_tweet']:
                text = tweet['extended_tweet']['full_text']

            if 'media' in tweet['extended_tweet']['entities']:
                tweet_media = tweet['extended_tweet']['entities']['media']
        elif text.startswith('RT'):
            # Tweet is a retweet as it begins with RT
            tweet_type = TweetType.RETWEET

            if tweet['retweeted_status']['truncated']:
                if 'full_text' in tweet['retweeted_status']['extended_tweet']:
                    text = tweet['retweeted_status']['extended_tweet'][
                        'full_text']
            else:
                if 'full_text' in tweet['retweeted_status']:
                    text = tweet['retweeted_status']['full_text']

        # Get all the mentions in the Tweet
        mentions = [
            mention['screen_name'] for mention in entities['user_mentions']
        ]

        # Get all the hashtags in the Tweet
        hashtags = [hashtag['text'] for hashtag in entities['hashtags']]

        # Get Tweet coordinates if it has any
        coordinates = tweet['coordinates']
        if coordinates:
            coordinates = coordinates['coordinates']

        # Retweets don't have locations
        if not text.startswith('RT'):
            # Get place object of Tweet
            if tweet['place']:
                place_name = tweet['place']['full_name']
                place_country = tweet['place']['country']
                place_country_code = tweet['place']['country_code']
                place_coords = tweet['place']['bounding_box']['coordinates']

        # Get number of images, videos and gifs stored in media folder
        number_stored_images = len(os.listdir('../media/images'))
        number_stored_videos = len(os.listdir('../media/videos'))
        number_stored_gifs = len(os.listdir('../media/gifs'))

        for media in tweet_media or []:
            if media['type'] == 'photo':
                # Only store 10 images
                if number_stored_images <= 10:
                    # Download the image to ../media/images
                    wget.download(media['media_url'], out='../media/images')

                images += 1
            elif media['type'] == 'video':
                if number_stored_videos <= 10:
                    # Download video to ../media/videos
                    wget.download(
                        media['video_info']['variants'][0]['url'],
                        out='../media/videos'
                    )

                videos += 1
            elif media['type'] == 'animated_gif':
                if number_stored_gifs <= 10:
                    wget.download(
                        media['video_info']['variants'][0]['url'],
                        out='../media/gifs'
                    )

                gifs += 1

        # Return Tweet in custom format, ready to store in MongoDB
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
            'gif_number': gifs,
            'tweet_type': tweet_type.name
        }

    except Exception as e:
        # Error with JSON so ignore this tweet
        print(e)
        return None
