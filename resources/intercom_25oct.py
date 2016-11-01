#! /usr/bin/python
#===============================================================================
# File Name      : intercom.py
# Date           : 12-02-2015
# Input Files    : Nil
# Author         : Satheesh <sathishsms@gmail.com>
# Description    :
# How to run     :twit_test.py -l info
#                :twit_test.py -h
#===============================================================================
import sys
sys.path.append('common')
sys.path.append('resources')
import globalS
import time
import generic
import json
#from pygeocoder import Geocoder
#from multiprocessing import Pool
import neo4jInterface
import mongoInt
import twitterInt
import instagramInt
import topicModel
import facebookInt
import loggerRecord
import random
from calendar import timegm
#import sparkInt
logger =  loggerRecord.get_logger()

facebookInt = facebookInt.facebookInt()
neo4jInt = neo4jInterface.neo4jInterface()
graphDB=neo4jInt.connect()
#graphDB=neo4jInt.connect('localhost:7474/db/data/','neo4j','admin')
####
# End of boilerplate, interesting code starts here:
neo4jInt.createConstraint(graphDB)
mongoInt=mongoInt.mongoInt()
mconnect = mongoInt.connect()
#sparkInt=sparkInt.sparkInt()

def retrieveTwitterAccessTokens(collName):
        ''' retrieve access tokens from DB and pass it to twitterInt
        '''
        if mongoInt.checkCollExists(collName) < 1:
            ''' if the collection twitter_Access_Tokens is not availble initially
            populate the document with default tokens read from cfg files    '''
            logger.debug('default twitter token is:%s',globalS.dictDb['SATHISH_TOKEN'])
            if mongoInt.insertTwitteTokens(collName,globalS.dictDb['SATHISH_TOKEN']):
                logger.warn('twitter_Access_Tokens was empty added default token now')
        tokens = mongoInt.retrieveTwitterTokens(collName)
        logger.debug('tokens retrieved key secret : %s',tokens)
        return tokens

twitterTokenCollectionName = 'twitter_Access_Tokens'
instagramTokenCollectionName = 'InstagramAccessTokens'
twitterInt = twitterInt.twitterInt(retrieveTwitterAccessTokens(twitterTokenCollectionName))
instagramInt = instagramInt.instagramInt(retrieveTwitterAccessTokens(instagramTokenCollectionName))

