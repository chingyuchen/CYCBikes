################################################################################
''' 
File: cmdlibrary.py
Author : Ching-Yu Chen

Description: cmdlibrary.py contains a dict that maps the commands to all the 
program classes of a designed telegram-bot. The list of corresponding commands 
and the name of the classes are in the commandsmap.json. 

'''
################################################################################

from pydoc import locate
import sqlite3
import telepot   
import telebot
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

        self.sqlfile = "usersinfo.sqlite3"
        with open('usersinfo.sqlite3', 'a+') as f:
            try:
                assert(f != None)
            except:
                print("no user info file")
        f.close()
        

        with open('commandsmap.json', 'r') as fp:
            self.command_class = json.load(fp)
        fp.close()

        for key in self.command_class:
            try:
                self.command_libarary[key] = locate(self.command_class[key])\
                (self.bot, self.tb, self.sqlfile)
            except:
                print(key + " class not exist")
    
    
################################################################################

if __name__ == "__main__":
    
    ''' for testing
    '''
    TOKEN = input("Enter the TOKEN: ") 
    bot = telepot.Bot(TOKEN)
    tb = telebot.TeleBot(TOKEN)
    testCmdLibrary = CmdLibrary(bot, tb)
    
   
