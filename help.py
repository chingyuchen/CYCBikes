################################################################################
'''
File: help.py
Author: Ching-Yu Chen

Description:
Help pgm send the commands instruction to the users.

'''
################################################################################

import abc
import telepot      

################################################################################

class PgmAbstract(object):

    ''' 
    Abstract class of the pgm of the bot. 
    '''

    # pgm execute command
    name = ""
    
    # object of telepot, sending and receiving messages from telegram users
    bot = None
    
    # object of telepot, shows customized keyboard to telegram users
    tb = None

    # function list to execute at different state
    statefun = []

    # list of functions to check valid command at different state
    check_cmd = []

    __metaclass__ = abc.ABCMeta

    def check_name(self):
        if self.name is None:
            raise NotImplementedError('Subclasses must define name')

################################################################################

class Help(PgmAbstract):

    ''' 
    "/help" command program. Send information of the commands to the user.
    '''
    
    name = "/help"
    bot = None

    INFORM = 0
    END = -1

    statefun = []
    check_cmd = []

#-------------------------------------------------------------------------------

    @staticmethod
    def check_start(msg):
        
        '''
        Return true if the msg is a valid command for the program at start state.
        Otherwise, return false.
        '''

        return True

#-------------------------------------------------------------------------------

    @staticmethod
    def state_inform(user, msg=None, args = None):

        '''
        The inform state function. Send commands instruction to the users and
        return the enum of the end state.
        '''

        Help.bot.sendMessage(user, \
            '/default : use current location or favorite locations.\n'
            '/addr : use address to identify the searching location.\n'
            '/fav : show current list of favorite locations.\n'
            '/editFav : edit favorite locations.\n'
            '/start : greeting!\n'
            '/help : commands instructions')

        return [Help.END, None]

#-------------------------------------------------------------------------------
        
    def __init__(self, bot, tb, sqlfile):
        
        '''
        the Help Class is initialized so the command execution will be operated
        by the given the bot object (telepot object). 
        '''

        Help.bot = bot
        Help.statefun = [Help.state_inform]
        Help.check_cmd = [Help.check_start]

#-------------------------------------------------------------------------------        
    
    @staticmethod # Should be inherit
    def run(user, state, msg=None, args=None):

        '''
        Execute the function of the program at the given state
        '''

        return Help.statefun[state](user, msg, args)
        
