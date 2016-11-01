# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy Twitter API library
"""
__version__ = '3.5.0'
__author__ = 'Joshua Roesslein'
__license__ = 'MIT'

from tweepy.models import Status, User, DirectMessage, Friendship, SavedSearch, SearchResults, ModelFactory, Category
from tweepy.error import TweepError, RateLimitError
from tweepy.api import API
from tweepy.cache import Cache, MemoryCache, FileCache
from tweepy.auth import OAuthHandler, AppAuthHandler
from tweepy.limit import RateLimitHandler
from tweepy.streaming import Stream, StreamListener
from tweepy.cursor import Cursor

# Global, unauthenticated instance of API
api = API()

def debug(enable=True, level=1):
    from six.moves.http_client import HTTPConnection
    HTTPConnection.debuglevel = level


def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


class Twitter(object):
    """
    Twitter API wrapper based on Tweepy using the RateLimitHandler
    with multiple access tokens (see https://github.com/svven/tweepy).
    It also handles API method cursors and splits input param lists in
    chunks if neccessary.
    """

    def __init__(self,
        consumer_key, consumer_secret, access_tokens=None):
        """
        Initialize params for RateLimitHandler to pass to Tweepy API.
        Param `access_tokens` must be a dictionary but it can be loaded
        later just before the first API method call, and has to be like
        {user_id: (access_token_key, access_token_secret)}.
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_tokens = access_tokens

    _api = None

    def _get_api(self):
        "Initialize Tweepy API object with RateLimitHandler auth."
        auth = RateLimitHandler(self.consumer_key, self.consumer_secret)
        for key, secret in self.access_tokens.values():
            auth.add_access_token(key, secret)
        # print 'Token pool size: %d' % len(auth.tokens)
        return API(auth)
            # retry_count=2, retry_delay=3,
            # wait_on_rate_limit=True, wait_on_rate_limit_notify=True

    @property
    def api(self):
        "Lazy loaded Tweepy API object."
        if not self._api:
            self._api = self._get_api()
        return self._api

