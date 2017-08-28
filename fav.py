################################################################################
'''
File: fav.py
Author: Ching-Yu Chen

Description:
fav.py contains Fav class, which is a program object of the "/fav" command. 
Fav pgm send the list of the addresses of the user's favorite locations.

Copyright (c) 2017 Ching-Yu Chen
'''
################################################################################

import abc
import telepot      
import geocoder
import sqlite3
import telebot
from pgmabstract import PgmAbstract  

################################################################################

class Fav(PgmAbstract):

    ''' 
    "/fav" command program. Send the list of the addresses of the user's 
    favorite locations.
    '''
    
    name = "/fav"

    # enum of the state of the program

    START = 0
    END = -1


    # geocoder key
    
    key = ""
    try:
        with open('geocoder_key', 'r') as f:
            key = f.read().strip()
        f.close()
        assert(len(key) != 0)
    except:
        print("error in accessing geocoder key")

#-------------------------------------------------------------------------------

    def check_start(self, msg):
        return True

#-------------------------------------------------------------------------------

    def state_start(self, user, msg=None, args = None):

        '''
        The inform state function. Send the addresses of the user's favorite 
        locations to the user. Return the enum of the end sate.
        '''

        conn = sqlite3.connect(self.sqlfile)
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
                    self.bot.sendMessage(user, "Sorry there's problem accessing geocoder")
                    return [Fav.END, None]

            if fav_dict[3] is not None:
                lat = fav_dict[3]
                lon = fav_dict[4]
                try:
                    corres_addr = geocoder.google([lat, lon], method='reverse', key=Fav.key)
                    favs["fav2"] = corres_addr.address
                except:
                    print("Error in accessing geocoder")
                    self.bot.sendMessage(user, "Sorry there's problem accessing geocoder")
                    return [Fav.END, None]

            if fav_dict[5] is not None:
                lat = fav_dict[5]
                lon = fav_dict[6]
                try:
                    corres_addr = geocoder.google([lat, lon], method='reverse', key=Fav.key)
                    favs["fav3"] = corres_addr.address
                except:
                    print("Error in accessing geocoder")
                    self.bot.sendMessage(user, "Sorry there's problem accessing geocoder")
                    return [Fav.END, None]

        respond_msg = 'Here is the list of your favorites locations.'\
        ' You can have at most three favorite locations.\n* Fav1 : {favs1}\n'\
        '* Fav2 : {favs2}\n''* Fav3 : {favs3}'.format(\
            favs1=favs["fav1"], favs2=favs["fav2"], favs3=favs["fav3"])

        self.bot.sendMessage(user, respond_msg)

        return [Fav.END, None]

#-------------------------------------------------------------------------------
        
    def __init__(self):
        
        '''
        The Fav Class is initialized so the command execution will be 
        operated by the bot and the tb object (telepot and telebot 
        object) initiated in superclass. Each state corresponding execute 
        function and check function are specified.
        '''

        self.statefun = [self.state_start]
        self.check_cmd = [self.check_start]
        super().__init__()
                
################################################################################

if __name__ == "__main__":
    
    '''
    For testing
    '''
    
    fav_class = Fav()
        
