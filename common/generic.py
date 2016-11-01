#! /usr/bin/python
import re,sys,os
import json
import itertools
import loggerRecord,globalS
from time import gmtime, strftime, localtime
logger =  loggerRecord.get_logger()

class generic():
    ''' this class will have generic methods common to linux,neo4J,wowgic etc. Creating a seperate class so that in case
    of future requirement this can be imported and readily used'''

    ############################################################################
    #Function Name  : parseIpfromOutput                                        #
    #Input          : string                                                   #
    #Return Value   : IP's list                                                #
    ############################################################################
    def parseIpfromOutput(self,buf):
        ''' this functions picks out the IP's from buffer string and returns in
        the form of list'''

        ipArr = re.findall("\d+.\d+.\d+.\d+",buf)
        logger.debug("IPs are %s",ipArr)
        return ipArr

    ############################################################################
    #Function Name  : dumpclean                                                #
    #Input          : dict variable                                            #
    #Return Value   : none                                                     #
    ############################################################################
    def dumpclean(obj):
        ''' so far this copied function is not used but placing it for future
        representation of python dictionaries'''

        logger.debug('Python Dictionary Printing start')
        if type(obj) == dict:
            for k, v in obj.items():
                if hasattr(v, '__iter__'):
                    logger.debug('%s',k)
                    dumpclean(v)
                else:
                    logger.debug('%s : %s', (k, v))
        elif type(obj) == list:
            for v in obj:
                if hasattr(v, '__iter__'):
                    dumpclean(v)
                else:
                    logger.debug('%s', v)
        else:
            logger.debug('%s', obj)
        logger.debug('Python Dictionary Printing END')

    ############################################################################
    #Function Name  : dictDumper #
    #Input          :  #
    #Return Value   :  #
    ############################################################################
    def dictDumper(self,obj, nested_level=0, output=sys.stdout):
        ''' recursive function for internal debugging purpose
        source:online'''
        spacing = '   '
        if type(obj) == dict:
            print >> output, '%s{' % ((nested_level) * spacing)
            for k, v in obj.items():
                if hasattr(v, '__iter__'):
                    print >> output, '%s%s:' % ((nested_level + 1) * spacing, k)
                    self.dictDumper(v, nested_level + 1, output)
                else:
                    print >> output, '%s%s: %s' % ((nested_level + 1) * spacing, k, v)
            print >> output, '%s}' % (nested_level * spacing)
        elif type(obj) == list:
            print >> output, '%s[' % ((nested_level) * spacing)
            for v in obj:
                if hasattr(v, '__iter__'):
                    self.dictDumper(v, nested_level + 1, output)
                else:
                    print >> output, '%s%s' % ((nested_level + 1) * spacing, v)
            print >> output, '%s]' % ((nested_level) * spacing)
        else:
            print >> output, '%s%s' % (nested_level * spacing, obj)

    ############################################################################
    #Function Name  : dateTimeFields                                           #
    #Input          : none                                                     #
    #Return Value   : str contains local date & time                           #
    ############################################################################
    def dateTimeFields(self):
        ''' the way how I need the current timestamp which is to be used for file
        names and across all the log files as well'''

        return strftime("%Y%m%d_%H%M%S", localtime())


    ############################################################################
    #Function Name  : connCheck                                                #
    #Input          : ipAddress-> ip address of the machine                    #
    #Return Value   : 1 0n failure 0 on success                                #
    ############################################################################
    def connCheck(self,ipAddress):
        ''' issue ping command and check the reachability of the machine. So that
        basic health checkup is administrated before doing ssh'''

        response = os.system("ping -c 1 -w 10 " + ipAddress)
        #and then check the response...
        if response == 0:
          logger.info('hostname# %s is up!',ipAddress)
          return 0
        logger.error('hostname# %s is down!',ipAddress)
        return 1

################################################################################
