################################################################################
'''
File: start.py
Author: Ching-Yu Chen

Description:
start.py contains Start class, which is a program object of the "/start" command. 
Start pgm greets to the CYCBikes user.

Copyright (c) 2017 Ching-Yu Chen
'''
################################################################################

import abc
import telepot   
from pgmabstract import PgmAbstract     

################################################################################

class Start(PgmAbstract):

    ''' 
    "/start" command program. Send greeting message. 
    '''

    name = "/start"

    # enum of the state of the program

    START = 0
    END = -1

#-------------------------------------------------------------------------------

    def check_start(self, msg):
        return True

#-------------------------------------------------------------------------------

    def state_start(self, user, msg, args=None):

        '''
        The start state function. Send greeting to the user and return enum 
        of the end state function. args provide the user name.
        '''

        if args is None:
            name = msg['from']['first_name']
            args = [name, ]

        self.bot.sendMessage(user, 'Hi, {first_name}! CYCBikes helps you to '
            'find the bike-share station to pick up or drop off bikes. Send '
            '/help for more options'.format(first_name=args[0]))

        return [Start.END, None]

#-------------------------------------------------------------------------------
        
    def __init__(self):
        
        '''
        The Start Class is initialized so the command execution will be operated 
        by the bot and the tb object (telepot and telebot object) initiated in 
        superclass. Each state corresponding execute function and check function 
        are specified.
        '''

        self.statefun = [self.state_start]
        self.check_cmd = [self.check_start]
        super().__init__()

################################################################################


if __name__ == "__main__":
    
    '''
    For testing
    '''

    sartclass1 = Start()
