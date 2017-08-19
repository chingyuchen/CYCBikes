################################################################################
'''
File: cyctelebot.py
Author: Ching-Yu Chen

Description:
cyctelebot.py contains a CYCTelebot class which is a telegram bot object. The 
object communicates and executes the commands from the telegram users.

'''
################################################################################

import sqlite3
import telepot     
from telepot.loop import MessageLoop
from time import sleep
from cmdanalyzer import *
import telebot
from telebot import types

################################################################################

class CYCTelebot:

    '''
    CYCTelebot is a telebot object that communicates and executes the 
    commands from the telegram users. The list of commands are in the 
    commandsmap.json.
    '''
#-------------------------------------------------------------------------------

    def __init__(self, TOKEN, testuser):

        # Testing user id for the CYCTelebot
        self.testuser = testuser
        
        # The token of the CYCTelebot
        self.TOKEN = TOKEN;

        # The telepot object that receives and send message
        self.bot = telepot.Bot(TOKEN)

        # The telebot object that create customized keyboards
        self.tb = telebot.TeleBot(TOKEN)

        # The CmdAnalyzer object analyze the received commands
        self.cmdanalyzeri = CmdAnalyzer(self.bot, self.tb)

#-------------------------------------------------------------------------------

    def testHandle(self, msg):
        
        ''' 
        handle the received msg. If the msg is a command than execute the 
        command. Otherwise send a message of "not a command".
        '''

        content_type, chat_type, chat_id = telepot.glance(msg)
        
        if self.cmdanalyzeri.is_command(msg): 
            self.bot.sendMessage(chat_id, 'is a command!')
            self.cmdanalyzeri.execute(chat_id, msg)
        else:
            self.bot.sendMessage(chat_id, ' （ˊ＾ˋ ） ') 
            self.bot.sendMessage(chat_id, 'not a command!')
                
#-------------------------------------------------------------------------------

    def run(self):

        '''
        Run the CYCTelebot object. Starts handling the receive message from 
        the telegram users.
        '''

        self.cmdanalyzeri.intl_execute(self.testuser)

        MessageLoop(self.bot, self.testHandle).run_as_thread()

        while True:
            sleep(10)

################################################################################

if __name__ == "__main__":

    '''
    The main function initiate a CYCTelebot object and runs it.
    '''

    TOKEN = input("Enter the TOKEN: ") 
    chat_id = int(input("Enter the test chat_id: "))
    testclass = CYCTelebot(TOKEN, chat_id)
    testclass.run()
    
