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

from pydoc import locate
import citybikes
import sqlite3
import abc
import telepot   
import telebot
from telebot import types
import json


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
            try:
                self.command_libarary[key] = locate(self.command_class[key])(self.bot, self.tb, self.sqlfile)
            except:
                print(key + " class not exist")
            

        fp.close()
    
    
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

