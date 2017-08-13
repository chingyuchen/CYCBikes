################################################################################
''' 
File: cmdlibrary.py
Author : Ching-Yu Chen

Description: cmdlibrary.py contains all the program classes of a designed 
telegram-bot. The list of corresponding commands and the name of classes are in 
the commandsmap.json. The class CmdLibrary contains the dict that map the 
commands to the classes.

'''
################################################################################

import abc
import telepot   
import telebot
from telebot import types
import json

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

    statefun = []
    check_cmd = []

#-------------------------------------------------------------------------------

    @staticmethod
    def check0(msg):
        
        '''
        check if the msg is a valid command for the program at state 0 
        '''

        return True

#-------------------------------------------------------------------------------

    @staticmethod
    def state0(user, args = None):

        '''
        The customized (given user) state 0 function for execution
        '''

        Start.bot.sendMessage(user, 'Hi, NAME! cycbikes helps you to find the \
            bikes station to pick up or drop off. Send /help for more\
            options')

#-------------------------------------------------------------------------------
        
    def __init__(self, bot, tb):
        
        '''
        the Start Class is initialized so the command execution will be operated
        by the given the bot and the tb object (telepot and telebot object). 
        '''

        Start.bot = bot
        Start.tb = tb
        Start.statefun = [Start.state0]
        Start.check_cmd = [Start.check0]

#-------------------------------------------------------------------------------        
    
    @staticmethod # Should be inherit
    def run(user, state, args=None):

        '''
        Execute the function of the program at the given state
        '''

        Start.statefun[state](user, args)
        state += 1
        if state is len(Start.statefun):
            return 0
        return state

################################################################################

class Default(PgmAbstract):
    
    ''' 
    "/default" command program. Ask the user whether to send current 
    location or choose the favorite pick up or drop off locations. Then use the
    respond message to find and send the station information.
    The default program is the standby running program.
    '''

    name = "/default"
    bot = None
    tb = None

    statefun = []
    check_cmd = []

    fav_dict = {}
    # {user, {'favP1'=location, 'favP2'=location, 'favP3'=location}}

#-------------------------------------------------------------------------------

    @staticmethod
    def check0(msg):

        '''
        check if the msg is a valid command for the program at state 0 
        '''
        
        return True

#-------------------------------------------------------------------------------

    @staticmethod
    def state0(user, args = None):
        
        '''
        The customized (given user) state 0 function for execution. The function
        will let user able to choose between 'share location', 'favPick' or 
        'favDrop' from the keyboard.
        '''

        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('share location', request_location=True)
        itembtn2 = types.KeyboardButton('favPick')
        itembtn3 = types.KeyboardButton('favDrop')
        markup.add(itembtn1)
        markup.add(itembtn2)
        markup.add(itembtn3)
        Default.tb.send_message(user, "default state0", reply_markup=markup)

#-------------------------------------------------------------------------------

    @staticmethod
    def check1(msg):

        '''
        check if the msg is a valid command for the program at state 1. If msg 
        is valid will move to state 1 function execution. Otherwise, 
        "error command" message will be sent.
        '''

        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is 'location':
            return True
        elif content_type is 'text':
            if msg['text'] == 'favPick' or msg['text'] == 'favDrop':
                return True
            else:
                return False
        else:
            return False

 #-------------------------------------------------------------------------------

    @staticmethod
    def state1(user, args = None):

        '''
        The customized (given user) state 1 function for execution
        '''

        # location 
            # pick up or drop off

        # favPick
            # change state and execute "/favP1"

        # favDrop 
            # change state and execute "/favDrop"

        Default.bot.sendMessage(user, 'state one execute')

#-------------------------------------------------------------------------------    
    
    def __init__(self, bot, tb):

        '''
        the Default Class is initialized so the command execution will be 
        operated by the given the bot and the tb object (telepot and telebot 
        object). 
        '''

        Default.bot = bot
        Default.tb = tb
        Default.statefun = [Default.state0, Default.state1]
        Default.check_cmd = [Default.check0, Default.check1]

#-------------------------------------------------------------------------------
    
    @staticmethod # Should be inherit
    def run(user, state, args=None):

        '''
        Execute the function of the program at the given state
        '''

        Default.statefun[state](user, args)
        
        state += 1
        if state is len(Default.statefun):
            return 0
        return state

################################################################################

class Help(PgmAbstract):

    ''' 
    "/help" command program. Send information of the commands to the user
    '''
    
    name = "/help"
    bot = None
    tb = None

    statefun = []
    check_cmd = []

#-------------------------------------------------------------------------------

    @staticmethod
    def check0(msg):
        
        '''
        check if the msg is a valid command for the program at state 0 
        '''

        return True

#-------------------------------------------------------------------------------

    @staticmethod
    def state0(user, args = None):

        '''
        The customized (given user) state 0 function for execution
        '''

        Start.bot.sendMessage(user, \
            '/default : use current location or top favorite location.\n \
            /map : use map to identify the searching location.\n \
            /addr : use address to identify the searching location.\n\
            /fav : show options of favorite location.\n\
            /addFav : add favorite locations.\n\
            /favDi : search the ith favorite drop off location.\n\
            /favPi : search the ith favorite pick up location.\n\
            /start : greeting!\n\
            /help : commands instructions')

#-------------------------------------------------------------------------------
        
    def __init__(self, bot, tb):
        
        '''
        the Help Class is initialized so the command execution will be operated
        by the given the bot and the tb object (telepot and telebot object). 
        '''

        Help.bot = bot
        Help.tb = tb
        Help.statefun = [Help.state0]
        Help.check_cmd = [Help.check0]

#-------------------------------------------------------------------------------        
    
    @staticmethod # Should be inherit
    def run(user, state, args=None):

        '''
        Execute the function of the program at the given state
        '''

        Help.statefun[state](user, args)
        state += 1
        if state is len(Help.statefun):
            return 0
        return state

################################################################################

class CmdLibrary(object):

    '''
    CmdLibrary is a object that store all the commands and the corresponding 
    program class of a designed telegram bot.
    '''

    def __init__(self, bot, tb):
        
        '''
        Initialized the CmdLibrary object with the given bot and tb (telepot and 
        telebot object), so the stored classes pgm will be executed and 
        communicate with the users through bot and tb.
        '''

        # The object sends and receives messages from the users.
        self.bot = bot

        # The object that show customized keyboard to the user.
        self.tb = tb

        # The dict that maps the commands to the corresponding pgm class name.
        self.command_class = {}

        # The dict that maps the commands to the corresponding pgm class.
        self.command_libarary = {}

        with open('commandsmap.json', 'r') as fp:
            self.command_class = json.load(fp)

        for key in self.command_class:
            self.command_libarary[key] = \
            eval(self.command_class[key])(self.bot, self.tb)
    
    
################################################################################

if __name__ == "__main__":
    
    ''' for testing
    '''
    TOKEN = input("Enter the TOKEN: ") 
    bot = telepot.Bot(TOKEN)
    tb = telebot.TeleBot(TOKEN)
    testCmdLibrary = CmdLibrary(bot, tb)
    
    #help = testCmdLibrary.Help()
    #help.run()

