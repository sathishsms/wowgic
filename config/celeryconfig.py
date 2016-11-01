import os
from celery.schedules import crontab

CELERY_BROKER_URL='amqp://guest@localhost//'
CELERY_RESULT_BACKEND = 'mongodb://localhost:27017/'
CELERY_ACKS_LATE = True
CELERY_REDIRECT_STDOUTS_LEVEL = 'DEBUG'
CELERY_TRACK_STARTED = True
CELERY_MONGODB_BACKEND_SETTINGS = {
        'database': 'wowgicflaskapp',
        'taskmeta_collection': 'my_taskmeta_collection',
    }
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
#CELERY_TASK_SERIALIZER='json'
#CELERY_RESULT_SERIALIZER='json'
#CELERY_TIMEZONE='Europe/Oslo'
CELERY_ENABLE_UTC=True
IP = os.uname()[1]
APP_PORT = '8080'
NEO4J_IP='127.0.0.1'
MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = '27017'
MONGODB_USERNAME = 'admin'
MONGODB_PASSWORD = '8ygFBXZHeIW6'
#Neo4j
NEO4J_USERNAME = 'neo4j'
NEO4J_PASSWORD = 'admin'
LOGGER_NAME='wowgic_dev'
MAX_TWEETS = 100
#CELERYBEAT_SCHEDULE =   {# Executes every Monday morning at 7:30 A.M
#    'getAllInterestNode_every15mins': {
#    'task': 'tasks.getAllInterestNode',
#    'schedule': crontab(minute='*/15'),
#        },
#    }
CELERYBEAT_SCHEDULE_FILENAME = "/tmp/wowgic_celerySchedule.conf"

#remove this after placing into database
#twitter keys key should named genericly so tat retriuvel mechanism is faster & prioritised
T_CONSUMER_KEY= 'HwvpHtsPt3LmOZocZXwtn72Zv'
T_CONSUMER_SECRET = 'afVEAR0Ri3ZluVItqbDi0kfm7BHSxjwRXbpw9m9kFhXGjnzHKh'
T_ACCESS_TOKEN = '419412786-cpS2hDmR6cuIf8BD2kSSri0BAWAmXBA3pzcB56Pw'
T_ACCESS_SECRET = 'pRx5MNKkmxyImwuhUFMNVOr1NrAWcRmOGUgGTLVYFAjsJ'
SATHISH_TOKEN_SECRET = 'iMGjh3MkFGS0yudhe9SadUH5Dxwk9ndiAPrXTE6ivyqr8'
SATHISH_TOKEN = '56276642-bOJMDDbpy7B2gCryxMfWgMDGrxgP9NnPJzgMV5fTS'
#VIVEK_TOKEN_SECRET = '8h1T0x2237pmUWA1Hg7QSi3sPRQt9WN6Okg6A0dMSYvRL'
#VIVEK_TOKEN = '2976291321-gfESJJC7xBvZk0mv8tbkbYgoMseQChUBwPslbYc'

#facebook tokens
FACEBOOK_APP_ID = '575443062564498'
FACEBOOK_APP_SECRET = '3112a499e27dcd991b9869a5dd5524c0'
FBTOKEN = 'EAAILXMdVJpIBAIXnXUIrOyvhsLhutvcLTQQpeIdKOcbW16oQMHbfdkuz7EulzYw1ZBtvpOTUZAQDjT2M5Q7E65McmYXj4mLZAz8jNe2IQwOcbyQgyf58SdKdLjED83KZAIgwhDNhdqk2XGChGNmMcUszbAETL1MGoJXQS9B64AZDZD'