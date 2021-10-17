import os
import re
import io
import tweepy
from flask import Response
from bson.json_util import dumps, RELAXED_JSON_OPTIONS
from tweepy.parsers import JSONParser


consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_SECRET')
# create OAuthHandler object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# set access token and secret
auth.set_access_token(access_token, access_token_secret)
# create tweepy API object to fetch tweets
api = tweepy.API(auth, parser=JSONParser())


def get_tweets(query, count = 10):

    # empty list to store parsed tweets
    tweets = []
    # target = io.open("mytweets.txt", 'w', encoding='utf-8')
    # call twitter api to fetch tweets
    q=str(query)
    fetched_tweets = api.search_tweets(q, count=count, lang='en', include_entities=False)
    print(type(fetched_tweets))
    # parsing tweets one by one

    for tweet in fetched_tweets['statuses']:
        tweets.append(tweet['text'])
        # empty dictionary to store required params of a tweet
        # parsed_tweet = {}
        # saving text of tweet
        # parsed_tweet['text'] = tweet.text
        # if "http" not in tweet.text:
        #     line = re.sub("[^A-Za-z]", " ", tweet.text)
        #     target.write(line+"\n")

    return Response(
        dumps(tweets, json_options=RELAXED_JSON_OPTIONS),
        status=200,
        mimetype="application/json",
        content_type="application/json"
    )
