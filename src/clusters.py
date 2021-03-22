from pymongo import MongoClient
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

import pandas as pd
import numpy as np

# Connect to local MongoDB
client = MongoClient('localhost', 27017)
database = client['webscience']
collection = database['streamer']

# Number of groups to create
n_clusters = 25


def cluster_tweets():
    # Get all Tweets from database collection
    all_tweets = collection.find(filter={})

    # Load Tweets into pandas DataFrame
    df = pd.DataFrame(all_tweets)

    # Create Tweet vectors, removing stop words
    vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
    tweet_vectors = vectorizer.fit_transform(df['text'])

    # Cluster Tweets using KMeans
    k_means = KMeans(n_clusters=n_clusters, random_state=0)
    clusters = k_means.fit_predict(tweet_vectors)
    # Add cluster to DataFrame
    df['cluster'] = clusters

    return df, vectorizer, tweet_vectors, clusters


def get_cluster_size(df):
    cluster_df, cluster_sizes = [], []

    # Append to list of clustered dataframes
    for i in range(n_clusters):
        cluster_df.append(df[df['cluster'] == i])

    # Get list of cluster sizes
    for cluster in cluster_df:
        cluster_sizes.append(len(cluster.index))

    # Get the average, min and max size of the clusters
    avg_size = np.mean(cluster_sizes)
    min_size = np.min(cluster_sizes)
    max_size = np.max(cluster_sizes)

    return avg_size, min_size, max_size


def get_cluster_keywords(vectorizer, tweet_vectors, clusters):
    # Calculate the mean of each cluster
    text_df = pd.DataFrame(tweet_vectors.todense()).groupby(clusters).mean()

    # Get the keywords from each vector
    feature_names = vectorizer.get_feature_names()

    # Iterate through clusters and print keywords
    for index, series in text_df.iterrows():
        keywords = [feature_names[i] for i in np.argsort(series)]

        # Filter our rt and https from keywords
        keywords = list(
            filter(
                lambda word: not word == 'rt' and not word == 'https', keywords
            )
        )

        print('Cluster ' + str(index + 1) + ': ' + str(keywords[-10:][::-1]))


if __name__ == '__main__':
    df, vectorizer, tweet_vectors, clusters = cluster_tweets()

    get_cluster_keywords(vectorizer, tweet_vectors, clusters)

    avg_size, min_size, max_size = get_cluster_size(df)

    print()
    print('Average cluster size:', avg_size)
    print('Min cluster size:', min_size)
    print('Max cluster size:', max_size)
    print()
