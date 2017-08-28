################################################################################
'''
File: pgmabstract.py
Author : Ching-Yu Chen

Description: pgmabstract.py contains the abstract class, PgmAbstract, where 
PgmAbstract is the abstract class of the command program in telegram bot.

'''
################################################################################

import abc
from abc import ABCMeta
import telepot     
import telebot

################################################################################

class PgmAbstract(object, metaclass=ABCMeta):

    '''
    PgmAbstract is an abstract class of the command program in telegram bot. 
    Subclass must define the functions to execute / check valid command function
    / enum of the state in each state of the program. 

    '''

    __metaclass__ = abc.ABCMeta
    
#---------------------------- Initialization -----------------------------------

    def __init__(self):

        '''
        Initialized the command program object. The subclasses must define 
        self.statefun and self.check_cmd.
        '''
        
        # Token of the bot.
        TOKEN = ""
        with open('cycbikes_TOKEN', 'r') as f:
            TOKEN = f.read().strip()
        f.close()

        
        # Object of telepot, sending and receiving messages from telegram users
        self.bot = telepot.Bot(TOKEN)
        
        # Object of telepot, show user customized keyboard
        self.tb = telebot.TeleBot(TOKEN)
        
        # sqlfilename, the file stores user info
        self.sqlfile = "usersinfo.sqlite3"  
        with open('usersinfo.sqlite3', 'a+') as f:
            try:
                assert(f != None)
            except:
                print("no user info file")
        f.close()
 
        
        # self.statefun, the list stores the state function.
        try:
            len(self.statefun) != 0
        except:
            raise NotImplementedError('Subclasses must define statefun')

        
        # self.check_cmd, the list stores the check command function.
        try:
            len(self.check_cmd) != 0
        except:
            raise NotImplementedError('Subclasses must define check_cmd')


#--------------------------- Inherit fields ------------------------------------

    '''
    Enum of the state, specified the index of the state function/check function 
    in the list objects self.statefun and self.check_cmd.
    '''
    
    @property
    def START():
        return 0

    
    @property
    def END():
        return -1

#--------------------------- Inherit method ------------------------------------
    
    def run(self, user, state, msg=None, args=None):

        ''' 
        Execute the pgm in specified state, user, msg and args. Return the next
        state of the program.
        '''

        try:
            next_stateinfo = self.statefun[state](user, msg, args)
            assert(next_stateinfo != None)
            return next_stateinfo
        except:
            raise NotImplementedError('State function must return next state inform')


#--------------------------- Abstract field ------------------------------------

    @property
    @abc.abstractmethod
    def name():

        '''
        The corresponding command of the program
        '''
        
        pass

#--------------------------- Abstract method -----------------------------------

    @abc.abstractmethod
    def check_start(self, msg=None):

        '''
        Function to check valid command at start state. Return true if it is 
        valid, otherwise return false.
        '''    

        pass


    @abc.abstractmethod
    def state_start(self, user, msg=None, args = None):

        '''
        Start state function. After check_start function check the command is 
        valid, the state function then can be execute. Return the next state
        and args.
        '''    

        pass

    

