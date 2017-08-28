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

    # The dict that maps the commands to the corresponding pgm class name.
    command_class = {}

#-------------------------------------------------------------------------------

    def __init__(self):
        
        '''
        Initialized the CmdLibrary that maps the commands to the command program
        objects.
        '''

        # The dict that maps the commands to the corresponding pgm class.
        self.command_libarary = {}

        with open('commandsmap.json', 'r') as fp:
            CmdLibrary.command_class = json.load(fp)
        fp.close()

        for key in CmdLibrary.command_class:
            try:
                self.command_libarary[key] = locate(CmdLibrary.command_class[key])()
            except:
                print(key + " class not exist")
    
    
################################################################################

if __name__ == "__main__":
    
    testCmdLibrary = CmdLibrary()
    
   
