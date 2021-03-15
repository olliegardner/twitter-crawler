from pymongo import MongoClient
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

import pandas as pd
import numpy as np

n_clusters = 25


def cluster_tweets():
    client = MongoClient('localhost', 27017)
    database = client['webscience']
    collection = database['tweets']

    # TODO: remove limit of 2000
    all_tweets = collection.find(filter={}).limit(2000)

    df = pd.DataFrame(all_tweets)

    # Create Tweet vectors, removing stop words
    vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
    tweet_vectors = vectorizer.fit_transform(df['text'])

    k_means = KMeans(n_clusters=n_clusters, random_state=0)
    clusters = k_means.fit_predict(tweet_vectors)
    df['cluster'] = clusters

    return df, vectorizer, tweet_vectors, clusters


def get_cluster_size(df):
    cluster_df = []

    # Append to list of clustered dataframes
    for i in range(n_clusters):
        cluster_df.append(df[df['cluster'] == i])

    cluster_sizes = [len(cluster.index) for cluster in cluster_df]

    avg_size = np.mean(cluster_sizes)
    min_size = np.min(cluster_sizes)
    max_size = np.max(cluster_sizes)

    return avg_size, min_size, max_size


def get_cluster_keywords(vectorizer, tweet_vectors, clusters):
    text_df = pd.DataFrame(tweet_vectors.todense()).groupby(clusters).mean()

    feature_names = vectorizer.get_feature_names()

    # Iterate through clusters and print keywords
    for index, series in text_df.iterrows():
        keywords = [feature_names[i] for i in np.argsort(series)]

        keywords = list(
            filter(
                lambda word: not word == 'rt' and not word == 'https', keywords
            )
        )

        print(
            'Keywords for cluster ' + str(index + 1) + ': ' +
            str(keywords[-10:][::-1])
        )


if __name__ == '__main__':
    df, vectorizer, tweet_vectors, clusters = cluster_tweets()

    get_cluster_keywords(vectorizer, tweet_vectors, clusters)

    avg_size, min_size, max_size = get_cluster_size(df)

    print()
    print('Average size:', avg_size)
    print('Min size:', min_size)
    print('Max size:', max_size)
    print()