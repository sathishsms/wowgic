from pyspark import SparkContext
from pyspark.ml.feature import HashingTF, Tokenizer
from pyspark.mllib.classification import LogisticRegressionWithLBFGS
from pyspark.mllib.evaluation import BinaryClassificationMetrics
from pyspark.mllib.util import MLUtils
import sys
sys.path.append('../common')
import loggerRecord
logger =  loggerRecord.get_logger()
#http://www.brettdangerfield.com/post/realtime_data_tag_cloud/

class sparkInt:

    def connect(self):
        #creating a standalone spark context
        self.sc = SparkContext("local", "wowgicApp")



    def wowFieldTrueOrFalse(self,data):
        ''' Parallelized collections are created by calling SparkContext's parallelize method
        '''
        # Load tweets into Spark for analysis
        allMediasRDD = self.sc.parallelize(data)
        # Infer the schema, and register the DataFrame as a table.
        #df = sqlContext.createDataFrame(data)
        #df = sc.read.json(data)
        #logger.debug("spark data frame:%s",df.printSchema())
        # Set up filter to only get tweets from the last week
        #def tokenzier(media):
        #    if 'text' in media:
        #        words=media['text'].split(' ')
        #        return words
        # Filter tweets to get rid of those who either have no hashtags or are too old
        #filteredTweetsRDD = allMeediasRDD.map(tokenzier)


        posWords = self.sc.textFile("others/dictionaries/pos-words.txt").collect()
        logger.debug('text file contains:%s',posWords)
        def myFunc2(t):
            if 'text' in t:
                words=t['text'].split(' ')
                for word in words:
                    if word.lower() in posWords:
                        output = {'wowField':True}
                    else:
                        output = {'wowField':False}
                    t.update(output)
            return t
        tagsRDD = allMediasRDD.map(myFunc2).collect()
        #logger.debug('mongo iphone %s',tagsRDD.collect())
        #pairs = lines.map(lambda s: (s, 1))
        #counts = pairs.reduceByKey(lambda a, b: a + b)
        #logger.debug('God leads323232 %s',counts.count())
        #filteredTweetsRDD = allTweetsRDD.filter(lambda t: t['id'] > 0)
        #logger.debug('God leads3')

        #words = allTweetsRDD.tweets_by_lang = tweets['lang'].value_counts()

        # Count each word in each batch
        #pairs = words.map(lambda word: (word, 1))
        #wordCounts = pairs.reduceByKey(lambda x, y: x + y)
        logger.debug('spark filteredTweetsRDD: %s',tagsRDD)
        return tagsRDD

    def removeUnwantedJsonFields(self,ID,data):
        ''' This function removes unwanted json files and stores into the mongoDb database
        '''
        #Load tweets into RDD for analysis
        data_raw = self.sc.parallelize(data)
        # Parse JSON entries in dataset
        data = data_raw.map(lambda feed: json.loads(feed))
        # Extract relevant fields in dataset -- category label and text content
        data_pared = data.map(lambda feed: (feed['label'], feed['text']))

    def __del__(self):
        self.sc.stop()