import commands
DEBUG = True
APP_DEBUG = True
PROPAGATE_EXCEPTIONS = True
#SECRET_KEY = os.environ.get('SECRET_KEY','\xfb\x13\xdf\xa1@i\xd6>V\xc0\xbf\x8fp\x16#Z\x0b\x81\xeb\x16')
#Get the environment information we need to start the server
#HOST_NAME = os.environ.get('HOSTNAME','localhost')
APP_NAME = 'wowgicFlaskApp'
IP = commands.getstatusoutput('hostname -i')[1]
NEO4J_IP='127.0.0.1'
APP_PORT = '8080'
LOGGER_NAME='wowgic_dev'
AUTH_EXPIRY_SECS = 1800
#/home/wowgic/wowgic/adminMongo
