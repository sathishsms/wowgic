#! /usr/bin/python
#===============================================================================
# File Name      : .py
# Date           : 12-02-2015
# Input Files    : Nil
# Author         : Satheesh <sathishsms@gmail.com>
# Description    : This file just interfaces to neo4J and brings you the handle so that multiple files can
#
#===============================================================================
import sys
sys.path.append('../common')
import loggerRecord
logger =  loggerRecord.get_logger()
####
from twitterInt import *
# Get neo4j set up
from py2neo import *
class neo4jInterface:
    ''' bla bla
        MATCH (n {id:'858104450925382'}) OPTIONAL MATCH (n)-[r]-() DELETE n,r RETURN count(n)
    '''
    #REST server credentials
    #default Remember to change these credentials User/Pass.
    #userName = 'Wowgic'
    userName = globalS.dictDb['NEO4J_USERNAME']
    passWord = globalS.dictDb['NEO4J_PASSWORD']
    #passWord = 'GcpXosEMPJV5pLR0QJQ3'
    #Rest server uri
    #connectUri='neo-graciela-stracke-cornsilk-564c5f886175e.do-stories.graphstory.com:7473'
    #connectUri='wowgic.sb02.stations.graphenedb.com:24789/db/data/'
    connectUri=globalS.dictDb['NEO4J_IP']+':7474/db/data/'

    #optional authentication for database servers, enabled by default
    #authenticate(connectUri,userName,passWord)
    def __init__(self):
        logger.debug('who invoked me ? hey u - %s',__name__)

    ############################################################################
    #Function Name  : connect                                                  #
    #Input          : IP -> IP of the machine to connect                       #
    #               : Username & password to connect with                      #
    #Return Value   : object to interact withe neo4j                           #
    ############################################################################
    def connect(self,c=connectUri,u=userName,p=passWord):
        '''The Graph class provides a wrapper around the REST API exposed by a running Neo4j database server and is
        identified by the base URI of the graph database'''
        #secure_graph frame the credentials
        secureUri = 'http://'+u+':'+p+'@'+c
        #secureUri = u+'/db/data/'
        #neo4jInt.connect('localhost:7474/db/data/','neo4j','admin')
        logger.debug('who invoked me ? hey u - %s',secureUri)
        graphDB = Graph(secureUri)
        #graphDB = Graph()
        #return Graph(secureUri)
        return graphDB

    ############################################################################
    #Function Name  : connect                                                  #
    #Input          : IP -> IP of the machine to connect                       #
    #               : Username & password to connect with                      #
    #Return Value   : 1 on success, 0 on failure                               #
    ############################################################################
    def createConstraint(self,graphDB,id=id):
        '''unique property constraints to ensure that property values are unique
        for all nodes
        '''
        logger.info('creating a neo4J constraint')
        try:
            n=graphDB.cypher.execute("""CREATE CONSTRAINT ON (n:name) ASSERT n.id IS UNIQUE """)
            logger.debug("neo4j constraint query output:%s",n)
            #assert (len(n) > 0 ),"Unable to create neo4j CONSTRAINT"
        except:
            logger.error("Error in creating constraint#%s",sys.exc_info()[0])
            return 0
        return 1

    ############################################################################
    #Function Name  : createUserNode                                           #
    #Input          : k--> ssh key                                             #
    #               : cmd --> cmd to send to the terminal                      #
    #Return Value   : string -->output content before the prompt               #
    ############################################################################
    def createUserNode(self,graphDB,dataJson,lbl):
        ''' once I get the Users FB Json data have to create thuser node and
        related with their interest'''''
        labels=[]
        labels.append(lbl)
        add_tweet_query = """
            WITH {dataJson} AS data
            UNWIND data AS t
            MERGE (u {id:t.id})
            ON CREATE SET
                     """+   (('u:'+',u:'.join(labels)+",") if labels else '') +"""
                        u.name=t.name,
                        u.id=t.id,
                        u.hometown=t.hometown.name,
                        u.location=t.location.name
                    """ +   (("ON MATCH SET\n  u:"+',u:'.join(labels)) if labels else '') +"""
                    RETURN u
            """
        logger.debug("neo4j query: %s",add_tweet_query)
        #Send Cypher query.
        n=graphDB.cypher.execute(add_tweet_query,dataJson=dataJson)
        return n

    ############################################################################
    #Function Name  : getInterestNode                                          #
    #Input          : graphDB -> neo4j instance object                         #
    #               : ID -> unique string of a Node                            #
    #Return Value   : 1 on success, 0 on failure                               #
    ############################################################################
    def getInterestNode(self,graphDB,ID):
        ''' this query fetches the user details of the user and  will AI them to
        post the relevant tweets/instagram of their interest'''

        query = """ MATCH (u:user {id:{ID}})-[r]->(n:interest) RETURN
        {name:n.name,city:n.city,id:n.id,lat:n.latitude,lng:n.longitude,relation:type(r)} as nameCity """
        n = graphDB.cypher.execute(query,ID=ID)
        logger.info('getInterestNode query output:\n%s',n)
        #from py2neo.cypher import Record,RecordProducer,RecordList
        #n=RecordProducer(n)
        #n=n[0][0]
        #logger.info('getInterestNode put:%s',n)
        return n

    ############################################################################
    #Function Name  : getAllInterestNode                                          #
    #Input          : graphDB -> neo4j instance object                         #
    #               : ID -> unique string of a Node                            #
    #Return Value   : 1 on success, 0 on failure                               #
    ############################################################################
    def getAllInterestNode(self,graphDB):
        ''' this query fetches the user details of the user and  will AI them to
        post the relevant tweets/instagram of their interest'''

        query = ''' MATCH (n:interest) RETURN {name:n.name,city:n.city,id:n.id,
        lat:n.latitude,lng:n.longitude} as nameCity'''
        n = graphDB.cypher.execute(query)
        logger.info('getAllInterestNode query output:\n%s',n)
        #from py2neo.cypher import Record,RecordProducer,RecordList
        #n=RecordProducer(n)
        #n=n[0][0]
        #logger.info('getInterestNode put:%s',n)
        return n

    ############################################################################
    #Function Name  : execCreateRelQuery                                       #
    #Input          : k--> ssh key                                             #
    #               : cmd --> cmd to send to the terminal                      #
    #Return Value   : 1 on success, 0 on failure                               #
    ############################################################################
    def execCreateRelQuery(self,graphDB,params,ht):
        ''' creat & releate flavour of neo4j query
        '''
        passCnt = 0
        labels=['interest']
        labels.append(ht)
        query = """ MERGE (i {id:{k}}) ON CREATE SET
            """+(('i:'+',i:'.join(labels)+",") if labels else '')+"""
            i.id={k}, i.name={v}
            FOREACH(ignoreMe IN CASE WHEN trim({city}) <> "" THEN [1] ELSE [] END | SET i.city = {city} )
            FOREACH(ignoreMe IN CASE WHEN trim({country}) <> "" THEN [1] ELSE [] END | SET i.country = {country})
            FOREACH(ignoreMe IN CASE WHEN trim({longitude}) <> "" THEN [1] ELSE [] END | SET i.longitude = {longitude})
            FOREACH(ignoreMe IN CASE WHEN trim({latitude}) <> "" THEN [1] ELSE [] END | SET i.latitude = {latitude})
            return i"""
        n=graphDB.cypher.execute(query,params)
        logger.info('cypher query output:%s',n)
        if len(n): passCnt += 1

        rQuery = """ Match """'(u {id:{d}}), (i {id:{k}}) MERGE (u)-[:`'+params['type']+'`]->(i)' """
                  return i """
        n=graphDB.cypher.execute(rQuery,params)
        if len(n): passCnt += 1
        return passCnt

    ############################################################################
    #Function Name  : createInterestNode                                       #
    #Input          : k--> ssh key                                             #
    #               : cmd --> cmd to send to the terminal                      #
    #Return Value   : 1 on success, 0 on failure                               #
    ############################################################################
    def createInterestNode(self,graphDB,decodedFBJson,ht):
        ''' once I get the Users FB Json data have to create thuser node and
        related with their interest'''''
        execCnt = 0
        if 'work' in ht:
            keyIs='employer'
        elif 'education' in ht:
            keyIs='school'
        if isinstance(decodedFBJson[ht],list):
            for itm in decodedFBJson[ht]:
                logger.info("increateColgInterestNode: %s",itm)
                if itm.get('type') == None:
                        itm['type'] = keyIs
                params = {
                    'd' : decodedFBJson['id'],
                    'k' : itm[keyIs]['id'],
                    'v' : itm[keyIs]['name'],
                    'type' : itm['type']
                }
                for key in ['city','country','latitude','longitude']:
                    if key in itm[keyIs]:
                        tmp={key:itm[keyIs][key]}
                        params.update(tmp)
                    else:
                        tmp={key:''}
                        params.update(tmp)
                logger.info ("params:%s",params)
                execCnt += self.execCreateRelQuery(graphDB,params,ht)
        else:
            params = {
                'd' : decodedFBJson['id'],
                'k' : decodedFBJson[ht]['id'],
                'v' : decodedFBJson[ht]['name'],
                'type' : ht
            }
            for key in ['city','country','latitude','longitude']:
                    if key in decodedFBJson[ht]:
                        tmp={key:decodedFBJson[ht][key]}
                        params.update(tmp)
                    else:
                        tmp={key:''}
                        params.update(tmp)
            execCnt += self.execCreateRelQuery(graphDB,params,ht)
        return execCnt


################################################################################
