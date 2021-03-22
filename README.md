# Twitter Crawler

Twitter Crawler is a coursework task for the Web Science (H) course undertaken at the University of Glasgow in 2021. Instructions on how to run the crawler and install the correct requirements can be found below.

## Twitter API Keys

Create a Twitter developer account [here](https://developer.twitter.com/en/apply-for-access). Create a copy of the [.env.example](.env.example) file and rename it to `.env`. Enter your Twitter API keys into the `.env` file so that you are able to run the crawler.

## Installation Instructions

[Install Python 3](https://www.python.org/downloads/) on your machine and follow the installation instructions. Note, this project has not been tested with Python 2 and is unlikely to work with Python 2. Next, create a Python virtual environment using the command:

```
python3 -m venv venv
```

After creating the virtual environment, activate it with the following commands:

```
cd venv
source bin/activate
cd ..
```

Install the requirements in the [requirements.txt](requirements.txt) file using pip:

```
pip install -r requirements.txt
```

Install MongoDB onto your machine using these [instructions](https://docs.mongodb.com/manual/installation/). The Twitter crawler uses a localhost database so this step is imperative.

## Running the Crawler

To run the Streaming API crawler, first navigate to the src folder using `cd src` and then run the following command:

```
python crawler.py
```

To cluster the Tweets based on similarity, run the following command:

```
python clusters.py
```

To run the hybrid crawler that utilises both the Streaming and REST API, run the following command:

```
python hybrid.py
```

To retrieve statistics about the Tweets that have been collected in the steps above, run the following command:

```
python counter.py
```
