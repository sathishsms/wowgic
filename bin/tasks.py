from celery import Celery
import sys
sys.path.append('../common')
sys.path.append('../config')
sys.path.append('../resources')
import globalS
import generic
import loggerRecord
import json

logFileName='/tmp/wowgic_celery.log'
logger,fhandler       = loggerRecord.loggerInit(logFileName,'debug')
logger.debug('Log file# %s & TestBed file',logFileName)
celery = Celery('tasks', broker='amqp://guest@localhost//')
# Load the default configuration
celery.config_from_object('celeryconfig')
#read config from envt variable
#celery.config_from_envvar('CELERY_CONFIG_FILE')#D:\wowgic-env\wowgic\wowgic_flask\instance\flaskapp.cfg
#filename = os.path.join(app.instance_path, 'application.cfg')
#with open(filename) as f:
#    config = f.read()
globalS.dictDb = celery.conf
logger.debug('celery dictDB contains %s',globalS.dictDb)

import intercom
intercom=intercom.intercom()

'''
Rough Tasks:
First read all the interest nodes from neo4j
create a common module that inokes instagram & twitter
using celery delay method pass argumenmts to that and invoke the tasks
foreach interest node trigger twitter & instagram calls without affecting the hit rate
store them in mongDB
Again read the interest nodes from neo4j
'''
@celery.task
def getAllInterestNode():
    ''' after first time login of user this gets invoked by an ID provided by UI
    like Request: https://http://wowgicflaskapp-wowgic.rhcloud.com/id=q13512667
    neo4j has associated feeds ID to be displayed to the user fetch them from mongdb and return it back
    '''
    interesetNodes = intercom.getAllInterestNode()
    logger.debug('feedList:%s',interesetNodes)
    geoDict = {}
    #for record in interesetNodes:
    #    if record[0]['lat'] is not None:
    #        geoDict.update({'lat':record[0]['lat']})
    #        geoDict.update({'lng':record[0]['lng']})
    #        geoDict.update({'distance':'.5'})#default radius =500m
    #    logger.debug('recordList output of neo4j:%s',record[0]['name'])
    #    if record[0]['city'] is not None:
    #        Q=record[0]['name'] +' '+ record[0]['city']
    #    else:
    #        Q=record[0]['name']
    #    ID=record[0]['id']
    #    logger.debug('fetchInterestFeeds Q=%s geo cordinates =%s',Q,geoDict)
    #    #retrieveTweets.delay(ID,Q,geoDict)
    #    #retrieveMediaBasedTags.delay(ID,Q,geoDict)
    #    #if mongoInt.checkCollExists(ID) > 1:
    #    #    tweets.extend(mongoInt.retrieveCollection(ID))
    #    #else:
    #    #    tweets.extend(self.retrieveTweets(Q,geoDict))
    #    #    tweets.extend(self.retrieveMediaBasedTags(ID,Q,geoDict))
    #    #    geoDict = {}#revert the geo dictionary
    ##sparkInt.Parallelized(tweets)
    ##feedJson=sparkInt.wowFieldTrueOrFalse(tweets)
    def iterFunc(record):
        geoDict = {}
        if record[0]['lat'] is not None:
            geoDict.update({'lat':record[0]['lat']})
            geoDict.update({'lng':record[0]['lng']})
            geoDict.update({'distance':'.5'})#default radius =500m
        logger.debug('recordList output of neo4j:%s',record[0]['name'])
        if record[0]['city'] is not None:
            Q=record[0]['name'] +' '+ record[0]['city']
        else:
            Q=record[0]['name']
        ID=record[0]['id']
        logger.debug('fetchInterestFeeds Q=%s geo cordinates =%s',Q,geoDict)
        #retrieveMediaBasedTags.delay(ID,Q,geoDict)
        #retrieveTweets.delay(ID,Q,geoDict)
        #g=group(retrieveTweets.s(ID,Q,geoDict,debug=True),
        #retrieveMediaBasedTags.s(ID,Q,geoDict,debug=True))
        #res = g()
    #    retrieveMediaBasedTags.s(ID,Q,geoDict).delay()
        retrieveTweets.s(ID,Q,geoDict).delay()
    map(iterFunc,interesetNodes)

    #jobs = group
    return getAllInterestNode.delay()
    #return True


#@celery.task()
@celery.task(rate_limit='18/m')
def retrieveTweets(collName,Q,geoDict):
    logger.info('retrieveTweets:%s,%s,%s',collName,Q,geoDict)
    return intercom.retrieveTweets(collName,Q,geoDict)


@celery.task(rate_limit='8/m')
#@celery.task()
def retrieveMediaBasedTags(collName,Q,geoDict):
    logger.info('retrieveMediaBasedTags:%s,%s,%s',collName,Q,geoDict)
    return intercom.retrieveMediaBasedTags(collName,Q,geoDict)

getAllInterestNode.delay()
if __name__ == '__main__':
    celery.start()
