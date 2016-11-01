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
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from gensim import corpora, models, similarities
from collections import defaultdict
from bson import json_util
import json
import requests
import re
import sys
sys.path.append('common')
import loggerRecord,globalS
logger =  loggerRecord.get_logger()

stop_words = set(stopwords.words('english'))
#word_set = []
lemmatizer = WordNetLemmatizer()
onlySentence = {} 


class topicModel:
    ''' gensim topic modelling - 
        Cration of corpus creation & dictionary creation should in written in iter methods <placeholder>
    '''
    def __init__(self, feeds):
        logger.debug('who invoked me ? hey u - %s',__name__)
        self.feeds = feeds
        self.dictionary = {}
        self.sentList=[]


    def __iter__(self):
        ''' The Iteration Protocol. is invoked while calling the class obj in for loop
        '''
        logger.debug('in iteration function')
        for tweet in self.feeds:
            if 'text' in tweet:
                sent = tweet['text']
                filtered_sentence = self.prepareSentence(sent)
                yield self.dictionary.doc2bow(filtered_sentence)
        logger.info('end of iteration function')

    def prepareSentence(self, sent):
        ''' lematizing the words and prepare the sentences
        '''
        #logger.debug('Entering function')
        sent=' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",sent).split())
        sent =sent.replace("RT", "", 1)
        filtered_sentence1=[]
        word_tokens = nltk.word_tokenize(sent)
        pos_tag = nltk.pos_tag(word_tokens)
        logger.debug(pos_tag)
        for w in word_tokens:
            if w not in stop_words:
                lemWord = lemmatizer.lemmatize(w)
                lemWord = lemWord.lower()
                filtered_sentence1.append(lemWord)
        #logger.info('exiting function')
        return filtered_sentence1

    def tryPos(self):
        for tweet in self.feeds:
            if 'text' in tweet:
                sent = tweet['text']
                filtered_sentence1=[]
                word_tokens = nltk.word_tokenize(sent)
                pos_tag = nltk.pos_tag(word_tokens)
                allowed_word_types = ["N","V"]
                print(pos_tag)
                for w in pos_tag:
                    '''print(w[1][0])
                    print('\n')'''
                    if w[1][0] in allowed_word_types:
                        filtered_sentence1.append(w[0].lower())
                logger.debug('---------------------')        
                logger.debug(' %s',sent)
                logger.debug(' %s',filtered_sentence1)
                logger.debug('**********************')
    
    def createDictionary(self, keyword):
        ''' The mapping between the questions and ids is called a dictionary
        '''
        #logger.debug('Entering function')
        for tweet in self.feeds:
            if 'text' in tweet:
                sent = tweet['text']
                #filtered_sentence = self.prepareSentence(sent)
                #call the prepareSentence function <placeholder>
                sent=' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",sent).split())
                sent =sent.replace("RT", "", 1)
                filtered_sentence1=[]
                word_tokens = nltk.word_tokenize(sent)
                for w in word_tokens:
                    if w not in stop_words and w != keyword:
                        lemWord = lemmatizer.lemmatize(w)
                        lemWord = lemWord.lower()
                        filtered_sentence1.append(lemWord)
            self.sentList.append(set(filtered_sentence1))

        #logger.debug('create dict sent length %s',len(self.sentList))
        # to create unique dictionary words
        self.dictionary = corpora.Dictionary(self.sentList)
        #logger.debug(self.dictionary.token2id)
        #self.dictionary = dictionary
        #logger.info('exiting function')
        return self.dictionary

    def createLSIModel(self,corpus,feeds = '', keyword =''):
        ''' actually convert tokenized documents to vectors
        '''
        #corpus = [self.dictionary.doc2bow(text) for text in self.sentList]
        lsi = models.LsiModel(corpus, id2word=self.dictionary,num_topics=30)
        index = similarities.MatrixSimilarity(lsi[corpus])
        #initialising an array which store the similarity tweets
        similarTweet_Id = []
        similarTweet_Ratio = []
        ogTweets = 0
        similarTweetId_parentId = []
        if feeds == '':
            feeds = self.feeds 
        #logger.debug('new corpus length :%s ',len(feeds))
        for tweet in feeds:
            if tweet['id'] not in similarTweet_Id:
                if 'text' in tweet:
                    ogTweets += 1
                    #logger.debug('chelloi tweet text :%s', tweet) # logger.debug (document_number, document_similarity) 2-tuples
                    #filtered_sentence = self.prepareSentence(sentence)
                    #call the prepareSentence function <placeholder>
                    sentence=' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",tweet['text']).split())
                    sentence =sentence.replace("RT", "", 1)
                    word_tokens = nltk.word_tokenize(sentence)
                    filtered_sentence = ''
                    for w in word_tokens:
                        if w not in stop_words and w != keyword:
                            lemWord = lemmatizer.lemmatize(w)
                            lemWord = lemWord.lower()
                            filtered_sentence += lemWord+' '
                    '''
                    logger.debug('\n\n\n\n----------------Actual sentence------------')
                    logger.debug(tweet['text'])
                    logger.debug('----------lemmatized sentence ---------%s',keyword)
                    
                    logger.debug(filtered_sentence)
                    logger.debug(len(filtered_sentence.split()))
                    '''
                    if len(filtered_sentence.split()) >= 4:
                    
                        vec_bow = self.dictionary.doc2bow(filtered_sentence.split())
                        vec_lsi = lsi[vec_bow] # convert the query to LSI space
                        sims = index[vec_lsi] # perform a similarity query against the corpus
                        #logger.debug(list(enumerate(sims))) # logger.debug (document_number, document_similarity) 2-tuples
                        sims = sorted(enumerate(sims), key=lambda item: -item[1])
                        #logger.debug(sims)
                        '''
                        logger.debug('\n\n\n\n----------------Start title------------')
                        logger.debug(tweet['text'])
                        logger.debug('----------titlke End ---------')
                        
                        for sim in sims:
                            if sim[1] > 0.70 and sim[1] <= 0.99:
                                indexKey = sim[0]
                                if self.feeds[indexKey]:
                                    similarTweetId_parentId.append(tweet['id']) # parent id
                                    similarTweet_Id.append(feeds[indexKey]['id']) #current twitter id2word
                                    similarTweet_Ratio.append(sim[1]) #probility value
                                    
                                    logger.debug('******** sims[0]%s',sim[0])
                                    logger.debug(sim[1])
                                    logger.debug(self.feeds[indexKey]['id'])
                                    logger.debug(self.feeds[indexKey].get('text'))
                                    logger.debug('=========')'''
        '''
        logger.debug('totoal no tweets: %s, Total no of parent tweets: %s, Total no of child tweets: %s',len(self.feeds), ogTweets,len(similarTweet_Id))
        logger.debug('length of id : %s, ratio : %s, parentId : %s', len(similarTweet_Id),len(similarTweet_Ratio),len(similarTweetId_parentId))'''
        similarTweet = [similarTweet_Id,similarTweet_Ratio,similarTweetId_parentId]
      #  logger.info('similarTweets wrt to corpus: %s',similarTweet)
        return similarTweet
