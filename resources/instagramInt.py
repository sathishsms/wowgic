#! /usr/bin/python
#===============================================================================
# File Name      : .py
# Date           : 12-21-2015
# Input Files    : Nil
# Author         : Satheesh <sathishsms@gmail.com>
# Description    : This file just interfaces to neo4J and brings you the handle so that multiple files can
#
#===============================================================================
from instagram import client
from flask import url_for, redirect, request
import sys,json
import random
sys.path.append('../common')
import loggerRecord, globalS
logger =  loggerRecord.get_logger()

from collections import OrderedDict

#chella's
INSTA_CLIENT_ID = '081ccf9e86164090af417c8ce91cc2e4'
INSTA_CLIENT_SECRET = '6594a9c5db684dfdb8e289d6471abb39'
#sathish client id
#INSTA_CLIENT_ID = 'dc8b300304794134b6d7e8d22cc45f36'
#INSTA_CLIENT_SECRET = '1979446a482c4db086d8de1ef2ca7631'
ACCESS_TOKEN = '2300510664.081ccf9.545afdfe23b441dd9cfb3d8341c83ca7' # this is about to expire which has to updated each time
client_ip = 'XX.XX.XX.XX'
api=''

class instagramInt:
    ''' bla bla
    '''
    redirect_uri = 'http://'+globalS.dictDb['IP']+':'+globalS.dictDb['APP_PORT']

    def __init__(self,ACCESS_TOKENS):
        logger.debug('who invoked me ? hey u - %s',__name__)
        self.ACCESS_TOKENS = ACCESS_TOKENS
        #authenticate twitter app

    def get_api(self):

        token= random.choice(self.ACCESS_TOKENS)
        logger.info('insta tokens = %s',token)
        logger.info('randomized instagram access token :%s',token['access_token'])
        api = client.InstagramAPI(client_id=INSTA_CLIENT_ID, client_secret=INSTA_CLIENT_SECRET,access_token= token['access_token'])
        return api

    def instagram_login(self):

        self.redirect_uri = self.redirect_uri
        instagram_client = client.InstagramAPI(client_id=INSTA_CLIENT_ID, client_secret=INSTA_CLIENT_SECRET, redirect_uri=self.redirect_uri+ url_for('_handle_instagram_authorization'))
        return redirect(instagram_client.get_authorize_url(scope=['public_content']))

    def _handle_instagram_authorization(self):

        code = request.values.get('code')
        if not code:
            logger.error('code is missing in instagram')
            return 'Missing code in instagram token auth'
        try:
            instagram_client = client.InstagramAPI(client_id=INSTA_CLIENT_ID, client_secret=INSTA_CLIENT_SECRET, redirect_uri=self.redirect_uri+ url_for('_handle_instagram_authorization'))
            logger.debug('Client is authorized lets exchange for token :%s',code)
            access_token, instagram_user = instagram_client.exchange_code_for_access_token(code)
            if not access_token:
                logger.error('Could not get instagram access token')
                #return 'Could not get access token'
            tmpDict = {'access_token':access_token, 'user_id': instagram_user['id']};
            instagram_user.update(tmpDict)
            #update access_token to the instagram_user
            #instagram_user['access_token'] = access_token
            #globalS.dictDb['instagram_userid'] = instagram_user['id']
            #globalS.dictDb['instagram_access_token'] = access_token
            logger.debug('instagram access_token#%s, instagram_user#%s',access_token, instagram_user)
            #deferred.defer(fetch_instagram_for_user, g.user.get_id(), count=20, _queue='instagram')
        except Exception as e:
            return ('Error while handle_instagram_authorization # %s', e)
        #return redirect(url_for('settings_data') + '?after_instagram_auth=True')
        #return globalS.dictDb
        return instagram_user

    def auth(self):
        ''' this generalize the authentication with instagram'''

    def retrieveMediaBasedTags(self,Q,geoDict):
        '''get recent media ids with the tag "instadogs", only get the most recent 80
        tag_recent_media returns 2 variables, the media ID in an array and the next
        url for the next page'''
        media_ids=[]
        api = self.get_api()
        #self.api = client.InstagramAPI(client_id=INSTA_CLIENT_ID, client_secret=client_secret,access_token= access_token)
        logger.debug('fetch instagram medias :%s',Q)
        try:
            tag_search, next_tag = api.tag_search(q=Q,count=2)
        except Exception, e:
            logger.error('instagram api error # %s', e)
            return e
        logger.debug('tagsearch resulted : %s',tag_search)
        #Below will work only if one word is searched
        for tag in tag_search:
            logger.debug('tagsearch resulted : %s',tag.name)
            tag_recent_media,next = api.tag_recent_media(tag_name=tag.name, count=globalS.dictDb['MAX_TWEETS'],return_json=True)
            #logger.debug('tagsearch resulted : %s',tag_recent_media)
            media_ids.extend(tag_recent_media)
        #logger.debug('jsonify error:\n %s', mid)
        return media_ids

    def getLocationSearch(self,geoCode):
        ''' check whether it gets recent media objects based on location or returns
        location id '''
        mediaList=[]
        api = self.get_api()
        logger.debug('getLocationSearch instagram medias :%s',geoCode)
        #self.api = client.InstagramAPI(client_id=INSTA_CLIENT_ID, client_secret=client_secret,access_token= access_token)
        #location_search = self.api.location_search(lat=geoCode['lat'],lng=geoCode['lng'],distance=(geoCode['distance']*1000))
        #for loc in  location_search:
        #    media_ids,next = self.api.location_recent_media(location_id=loc.id,return_json=True)
        #    mediaList.extend(media_ids)
        #    logger.info('instagram api location_search %s',media_ids)
        mediaList = api.media_search(lat=geoCode['lat'],lng=geoCode['lng'],distance=(geoCode['distance']*1000),return_json=True)
        return mediaList
