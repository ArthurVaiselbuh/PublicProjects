import tweepy
from tweepy import OAuthHandler
import tokens

consumer_key = tokens.CONSUMER_KEY
consumer_secret = tokens.CONSUMER_SECRET
access_token = tokens.ACCESS_TOKEN
access_secret = tokens.TOKEN_SECRET

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)

# Reading timeline
for i, status in enumerate(tweepy.Cursor(api.home_timeline).items(10)):
    # Process a single status
    print(i, status.text)