'''
    
    def extract_entity_names(f, tweets):
        #r = requests.get('http://104.251.215.131:8080/displayFeeds?collId=112621745415708&count=100&lastTimeStamp=1468055698')
        #tweets = r.json()
        #logger.debug('just to understand123....',tweets);
        jer = 0
        for tweet in tweets:
            if 'text' in tweet:
                jer+=1
                #logger.debug('hello tweets',jer)
                filtered_sentence = []
                sent = tweet['text']
                sent=' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",sent).split())
                sent =sent.replace("RT", "", 1)
                word_tokens = nltk.word_tokenize(sent)
                for w in word_tokens:
                    if w not in stop_words:
                        lemWord = lemmatizer.lemmatize(w)
                        lemWord = lemWord.lower()
                        #word_set.append(lemWord)
                        filtered_sentence.append(lemWord)
            onlySentence[tweet['id']] = filtered_sentence
            logger.debug('\n')
            logger.debug(filtered_sentence)
            
            sentList.append(set(filtered_sentence))
        #word_set =set(word_set)
        #logger.debug(len(word_set))
        logger.debug('extract entity namesss',len(sentList))
        frequency = defaultdict(int)
        for text in sentList:
             for token in text:
                frequency[token] += 1
                #sentList = [[token for token in text if frequency[token] > 1] for text in sentList]
        dictionary = corpora.Dictionary(sentList)
        logger.debug(dictionary.token2id)
        dictionary.save('/tmp/deerwester.dict')  # store the dictionary, for future reference
        #logger.debug(dictionary.token2id)
        for s in sentList:
            logger.debug('sntlist',s)
        logger.debug('len sentlist', len(sentList))
    
        corpus = [dictionary.doc2bow(text) for text in sentList]
        corpora.MmCorpus.serialize('/tmp/deerwester.mm', corpus)  # store to disk, for later use
        logger.debug(corpora)
        logger.debug('corpus length ',len(corpus))
        rew = json.dumps(tweets, sort_keys=True, indent=4, default=json_util.default)
        #tweets= json.dump(tweets, sort_keys=True, indent=4, default=json_util.default)
        with open('tweets.json', 'w') as f:
            json.dump(rew, f)
        
        dictionary = corpora.Dictionary.load('/tmp/deerwester.dict')
        corpus = corpora.MmCorpus('/tmp/deerwester.mm') # comes from the first tutorial, "From strings to vectors"
        logger.debug(corpus)

        lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=200)
        #logger.debug(vec_lsi)
        index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it
        index.save('/tmp/deerwester.index')
        index = similarities.MatrixSimilarity.load('/tmp/deerwester.index')
        for tweet in tweets:
            if 'text' in tweet:
                doc = tweet['text']
                doc=' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",doc).split())
                doc =doc.replace("RT", "", 1)
                word_tokens = nltk.word_tokenize(doc)
                sent = ''
                for w in word_tokens:
                    if w not in stop_words:
                        #logger.debug(w)
                        #logger.debug(lemmatizer.lemmatize(w))
                        lemWord = lemmatizer.lemmatize(w)
                        lemWord = lemWord.lower()
                        sent+=lemWord+' '
                vec_bow = dictionary.doc2bow(sent.split())
                vec_lsi = lsi[vec_bow] # convert the query to LSI space
                
                sims = index[vec_lsi] # perform a similarity query against the corpus
                #logger.debug(list(enumerate(sims))) # logger.debug (document_number, document_similarity) 2-tuples
                sims = sorted(enumerate(sims), key=lambda item: -item[1])
                #logger.debug('hello',sims) # logger.debug sorted (document number, similarity score) 2-tuples
                logger.debug('\n\n----------------------')
                logger.debug(doc)
                logger.debug('----------------------')
                for sim in sims:
                    if sim[1] > 0.50:
                        indexKey = sim[0]
                        if tweets[indexKey]:
                            logger.debug(sim[1])
                            logger.debug('********')
                            logger.debug(tweets[indexKey]['id'])
                            logger.debug(tweets[indexKey].get('text'))
                            logger.debug('********')'''
                
