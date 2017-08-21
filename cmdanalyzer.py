################################################################################
'''
File: cmdanalyzer.py
Author: Ching-Yu Chen

Description:
cmdanalyzer.py contains a CmdAnalyzer class which is a object that analyzes the 
commands(messages) received from telegram user and able to execute the commands.

'''
################################################################################

import telepot   
import json
from cmdlibrary import *

################################################################################

class CmdAnalyzer:

    ''' 
    CmdAnalyzer analyzes the commands(messages) received from telegram user 
    and able to execute the command. It is initialized by given a bot (telepot 
    object) and a tb (telebot object)
    '''
#-------------------------------------------------------------------------------

    def __init__(self, bot, tb):

        # the object that send and receive messages
        self.bot = bot

        # the object that contains the information of the commands and 
        # corresponding programs.
        self.commandsclass = CmdLibrary(bot, tb)

        # the dict that maps the commands to the program 
        self._command_libarary = self.commandsclass.command_libarary

        # the dict that maps the user to the current running program state
        # {userID, 
        # {'cmd'='/pgm', 'state_num'=int, 'check_cmd_fun'=fun, 'arg' = [args]}}
        self.user_state = {}
        
#-------------------------------------------------------------------------------

    def intl_execute(self, userid):

        ''' 
        The first function execute when starting a conversation with userid.
        It runs the "/start" cmd and then run the "/default" cmd
        '''
        
        state_inform = {'cmd' : '/start', 'state_num' : 0, 'arg' : None}
        self.user_state[userid] = state_inform
        self.execute(userid)

#-------------------------------------------------------------------------------

    def is_command(self, msg):

        ''' 
        Return True if a msg is a valid cmd. Otherwise, return False.
        '''

        content_type, chat_type, chat_id = telepot.glance(msg)
        state_inform = self.user_state.get(chat_id)
        if state_inform['check_cmd_fun'](msg):  # check valid current pgm cmd
            if content_type is 'text':
                commandi = msg['text'].split()
                if 'arg' not in state_inform:
                    state_inform['arg'] = None
                if len(commandi) != 1:
                    state_inform['arg'] = commandi[1 : ] 

            return True

        elif content_type != 'text':  # check valid new cmd type
            return False
        
        else:
            commandi = msg['text'].split()
            if commandi[0] in self._command_libarary:  # check new pgm cmd
                state_inform['cmd'] = commandi[0]
                state_inform['state_num'] = 0
                state_inform['check_cmd_fun'] = None
                state_inform['arg'] = None
                if len(commandi) != 1:               
                    state_inform['arg'] = commandi[1 : ] # should add check valid arguments function!!

                return True
            else:
                return False

#-------------------------------------------------------------------------------

    def execute(self, chat_id, msg=None):
        
        ''' 
        Execute the chat_id command
        '''

        state_inform = self.user_state.get(chat_id)
        classi = self._command_libarary[state_inform['cmd']]
        
        nextstate_info = \
        classi.run(chat_id, state_inform['state_num'], msg, state_inform['arg'])

        state_inform['state_num'] = nextstate_info[0]
        state_inform['arg'] = nextstate_info[1]

        
        state_inform['check_cmd_fun'] = \
        classi.check_cmd[state_inform['state_num']]

        if state_inform['state_num'] is -1: # pgm ends, run the default pgm
          
            classi = self._command_libarary['/default']
            state_inform['cmd'] = '/default'

            nextstate_info = classi.run(chat_id, 0)
            state_inform['state_num'] = nextstate_info[0]
            state_inform['arg'] = nextstate_info[1]

            state_inform['check_cmd_fun'] = \
            classi.check_cmd[state_inform['state_num']]

        
################################################################################

if __name__ == "__main__":

    '''
    For testing
    '''

    TOKEN = input("Enter the TOKEN: ") 
    bot = telepot.Bot(TOKEN)
    tb = telebot.TeleBot(TOKEN)
    testCmdAnalyzer = CmdAnalyzer(bot, tb)
