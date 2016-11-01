#! /usr/bin/python
import logging
import sys
#===============================================================================
# Create a logging objects
#===============================================================================
#let force the name whichever invokes it doesnt matter for me
#__name__ = 'logic+magic is our wowgic'

def loggerInit(logFileName,lvl='error'):
    '''Handler for a streaming logging request. This basically logs the record using whatever logging policy is
    configured locally'''

    LEVELS = {'debug':logging.DEBUG,
            'info':logging.INFO,
            'warning':logging.WARNING,
            'error':logging.ERROR,
            'critical':logging.CRITICAL}

    lvl = LEVELS.get(lvl, logging.NOTSET)
    # create logger with 'OCPM Loggy Tool'
    logging.basicConfig(level=lvl)
    logger = logging.getLogger('wowgic_dev')
    #logger = logging.getLogger('wowgic_dev')
    # create file handler which logs even debug messages
    fh = logging.FileHandler(logFileName)
    fh.setLevel(lvl)
    # create console handler with a higher log level
    #ch = logging.StreamHandler()
    ch = logging.StreamHandler(sys.stdout)
    ##ch.setLevel(logging.ERROR)
    ch.setLevel(lvl)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(funcName)s %(module)s:%(lineno)d - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    #logger.addHandler(ch)
    #print logger
    return logger,fh

def get_logger():
    ''' logger for wowgic is returned here a global method to do that as of now we are going to use single file to write
    our log statements in case if required multiple files modify this method with help passing args'''
    return logging.getLogger('wowgic_dev')

################################################################################
