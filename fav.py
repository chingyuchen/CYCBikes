################################################################################
'''
File: fav.py
Author: Ching-Yu Chen

Description:
Fav pgm send the list of the addresses of the user's favorite locations.

'''
################################################################################

import abc
import telepot      
import geocoder
import sqlite3
import telebot


################################################################################

class PgmAbstract(object):

    ''' 
    Abstract class of the pgm of the bot. 
    '''

    # pgm execute command
    name = "/fav"
    
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

class Fav(PgmAbstract):

    ''' 
    "/fav" command program. Send the list of the addresses of the user's 
    favorite locations.
    '''
    
    name = "/fav"
    bot = None

    INFORM = 0
    END = -1

    statefun = []
    check_cmd = []

#-------------------------------------------------------------------------------

    @staticmethod
    def check_start(msg):
        
        '''
        Return true if the command is valid for the start state. Otherwise, 
        return false. 
        '''

        return True

#-------------------------------------------------------------------------------

    @staticmethod
    def state_inform(user, msg=None, args = None):

        '''
        The inform state function. Send the addresses of the user's favorite 
        locations to the user. Return the enum of the end sate.
        '''

        conn = sqlite3.connect(Fav.sqlfile)
        cur = conn.cursor()
        cur.execute('SELECT * FROM Favs WHERE id = ?', (user,))
        fav_dict = cur.fetchone()
        conn.close()
        
        favs = {"fav1":"", "fav2":"", "fav3":""}
        if fav_dict is not None: # bad repeated code
            if fav_dict[1] is not None: # bad index
                lat = fav_dict[1]
                lon = fav_dict[2]
                try:
                    corres_addr = geocoder.google([lat, lon], method='reverse', key=Fav.key)
                    favs["fav1"] = corres_addr.address
                except:
                    print("Error in accessing geocoder")
                    Fav.bot.sendMessage(user, "Sorry there's problem accessing geocoder")
                    return [Fav.END, None]

            if fav_dict[3] is not None:
                lat = fav_dict[3]
                lon = fav_dict[4]
                try:
                    corres_addr = geocoder.google([lat, lon], method='reverse', key=Fav.key)
                    favs["fav2"] = corres_addr.address
                except:
                    print("Error in accessing geocoder")
                    Fav.bot.sendMessage(user, "Sorry there's problem accessing geocoder")
                    return [Fav.END, None]

            if fav_dict[5] is not None:
                lat = fav_dict[5]
                lon = fav_dict[6]
                try:
                    corres_addr = geocoder.google([lat, lon], method='reverse', key=Fav.key)
                    favs["fav3"] = corres_addr.address
                except:
                    print("Error in accessing geocoder")
                    Fav.bot.sendMessage(user, "Sorry there's problem accessing geocoder")
                    return [Fav.END, None]

        respond_msg = 'Here is the list of your favorites locations.'\
        ' You can have at most three favorite locations.\n* Fav1 : {favs1}\n'\
        '* Fav2 : {favs2}\n''* Fav3 : {favs3}'.format(\
            favs1=favs["fav1"], favs2=favs["fav2"], favs3=favs["fav3"])

        Fav.bot.sendMessage(user, respond_msg)

        return [Fav.END, None]

#-------------------------------------------------------------------------------
        
    def __init__(self, bot, tb, sqlfile):
        
        '''
        the Fav Class is initialized so the command execution will be operated
        by the given the bot object (telepot object). The user information is 
        in the sqlfile.
        '''

        Fav.bot = bot
        Fav.statefun = [Fav.state_inform]
        Fav.check_cmd = [Fav.check_start]
        Fav.sqlfile = sqlfile
        Fav.key = "" 
        try:
            with open('geocoder_key','r') as f:
                Fav.key = f.read().strip()
            f.close()
            assert(len(Fav.key) != 0)
        except:
            print("error in accessing geocoder key")
            Fav.bot.sendMessage(user, "Sorry there's problem using geocoder")
                
#-------------------------------------------------------------------------------        
    
    @staticmethod # Should be inherit
    def run(user, state, msg=None, args=None):

        '''
        Execute the function of the program at the given state
        '''

        return Fav.statefun[state](user, msg, args)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    '''
    For testing
    '''
    TOKEN = input("Enter the TOKEN: ")
    bot = telepot.Bot(TOKEN)
    sqlfile = None
    with open('sqlfilename', 'r') as f:
        sqlfile = f.read()
    f.close
    fav_class = Fav(bot, None, sqlfile)
        
