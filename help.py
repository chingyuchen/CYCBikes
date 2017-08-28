################################################################################
'''
File: help.py
Author: Ching-Yu Chen

Description:
help.py contains Help class, which is a program object of the "/help" command. 
Help pgm send the commands instruction to the users.

Copyright (c) 2017 Ching-Yu Chen
'''
################################################################################

import abc
import telepot 
from pgmabstract import PgmAbstract     

################################################################################

class Help(PgmAbstract):

    ''' 
    "/help" command program. Send information of the commands to the user.
    '''
    
    name = "/help"
    

    # enum of the state of the program

    START = 0
    END = -1

#-------------------------------------------------------------------------------

    def check_start(self, msg):
        return True

#-------------------------------------------------------------------------------

    def state_start(self, user, msg=None, args = None):

        '''
        The inform state function. Send commands instruction to the users and
        return the enum of the end state.
        '''

        self.bot.sendMessage(user, \
            '/default : use current location or favorite locations.\n'
            '/addr : use address to identify the searching location.\n'
            '/fav : show current list of favorite locations.\n'
            '/editFav : edit favorite locations.\n'
            '/start : greeting!\n'
            '/help : commands instructions')

        return [Help.END, None]

#-------------------------------------------------------------------------------
        
    def __init__(self):
        
        '''
        The Help Class is initialized so the command execution will be operated 
        by the bot and the tb object (telepot and telebot object) initiated in 
        superclass. Each state corresponding execute function and check function 
        are specified.
        '''

        self.statefun = [self.state_start]
        self.check_cmd = [self.check_start]
        super().__init__()