class intercom:
    ''' this file act as a intercaller /router / flow chart whaterver you call. T o& fro
    calling functions interworking between verious interfaces like twitter, Instagram,
    facebook , neo4j & mongoDB lies from here
    '''
    def __init__(self):
        logger.debug('who invoked me ? hey u - %s',__name__)
        #mconnect = mongoInt.connect()
        #sparkInt.connect()
        #authenticate twitter app

    def createUserNode(self,decodedFBJson):
        '''
        latitude & longitude also needs to be stored in neo4j for retrival of reveland tweets
        '''
        #decodedFBJson=json.loads(decodedFBJson) remove true for now
        #if mongoInt.insertFBUserLoginData(decodedFBJson) or True:
        mongoInt.insertFBUserLoginData(decodedFBJson)
        neo4jInt.createUserNode(graphDB,decodedFBJson,'user')
        interestList = ['hometown','location','work','education']
        for intr in interestList:
            if 'work' in intr:
                keyIs='employer'
            elif 'education' in intr:
                keyIs='school'
            if intr in decodedFBJson:
                if isinstance(decodedFBJson[intr],list):
                    for itm in decodedFBJson[intr]:
                        if itm.get('type') == None:
                                itm['type'] = keyIs
                        data = facebookInt.getIdLocation(itm[keyIs]['id'])
                        logger.debug('Facebook get address using id:%s',data)
                        if 'location' in data:
                            itm[keyIs].update(data['location'])
                else:
                    data = facebookInt.getIdLocation(decodedFBJson[intr]['id'])
                    logger.debug('Facebook get address using id:%s',data)
                    if 'location' in data:
                        decodedFBJson[intr].update(data['location'])
                #add IF check whther interest is part of data provided
                neo4jInt.createInterestNode(graphDB,decodedFBJson,intr)
                #creating mongoDb interest nodes with ID as thy are unique
                if not mongoInt.createCollectionIfnot(decodedFBJson['id']):
                    logger.warn('unable to create collection in mongodb')
            else:
                logger.debug('user key doesnot exists')
        logger.debug('dataFb decodedFBJson:%s',decodedFBJson)
        #else:
        #logger.debug('user already exists hence skipping the neo4J creation of nodes & interest')
        #once the nodes are created lets fetch the feeds
        return 1

    def topicModelLSI(self,twits):
        '''
        irrespc of collection fetch the pratenId=1 tweets and merge them together with the curreent tweets from twitter AJX call
        then run topic modeling 
        '''
        topicModelObj = topicModel.topicModel(twits)
        dictionary = topicModelObj.createDictionary()
        corpus = []
        for vector in topicModelObj:
            corpus.append(vector)
        #print(corpus)
        return topicModelObj.createLSIModel(corpus)

    def retrieveTweets(self,ID,Q,geoCode):
        '''retrieveTweets from twitter and store the feeds into MongoDB
        '''
        logger.debug('retrieve tweets')
        #fetch the latest since_id and pass it in next twitter call
        #since_id = mongoInt.retrieveSinceID(ID)
        twits = twitterInt.retrieveTweets(Q,geoCode)
        #map(lambda tw:tw.update({'created_time': timegm(time.gmtime(time.strptime(tw['created_at'],"%a %b %d %H:%M:%S +0000 %Y")))}),twits)
        map(lambda tw:tw.update({'created_time': timegm(time.strptime(tw['created_at'],"%a %b %d %H:%M:%S +0000 %Y"))}),twits)
        
        #callinf directly instead of wrapper change it later
        #pass only twitter text & ID only here
        logger.info('tweets fetched are %s',twits)
        similarTweet = self.topicModelLSI(twits) # new feeds from service
        #topicModelObj.close()
        #map(lambda tw:tw.update({'created_time': int(time.mktime(time.strptime(tw['created_at'],"%a %b %d %H:%M:%S +0000 %Y")))}),twits)
        #map(lambda tw:tw.update({'created_time': int(time.gmtime(time.strptime(tw['created_at'],"%a %b %d %H:%M:%S +0000 %Y")))}),twits)
        #twits = twitterInt.retrieveTweetsBasedHashtag(Q)
        #if geoCode:
        #    twits.extend(twitterInt.retrieveTweetBasedLocation(geoCode))
        logger.debug('storing tweets of twitter of both location based on keyword mongoDb')
        #twits=sparkInt.wowFieldTrueOrFalse(twits)
        self.similarTopicRemoval(ID,similarTweet,twits)
        #self.insertFeedData(ID,twits)
        #page_sanitized = json_util.dumps(twits)
        # below returning to be removed has to be done from mongoDB only
        return len(twits)

    def similarTopicRemoval(self,collName,similarTweet,twits):
        ''' if childId = parentId update mongoDB parentId = true
            else parent id != child ID & ratio != 1.0 update mongodb parentId = parent id, ratio = ratio 
            analysis
        '''
        uniqueTweetsFromTwitter =[]
        similarTweetsFromTwitter =[]
        logger.debug('entering')

        for childID,parentID,ratio in zip(similarTweet[0],similarTweet[2],similarTweet[1]):
            for twit in twits:
                if childID == parentID:
                    if twit['id'] is parentID:
                        twit.update({'parentId' : 1})
                        uniqueTweetsFromTwitter.append(twit)
                        
                elif childID != parentID and ratio <= 0.999999:
                #elif cmp(1,float(ratio)) == 1:
                    #logger.error('%s != %s & ratio : %s',childID,cmp(float(ratio),1),ratio)
                    if twit['id'] is childID:
                        tmpDict = {'parentId' : parentID, 'ratio' : float(ratio)}
                        twit.update(tmpDict)
                        similarTweetsFromTwitter.append(twit)
            
        uniqueTweetsFromDB = mongoInt.retrieveParentIdTrue(collName)
        # similar_id1 = []
        # for ele in uniqueTweetsFromDB:
            # similar_id1.append(ele['id'])
        logger.debug('existing uniqueTweetsFromDB :%s',len(uniqueTweetsFromDB))
        uniqueTweetsFromDB.extend(uniqueTweetsFromTwitter)
        #<place holder remove the matching tweets between uniqueTweetsFromDB and which is again got from server uniqueTweetsFromTwitter
        allUniqueTweetsIDList = []
        for ele in uniqueTweetsFromDB:
            allUniqueTweetsIDList.append(ele['id'])
        logger.debug('Duplication allUniqueTweetsIDList contains len : %s value :%s',len(allUniqueTweetsIDList),allUniqueTweetsIDList)
        allUniqueTweetsIDList = set(allUniqueTweetsIDList)
        logger.debug('unique allUniqueTweetsIDList contains len : %s value :%s',len(allUniqueTweetsIDList), allUniqueTweetsIDList)
        allUniqueTweets = []
        for ident in allUniqueTweetsIDList:
            for ele in uniqueTweetsFromDB:
                if ele['id'] is ident:
                    allUniqueTweets.append(ele)
        logger.debug('allUniqueTweets lenght is %s',allUniqueTweets)
        similarTweet = self.topicModelLSI(allUniqueTweets)


        uniqueTweetsFromTwitter_1 = []
        for childID,parentID,ratio in zip(similarTweet[0],similarTweet[2],similarTweet[1]):
            for twit in twits :
                #similar_id = similar_id1
                #if twit['id'] not in similar_id:
                #   similar_id.append(twit['id'])
                if childID == parentID:
                    if twit['id'] is parentID:
                        twit.update({'parentId' : 1})
                        uniqueTweetsFromTwitter_1.append(twit)
                        # similar_id1.append(twit['id'])

                # elif childID != parentID and ratio <= 0.999999 and childID not in similar_id1:
                # elif childID != parentID and ratio <= 0.999999 :
                    # #similar_id.append(childID)
                    # #elif cmp(1,float(ratio)) == 1:
                    # #logger.error('%s != %s & ratio : %s',childID,cmp(float(ratio),1),ratio)
                    # if twit['id'] is childID:
                        # tmpDict = {'parentId' : parentID, 'ratio' : float(ratio)}
                        # twit.update(tmpDict)
                        # similarTweetsFromTwitter.append(twit)
 
        for ele in uniqueTweetsFromTwitter_1:
            logger.debug('current tweets : text: %s, ID: %s',ele['text'],ele['id'])

        '''
        else:
            #if collection already exists
            for childID,parentID,ratio in zip(similarTweet[0],similarTweet[2],similarTweet[1]):
                for twit in twits:
                    if childID == parentID:
                        if twit['id'] is parentID:
                            uniqueTweetsFromTwitter.append(twit)

            uniqueTweetsFromDB = mongoInt.retrieveParentIdTrue(collName)
            logger.debug('uniqueTweetsFromDB :%s',uniqueTweetsFromDB)
            topicModelObj = topicModel.topicModel(uniqueTweetsFromDB)
            dictionary = topicModelObj.createDictionary()
            corpus = []
            for vector in topicModelObj:
                corpus.append(vector)
            
            logger.debug('chelloi corpus : %s',corpus)

            similarTweet= topicModelObj.createLSIModel(corpus,uniqueTweetsFromTwitter)
            logger.debug('chelloi similarTweet : %s',similarTweet)
            
            for childID,parentID,ratio in zip(similarTweet[0],similarTweet[2],similarTweet[1]):
                for twit in twits:
                    if childID == parentID:
                        if twit['id'] is parentID:
                            twit.update({'parentId' : 1})
                            uniqueTweetsFromTwitter.append(twit)
                    elif childID != parentID and ratio <= 0.999999:
                    #elif cmp(1,float(ratio)) == 1:
                        #logger.error('%s != %s & ratio : %s',childID,cmp(float(ratio),1),ratio)
                        if twit['id'] is childID:
                            tmpDict = {'parentId' : parentID, 'ratio' : float(ratio)}
                            twit.update(tmpDict)
                            uniqueTweetsFromTwitter.append(twit)
                            '''
        logger.info('Before revomal %s twits after similar Topic removal: %s',len(twits),len(uniqueTweetsFromTwitter_1))
        uniqueTweetsFromTwitter_1.extend(similarTweetsFromTwitter)
        self.insertFeedData(collName,uniqueTweetsFromTwitter_1)
        return len(uniqueTweetsFromTwitter) #simple returning the count of unique tweets
        
    def insertFeedData(self,collName,docs):
        ''' mock for mongo int inserting documents '''
        passCnt = 0
        if len(docs):
            passCnt += mongoInt.insertFeedData(collName,docs)
        else:
            logger.debug('docList is empty')
            if not mongoInt.createCollectionIfnot(collName):
                logger.warn('unable to create collection in mongodb')
        return passCnt

    def instagram_login(self):
        ''' bypasser for instagram login as decorator functions are used This
        function is called from app.py & calls instagramInt function
        '''
        return instagramInt.instagram_login()

    def retrieveMediaBasedTags(self,ID,Q,geoDict):
        '''instagram feeds this function is hanging correct it
        '''
        logger.debug('retrieve instagram medias')
        #tag search in instagram remove comma
        #Q.replace(',','')
        feedJson = instagramInt.retrieveMediaBasedTags(Q,geoDict)
        if geoDict:
            logger.debug('geoDict for instagram based media retrieve  %s',geoDict)
            feedJson.extend(instagramInt.getLocationSearch(geoDict))
        #else:
        #    # Example addr: 875 N Michigan Ave, Chicago, IL 60611
        #    results = Geocoder.geocode(Q)
        #    latlng=results.coordinates
        #    logger.debug('google geocode api coordinate pair:%s',latlng)
        #    geoDict.update({'lat':latlng[0]})
        #    geoDict.update({'lng':latlng[1]})
        #    geoDict.update({'distance':'.5'})#default radius =500m
        #logger.debug('geo cord to search in instagram is %s',geoDict)
        #feedJson.extend(instagramInt.getLocationSearch(geoDict))
        #feedJson = json.loads(feedJson)
        map(lambda tw:tw.update({'created_time': int(tw['created_time'])}),feedJson) #convert string to int
        logger.debug('store instagram media in mongoDb')
        #use spark removed unwanted feilds in json & add a key:value
        #feedJson=sparkInt.wowFieldTrueOrFalse(feedJson)
        self.insertFeedData(ID,feedJson)
        # below returning to be removed has to be done from mongoDB only
        return len(feedJson)

    def refreshFeeds(self):
        ''' this method is invoked when user hits 2nd time and we fetch his interest
        via the ID provided by UI and fetch the corresponding neo4j interest nodes
        returning feed Ids.
        Also invoked for the very first time as well aftr cr8ing neo4j nodes ( this statment is tricky lets refine)
        '''
        #fetch neo4j interest based on ID's

    def fetchInterestFeeds(self,ID,lastTimeStamp):
        '''fetch the all neo4j interest nodes returning name & city then using those
        tags look for mongoDb collection if not then do search in twitter &
        instagram and store the output in mongoDb in a collection mapped to interest nodes'''

        recordList = neo4jInt.getInterestNode(graphDB,ID)
        #intialise the variables
        geoDict = {}
        tweets=[]
        jobsArgs =[]
        collectionList = []

        #parse the recordList and frame the has tags here
        for record in recordList:
            geoDict = {}#revert the geo dictionary
            if record[0]['lat'] is not None:
                geoDict.update({'lat':record[0]['lat']})
                geoDict.update({'lng':record[0]['lng']})
                geoDict.update({'distance':'.5'})#default radius =500m
                logger.info('recordList output of neo4j:%s',record[0]['name'])

            if record[0]['city'] is not None:
                Q=record[0]['name'] +' '+ record[0]['city']
            else:
                Q=record[0]['name']

            ID=record[0]['id']
            logger.debug('fetchInterestFeeds ID:%s Q=%s geo cordinates =%s',ID,Q,geoDict)

            if mongoInt.checkCollExists(ID) > 1:
                collectionList.append(ID)
            else:
                jobsArgs.append([ID,Q,geoDict])


        ## auxiliary funciton to make it work

        #first time login logic to be defined
        if len(collectionList):
            def recCursor(lastTimeStamp):
                ''' not an effective method to query across multiple connection '''
                for collName in collectionList:
                    logger.debug('collName = %s & time = %s',collName,lastTimeStamp)
                    docLists =  mongoInt.retrieveCollection(collName,lastTimeStamp,globalS.dictDb['MONGODB_COUNT_LIMIT'])
                    if globalS.dictDb['APP_DEBUG']:
                        def insertQueryData(twit,*argv):
                            twit.update({'queryDetails':argv})
                        map(lambda twit: insertQueryData(twit,ID), docLists);
                    if len(docLists):
                        logger.info('fetched %s docs from collection:%s appending to tweets',len(docLists),collName)
                        #print the ID's of feeds so that we verify any dup feeds are obtained
                        map(lambda twit: logger.debug('doc ID is %s',twit['id']), docLists);
                        tweets.extend(docLists)
                if len(tweets) < 10:
                    lastTimeStamp=int(lastTimeStamp)-globalS.dictDb['DELTA_FEEDS_TIME']
                    logger.info('Docs are not available so recursive calling %s',lastTimeStamp)
                    return recCursor(lastTimeStamp)
                logger.info('collectively returned %s docs for multiple documents %s',len(tweets),collectionList)
                return 1
            recCursor(lastTimeStamp)
        elif (len(tweets) == 0) and len(jobsArgs):
            logger.warn('Collection is empty invoking worker pools:%s',jobsArgs)

            def retrieveMedias_helper(args):
                tweets.extend(self.retrieveMediaBasedTags(*args))
            def retrieveTweets_helper(args):
                '''commenting this as its taking too much of time'''
                tweets.extend(self.retrieveTweets(*args))
            #map(retrieveTweets_helper,jobsArgs)
            map(retrieveMedias_helper,jobsArgs)
            logger.debug('multiprocessing pool has returned %s feeds',len(tweets))
            #tweets = tweets[:20]
        #sparkInt.Parallelized(tweets)
        #feedJson=sparkInt.wowFieldTrueOrFalse(tweets)
        return tweets


    def updateFBUserLoginData(self,userTimeJson):
        '''store last_login into user data
        '''
        #0 means not updated
        if mongoInt.updateFBUserLoginData(userTimeJson):
            logger.debug('updated user login DB with last_login ')
            return 1
        else:
            logger.error('updating user login DB with last_login failed')
            return 0

    def handle_instagram_authorization(self):
        '''
        '''
        passCnt = 0
        user=instagramInt._handle_instagram_authorization()
        if 'access_token' in user:
            passCnt += mongoInt.insertTwitteTokens(instagramTokenCollectionName,user)
            return "Thanks buddy ! Instagram is authorized"
        logger.info('instagram_retrieved tokens is %s',user)
        return user

    def FBLoginData(self,userJson):
        '''
        very first time user comes in
        '''
        #store the user data along with access_token
        #logger.debug('userJson:%s',userJson)
        try:
            userJson=json.loads(userJson)
        except:
            pass #while passing json directly this is not reqd in production remove this
        #passCnt += mongoInt.insertFBUserLoginData(userJson)
        logger.info('FB data obtained is %s',userJson)
        self.createUserNode(userJson)
        logger.debug('fetch interest based feeds')
        #feedList=self.fetchInterestFeeds(userJson['id'])
        return userJson['id'] #return 1 on success 0 on failure

    def retrieveLocationBasedTags(self,geoCode):
        ''' the slidebar feature based on radius dragging is done here both twitter
        & instagram datas are retrieved'''
        passCnt = 0
        feedList=[]
        feedList.extend(twitterInt.retrieveTweetBasedLocation(geoCode))
        #do a reverse geocoding and hit with feeds
        feedList.extend(instagramInt.getLocationSearch(geoCode))
        #passCnt += mongoInt.insertInstagramUserLoginData(user)
        random.shuffle(feedList)
        return feedList

    def verifyAuthUser(self,ID):
        ''' just return the password token stored in mongoDB
        '''
        return mongoInt.validateToken(ID)

    def getAllInterestNode(self):
        ''' just return the password token stored in mongoDB
        '''
        return neo4jInt.getAllInterestNode(graphDB)

    def retrieveCollection(self,ID,lastTimeStamp,count):
        ''' for displayFeeds debugging stuff
        '''
        tweets=[]
        #docs = mongoInt.retrieveCollection(ID,lastTimeStamp,count)
        #tweets.extend(docs) if docs>0 else 0
        tweets.extend(mongoInt.retrieveCollection(ID,lastTimeStamp,count))
        if globalS.dictDb['APP_DEBUG']:
            logger.debug('APP_DEBUG is true so seeting the queryDetails:ID field')
            def insertQueryData(twit,ID):
                twit.update({'queryDetails':ID})
                #return twit
            map(lambda twit: insertQueryData(twit, ID), tweets);
        return tweets

    def insertTwitterAccessTokens(self,resp):
        ''' store the twitter access tokens of the user
        '''
        logger.debug('twitter authorized response:%s',resp)
        collName = 'twitter_Access_Tokens'
        nInserted = mongoInt.insertTwitteTokens(collName,resp)
        if nInserted:
            logger.debug('successful insert of twitter access token')
        else:
            logger.error('unable to insert the twitter access token')
        return nInserted
