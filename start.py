################################################################################
'''
File: start.py
Author: Ching-Yu Chen

Description:
Start pgm greets to the CYCBikes user.

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
    name = "/start"
    
    # object of telepot, sending and receiving messages from telegram users
    bot = None

    # function list to execute at different state
    statefun = []

    # list of functions to check valid command at different state
    check_cmd = []

    __metaclass__ = abc.ABCMeta

    def check_name(self):
        if self.name is None:
            raise NotImplementedError('Subclasses must define name')

################################################################################

class Start(PgmAbstract):

    ''' 
    "/start" command program. Send greeting message. 
    '''

    name = "/start"
    bot = None
    tb = None

    GREETING = 0
    END = -1

    statefun = []
    check_cmd = []

#-------------------------------------------------------------------------------

    @staticmethod
    def check_start(msg):
        
        '''
        Return true if the command is valid for start state. Otherwise,
        return false. 
        '''

        return True

#-------------------------------------------------------------------------------

    @staticmethod
    def state_greeting(user, msg, args=None):

        '''
        The greeting state function. Send greeting to the user and return enum 
        of the end state function. args provide the user name.
        '''

        if args is None:
            name = msg['from']['first_name']
            args = [name, ]

        Start.bot.sendMessage(user, 'Hi, {first_name}! CYCBikes helps you to '
            'find the bike-share station to pick up or drop off bikes. Send '
            '/help for more options'.format(first_name=args[0]))

        return [Start.END, None]

#-------------------------------------------------------------------------------
        
    def __init__(self, bot, tb, sqlfile):
        
        '''
        the Start Class is initialized so the command execution will be operated
        by the given the bot object (telepot object). 
        '''

        Start.bot = bot

        Start.statefun = [Start.state_greeting]
        Start.check_cmd = [Start.check_start]

#-------------------------------------------------------------------------------        
    
    @staticmethod # Should be inherit
    def run(user, state, msg=None, args=None):

        '''
        Execute the function of the program at the given state and return the 
        next state
        '''

        return Start.statefun[state](user, msg, args)
        
################################################################################