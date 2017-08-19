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

        Start.bot.sendMessage(user, 'Hi, NAME! cycbikes helps you to find the \
            bikes station to pick up or drop off. Send /help for more\
            options')

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

    REQUEST = 0
    RESPOND = 1
    END = -1

    statefun = []
    check_cmd = []

    fav_dict = {}
    # {user, [[favp1, favp2, favp3] [favd1, favd2, favd3]]}

#-------------------------------------------------------------------------------

    @staticmethod
    def check_start(msg=None):

        '''
        check if the msg is a valid command for the program at state 0 
        '''
        
        return True

#-------------------------------------------------------------------------------

    @staticmethod
    def state_request(user, msg=None, args=None):
        
        '''
        The customized (given user) state 0 function for execution. The function
        will let user able to choose between 'share location', 'favPick' or 
        'favDrop' from the keyboard.
        '''

        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('share location', request_location=True)
        itembtn2 = types.KeyboardButton('fav1')
        itembtn3 = types.KeyboardButton('fav2')
        markup.add(itembtn1)
        markup.add(itembtn2)
        markup.add(itembtn3)
        Default.tb.send_message(user, "default state0", reply_markup=markup)

        return [Default.RESPOND, None]

#-------------------------------------------------------------------------------

    @staticmethod
    def check_respond(msg):

        '''
        check if the msg is a valid command for the program at state 1. If msg 
        is valid will move to state 1 function execution. Otherwise, 
        "error command" message will be sent.
        '''

        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is 'location':
            return True
        elif content_type is 'text':
            if msg['text'] == 'fav1' or msg['text'] == 'fav2':
                return True
            else:
                return False
        else:
            return False

 #-------------------------------------------------------------------------------

    @staticmethod
    def state_respond(user, msg, args=None):

        '''
        The customized (given user) state 1 function for execution. Return the 
        state increment.
        '''
        Default.bot.sendMessage(user, 'state one execute')

        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is 'location':
            location = msg['location']
            print(location)
            return [Default.END, None]

        elif msg['text'] == 'fav1': 
            if user in Default.fav_dict and Default.fav_dict[user][0][0] != None: # should change the fav dict to some other module object
                Default.bot.sendMessage(user, 'search execute')
                # search and show
                return [Default.END, None]
            else:
                Default.bot.sendMessage(user, '1st Favorite location is \
                    not set, please use /addFav to set')
                return [Default.END, None]
            
        else:
            if user in Default.fav_dict and Default.fav_dict[user][1][0] != None: # should change the fav dict to some other module object
                Default.bot.sendMessage(user, 'search execute')
                return [Default.END, None]
            else:
                Default.bot.sendMessage(user, '2nd Favorite location is \
                    not set, please use /addFav to set')
                return [Default.END, None]
        

#-------------------------------------------------------------------------------    
    
    def __init__(self, bot, tb, sqlfile):

        '''
        the Default Class is initialized so the command execution will be 
        operated by the given the bot and the tb object (telepot and telebot 
        object). 
        '''

        Default.bot = bot
        Default.tb = tb
        Default.statefun = [Default.state_request, Default.state_respond]
        Default.check_cmd = [Default.check_start, Default.check_respond]

#-------------------------------------------------------------------------------
    
    @staticmethod # Should be inherit
    def run(user, state, msg=None, args=None):

        '''
        Execute the function of the program at the given state and return the 
        next state
        '''

        return Default.statefun[state](user, msg, args)
        

################################################################################

class Help(PgmAbstract):

    ''' 
    "/help" command program. Send information of the commands to the user
    '''
    
    name = "/help"
    bot = None
    tb = None

    INFORM = 0
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
    def state_inform(user, msg=None, args = None):

        '''
        The customized (given user) state 0 function for execution
        '''

        Start.bot.sendMessage(user, \
            '/default : use current location or top favorite location.\n \
            /map : use map to identify the searching location.\n \
            /addr : use address to identify the searching location.\n\
            /fav : show options of favorite location.\n\
            /addFav : add favorite locations.\n\
            /start : greeting!\n\
            /help : commands instructions')

        return [Help.END, None]

#-------------------------------------------------------------------------------
        
    def __init__(self, bot, tb, sqlfile):
        
        '''
        the Help Class is initialized so the command execution will be operated
        by the given the bot and the tb object (telepot and telebot object). 
        '''

        Help.bot = bot
        Help.tb = tb
        Help.statefun = [Help.state_inform]
        Help.check_cmd = [Help.check_start]

#-------------------------------------------------------------------------------        
    
    @staticmethod # Should be inherit
    def run(user, state, msg=None, args=None):

        '''
        Execute the function of the program at the given state
        '''

        return Help.statefun[state](user, args)
        

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

        # Users sqlite3 database filename
        self.sqlfile = ""

        # The dict that maps the commands to the corresponding pgm class name.
        self.command_class = {}

        # The dict that maps the commands to the corresponding pgm class.
        self.command_libarary = {}

        with open('sqlfilename', 'r') as f:
            self.sqlfile = f.read()
        f.close()

        with open('commandsmap.json', 'r') as fp:
            self.command_class = json.load(fp)

        for key in self.command_class:
            self.command_libarary[key] = \
            eval(self.command_class[key])(self.bot, self.tb, self.sqlfile)

        fp.close()
    
    
################################################################################

if __name__ == "__main__":
    
    ''' for testing
    '''
    TOKEN = input("Enter the TOKEN: ") 
    bot = telepot.Bot(TOKEN)
    tb = telebot.TeleBot(TOKEN)
    testCmdLibrary = CmdLibrary(bot, tb, sqlfile)
    
    #help = testCmdLibrary.Help()
    #help.run()

