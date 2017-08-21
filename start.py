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
        check if the msg is a valid command for the program at state 0 
        '''

        return True

#-------------------------------------------------------------------------------

    @staticmethod
    def state_greeting(user, msg=None, args=None):

        '''
        The customized (given user) state 0 function for execution. Return the
        state increment.
        '''

        Start.bot.sendMessage(user, 'Hi, NAME! cycbikes helps you to find the'
        ' bikes station to pick up or drop off. Send /help for more options')

        return [Start.END, None]

#-------------------------------------------------------------------------------
        
    def __init__(self, bot, tb, sqlfile):
        
        '''
        the Start Class is initialized so the command execution will be operated
        by the given the bot and the tb object (telepot and telebot object). 
        '''

        Start.bot = bot
        Start.tb = tb

        Start.statefun = [Start.state_greeting]
        Start.check_cmd = [Start.check_start]

#-------------------------------------------------------------------------------        
    
    @staticmethod # Should be inherit
    def run(user, state, msg=None, args=None):

        '''
        Execute the function of the program at the given state and return the 
        next state
        '''

        return Start.statefun[state](user, args)
        
################################################################################