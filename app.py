#!/usr/bin/env python
# george/app.py

import os
import logging
import tweepy

from distutils.util import strtobool

from config import create_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class FavRetweetListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        self.me = api.me()
        
        LIKE = strtobool(os.getenv("LIKE", "FALSE"))
        RETWEET = strtobool(os.getenv("RETWEET", "FALSE"))
        COMMENT = strtobool(os.getenv("COMMENT", "FALSE"))
        MSG = os.getenv("MSG")

    def on_status(self, tweet):
        logger.info("Processing Tweet")
        if tweet.in_reply_to_status_id is not None or \
            tweet.user.id == self.me.id:
            # This tweet is a reply or I'm its author, ignore
            return
        if not tweet.favorited and LIKE is True:
            # Mark it as Liked, since we have not done it yet
            try:
                tweet.favorite()
                logger.debug("Liked")
            except Exception as e:
                logger.error("Error on fav", exc_info=True)
        if not tweet.retweeted and RETWEET is True:
            # Retweet, since we have not retweeted it yet
            try:
                tweet.retweet()
                logger.debug("ReTweeted")
            except Exception as e:
                logger.error("Error on retweet", exc_info=True)
        if not tweet.retweeted and COMMENT is True:
            # Comment
            try:
                logger.info("Commenting ...")
                reply = "@" + tweet.author._json['screen_name'] + " " + MSG
                self.api.update_status(status=reply, in_reply_to_status_id=tweet.id, auto_populate_reply_metadata=True) 
                logger.debug("Commented")               
            except Exception as e:
                logger.error("Error on reply", exc_info=True)

    def on_error(self, status):
        logger.error(status)

  
def main(keywords):
    logger.info("Configuring API ...")
    api = create_api()
    tweets_listener = FavRetweetListener(api)
    stream = tweepy.Stream(api.auth, tweets_listener)
    stream.filter(track=keywords, languages=["en"])
    logger.info("Stream is now running ...")
    time.sleep(STREAM_TIME)
    logger.info("... stream is now stopping.")
    stream.disconnect()
    return

if __name__ == "__main__":
    HASHTAG = os.getenv("HASHTAG", "#sleep")
    THROTTLE = os.getenv("THROTTLE", 21600)
    STREAM_TIME = os.getenv("STREAM_TIME", 10)

    while True:
        logger.info("Starting Stream ...")
        main([HASHTAG])
        logger.info("Waiting on next cycle to start stream again ...")
        time.sleep(THROTTLE)