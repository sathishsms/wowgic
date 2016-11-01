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

stop_words = set(stopwords.words('english'))
#word_set = []
sentList=[]
lemmatizer = WordNetLemmatizer()
onlySentence = {} 


class topicModel:
    '''
    def __init__(self, feeds):
        self.feeds = feeds

    def __iter__(self):
        dictionary = self.dictionary
        for tweet in self.feeds:
            if 'text' in tweet:
                sent = tweet['text']
                filtered_sentence = self.prepareSentence(sent)
                yield dictionary.doc2bow(filtered_sentence)
    
    def prepareSentence(self, sent):
        sent=' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",sent).split())
        sent =sent.replace("RT", "", 1)
        filtered_sentence1=[]
        word_tokens = nltk.word_tokenize(sent)
        for w in word_tokens:
            if w not in stop_words:
                lemWord = lemmatizer.lemmatize(w)
                lemWord = lemWord.lower()
                filtered_sentence1.append(lemWord)
        return filtered_sentence1
    
    def createDictionary(self):
        sentList = []
        
        for tweet in self.feeds:
            if 'text' in tweet:
                sent = tweet['text']
                #filtered_sentence = self.prepareSentence(sent)
                sent=' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",sent).split())
                sent =sent.replace("RT", "", 1)
                filtered_sentence1=[]
                word_tokens = nltk.word_tokenize(sent)
                for w in word_tokens:
                    if w not in stop_words:
                        lemWord = lemmatizer.lemmatize(w)
                        lemWord = lemWord.lower()
                        filtered_sentence1.append(lemWord)
            sentList.append(set(filtered_sentence1))

        self.sentList = sentList 
        print('create dict sent length',len(self.sentList))
        dictionary = corpora.Dictionary(sentList)
        print(dictionary.token2id)
        self.dictionary = dictionary
        return dictionary
    
    def createLSIModel(self,corpus):
        corpus = [self.dictionary.doc2bow(text) for text in self.sentList]
        print('new corpus length ',len(corpus))
        lsi = models.LsiModel(corpus, id2word=self.dictionary, num_topics=200)
        index = similarities.MatrixSimilarity(lsi[corpus])
        for tweet in self.feeds:
            if 'text' in tweet:
                sent = tweet['text']
                #filtered_sentence = self.prepareSentence(sent)
                sent=' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",sent).split())
                sent =sent.replace("RT", "", 1)
                word_tokens = nltk.word_tokenize(sent)
                filtered_sentence = ''
                for w in word_tokens:
                    if w not in stop_words:
                        lemWord = lemmatizer.lemmatize(w)
                        lemWord = lemWord.lower()
                        filtered_sentence += lemWord+' '
                vec_bow = self.dictionary.doc2bow(filtered_sentence.split())
                vec_lsi = lsi[vec_bow] # convert the query to LSI space
                sims = index[vec_lsi] # perform a similarity query against the corpus
                #print(list(enumerate(sims))) # print (document_number, document_similarity) 2-tuples
                sims = sorted(enumerate(sims), key=lambda item: -item[1])
                #print(sims)
                print('-------------------')
                print(filtered_sentence)
                print('----------------------')
                for sim in sims:
                    if sim[1] > 0.50:
                        indexKey = sim[0]
                        if self.feeds[indexKey]:        
                            print(sim[1])
                            print('********')
                            print(self.feeds[indexKey]['id'])
                            print(self.feeds[indexKey].get('text'))
                            print('********')                       
                            


'''
    
    def extract_entity_names(f, tweets):
        #r = requests.get('http://104.251.215.131:8080/displayFeeds?collId=112621745415708&count=100&lastTimeStamp=1468055698')
        #tweets = r.json()
        #print('just to understand123....',tweets);
        jer = 0
        for tweet in tweets:
            if 'text' in tweet:
                jer+=1
                #print('hello tweets',jer)
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
            print('\n')
            print(filtered_sentence)
            
            sentList.append(set(filtered_sentence))
        #word_set =set(word_set)
        #print(len(word_set))
        print('extract entity namesss',len(sentList))
        frequency = defaultdict(int)
        for text in sentList:
             for token in text:
                frequency[token] += 1
                #sentList = [[token for token in text if frequency[token] > 1] for text in sentList]
        dictionary = corpora.Dictionary(sentList)
        print(dictionary.token2id)
        dictionary.save('/tmp/deerwester.dict')  # store the dictionary, for future reference
        #print(dictionary.token2id)
        for s in sentList:
            print('sntlist',s)
        print('len sentlist', len(sentList))
    
        corpus = [dictionary.doc2bow(text) for text in sentList]
        corpora.MmCorpus.serialize('/tmp/deerwester.mm', corpus)  # store to disk, for later use
        print(corpora)
        print('corpus length ',len(corpus))
        rew = json.dumps(tweets, sort_keys=True, indent=4, default=json_util.default)
        #tweets= json.dump(tweets, sort_keys=True, indent=4, default=json_util.default)
        with open('tweets.json', 'w') as f:
            json.dump(rew, f)
        
        dictionary = corpora.Dictionary.load('/tmp/deerwester.dict')
        corpus = corpora.MmCorpus('/tmp/deerwester.mm') # comes from the first tutorial, "From strings to vectors"
        print(corpus)

        lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=200)
        #print(vec_lsi)
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
                        #print(w)
                        #print(lemmatizer.lemmatize(w))
                        lemWord = lemmatizer.lemmatize(w)
                        lemWord = lemWord.lower()
                        sent+=lemWord+' '
                vec_bow = dictionary.doc2bow(sent.split())
                vec_lsi = lsi[vec_bow] # convert the query to LSI space
                
                sims = index[vec_lsi] # perform a similarity query against the corpus
                #print(list(enumerate(sims))) # print (document_number, document_similarity) 2-tuples
                sims = sorted(enumerate(sims), key=lambda item: -item[1])
                #print('hello',sims) # print sorted (document number, similarity score) 2-tuples
                print('\n\n----------------------')
                print(doc)
                print('----------------------')
                for sim in sims:
                    if sim[1] > 0.50:
                        indexKey = sim[0]
                        if tweets[indexKey]:
                            print(sim[1])
                            print('********')
                            print(tweets[indexKey]['id'])
                            print(tweets[indexKey].get('text'))
                            print('********')'''
                
