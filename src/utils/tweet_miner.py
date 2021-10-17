
import os
import tweepy
from tweepy import StreamListener
import threading
import pandas as pd
import datetime as dt
import json
from time import time
# from google.cloud import language
from dotenv import load_dotenv
load_dotenv()

class Listener(StreamListener):
    def __init__(self, symbol):
        """
        Initialize twitter listener
        """
        super(Listener,self).__init__()
        self.symbol = symbol

    def on_error(self,status):
        print(status)
        return True

class TweetMiner:
    def __init__(self,symbol, max_tweets=1000):
        """  Initialize tweet miner with Tweepy API """
        self.symbol = symbol
        self._consumer_key = os.getenv('CONSUMER_KEY')
        self._consumer_secret = os.getenv('CONSUMER_SECRET')
        self._access_token = os.getenv('ACCESS_TOKEN')
        self._access_secret = os.getenv('ACCESS_SECRET')
        self.results = []
        self.max_tweets = max_tweets

        self.auth = tweepy.OAuthHandler(self._consumer_key,self._consumer_secret)
        self.auth.set_access_token(self._access_token,self._access_secret)
        self.api = tweepy.API(self.auth)

    def _stream_tweet(self):
        """
            Initialize streamer and filter tweets by the specified symbol
        """
        twitter_stream = tweepy.Stream(self.auth, Listener(self.symbol))
        twitter_stream.filter(track=["#"+self.symbol,self.symbol,"$"+self.symbol])

    def _write_tweets(self,tweets):
        """ Append the tweets to a file already created """
        with open(self.symbol+"\\"+self.symbol+"_JTweets.json", 'a') as f:
            for tweet in tweets:
                json.dump(tweet._json, f)
                f.write('\n')

    def _transfer_to_text(self):
        """ Transfer tweets from .json to .txt """
        with open(self.symbol+"\\"+self.symbol+"_Tweets.txt","a") as f2:
                with open(self.symbol+"\\"+self.symbol+"_JTweets.json","r") as f3:
                    for line in f3:
                        tweet = json.loads(line)
                        f2.write(tweet["text"].encode("utf-8"))
                        f2.write("\n")

    def _tweet_to_df(self):
        """ Transform the tweets to a Pandas Dataframe """
        self.df = pd.read_json(self.symbol+"\\"+self.symbol+"_JTweets.json",lines=True)
        self.df = self.df.set_index(pd.DatetimeIndex(self.df["created_at"]))
        self.df = pd.DataFrame(self.df["text"].drop_duplicates())

    def _get_tweet_id(self, date='', days_ago=9, query='a'):
        """ Function that gets the ID of a tweet. This ID can then be
        used as a 'starting point' from which to search. The query is
        required and has been set to a commonly used word by default.
        The variable 'days_ago' has been initialized to the maximum
        amount we are able to search back in time (9)."""

        if date:
            # return an ID from the start of the given day
            td = date + dt.timedelta(days=1)
            tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
            tweet = self.api.search(q=query, count=1, until=tweet_date)
        else:
            # return an ID from __ days ago
            td = dt.datetime.now() - dt.timedelta(days=days_ago)
            tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
            # get list of up to 10 tweets
            tweet = self.api.search(q=query, count=10, until=tweet_date)
            print('search limit (start/stop):',tweet[0].created_at)
            # return the id of the first tweet in the list
            return tweet[0].id

    def _tweet_search(self, query, max_tweets, max_id, since_id, geocode):
        """ Function that takes in a search string 'query', the maximum
            number of tweets 'max_tweets', and the minimum (i.e., starting)
            tweet id. It returns a list of tweepy.models.Status objects. """

        searched_tweets = []
        while len(searched_tweets) < max_tweets:
            remaining_tweets = max_tweets - len(searched_tweets)
            try:
                # You can start from an ID previously retrieved
                new_tweets = self.api.search(q=query, count=remaining_tweets,
                                        since_id=str(since_id),
                                        max_id=str(max_id - 1))
                # Print if there were tweets found
                print('found', len(new_tweets), 'tweets')
                if not new_tweets:
                    print('no tweets found')
                    break
                # Store tweets found in array
                for i in new_tweets:
                    if i not in searched_tweets:
                        searched_tweets.append(i)
                max_id = new_tweets[-1].id
            except tweepy.TweepError:
                print('exception raised, waiting 15 minutes')
                print('(until:', dt.datetime.now() + dt.timedelta(minutes=15), ')')
                time.sleep(15 * 60)
                break  # stop the loop
        # Return searched_tweets and current max_id
        return searched_tweets, max_id

    def _main_function(self):
        """ This is a script that continuously searches for tweets
        that were created over a given number of days. The search
        dates and search phrase can be changed below. """

        # Store search variables
        search_phrases = [self.symbol]
         # Set runtime limit
        time_limit = 1.5    
        # Number of tweets per search (will be                      
        max_tweets = self.max_tweets                           
        # Search limits in days from 7 to 8                     
        min_days_old, max_days_old = 0, 8        
        # This geocode includes nearly all American states (and a large portion of Canada)        
        USA = '39.8,-95.583068847656,2500km'       


        # Loop over search items,
        # Creating a new file for each (In this case only one)
        for search_phrase in search_phrases:

            print('Search phrase =', search_phrase)

            # Set json file in which the tweets will be stored
            json_file_root = self.symbol + '/'  + self.symbol + "_JTweets.json"
            if not os.path.exists(os.path.dirname(json_file_root)):
                os.makedirs(os.path.dirname(json_file_root))
            read_IDs = False

            # Open a file in which to store the tweets
            if max_days_old - min_days_old == 1:
                d = dt.datetime.now() - dt.timedelta(days=min_days_old)
                day = '{0}-{1:0>2}-{2:0>2}'.format(d.year, d.month, d.day)
            else:
                d1 = dt.datetime.now() - dt.timedelta(days=max_days_old-1)
                d2 = dt.datetime.now() - dt.timedelta(days=min_days_old)
                day = '{0}-{1:0>2}-{2:0>2}_to_{3}-{4:0>2}-{5:0>2}'.format(
                      d1.year, d1.month, d1.day, d2.year, d2.month, d2.day)
            json_file = json_file_root
            if os.path.isfile(json_file):
                print('Appending tweets to file named: ',json_file)
                read_IDs = True

            # Set the 'starting point' ID for tweet collection
            if read_IDs:
                # Open the json file and get the latest tweet ID
                with open(json_file, 'r') as f:
                    lines = f.readlines()
                    max_id = json.loads(lines[-1])['id']
                    print('Searching from the bottom ID in file')
            else:
                # Get the ID of a tweet that is min_days_old
                if min_days_old == 0:
                    max_id = -1
                else:
                    max_id = self._get_tweet_id(days_ago=(min_days_old-1))
            # Set the smallest ID to search for
            since_id = self._get_tweet_id(days_ago=(max_days_old-1))
            print('max id (starting point) =', max_id)
            print('since id (ending point) =', since_id)

            # Retrieve tweets loops.
            start = dt.datetime.now()
            end = start + dt.timedelta(hours=time_limit)
            count, exitcount = 0, 0
            while dt.datetime.now() < end:
                count += 1
                print('count =',count)
                # Collect tweets and update max_id
                if os.path.exists(self.symbol + "\\" + self.symbol + "_JTweets.json") and os.path.getsize(self.symbol + "\\" + self.symbol + "_JTweets.json") >= 900000:
                    print("Limited file size, reached: " + str(os.path.getsize(self.symbol + "\\" + self.symbol + "_JTweets.json")))
                    return 0
                tweets, max_id = self._tweet_search(search_phrase, max_tweets,
                                              max_id=max_id, since_id=since_id,
                                              geocode=USA)
                # Write tweets to file in JSON format
                if tweets:
                    self._write_tweets(tweets)
                    exitcount = 0
                else:
                    exitcount += 1
                    if exitcount == 10:
                        if search_phrase == search_phrases[-1]:
                            print('Maximum number of empty tweet strings reached - exiting')
                            break
                        else:
                            print('Maximum number of empty tweet strings reached - breaking')
                            break


    def main_function(self, test=True):
        if not test:
            self._main_function()
        self._tweet_to_df()

    def get_df(self):
        self._tweet_to_df()
        return self.df
