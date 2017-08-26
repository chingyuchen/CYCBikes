################################################################################
'''
File: editfav.py
Author: Ching-Yu Chen

Description:
editfav pgm allows users to edit their favorite locations.

'''
################################################################################

import geocoder
import citybikes
import sqlite3
import abc
import telepot   
import telebot
from telebot import types


################################################################################

class PgmAbstract(object):

    ''' 
    Abstract class of the pgm of the bot. 
    '''

    # pgm execute command
    name = ""
    
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

class EditFav(PgmAbstract):
    
    ''' 
    "/editFav" command program. Let the user to edit their favorite locations.
    '''

    name = "/editFav"
    bot = None
    tb = None

    REQUEST = 0
    RESPOND = 1
    SEARCH = 2
    CHECKCORRECT = 3
    END = -1

    statefun = []
    check_cmd = []

    conn = None
    cur = None
    sqlfile = None

#-------------------------------------------------------------------------------

    @staticmethod
    def check_start(msg=None):

        '''
        Return true if the command is valid for the start state. Otherwise, 
        return false. 
        '''
        
        return True

#-------------------------------------------------------------------------------

    @staticmethod
    def state_request(user, msg=None, args=None):
        
        '''
        The request state function. Send user his/her current favorite locations 
        stored in the database. Ask user to choose which one to be edited with a
        customized keyboard 'EditFav1', 'EditFav2' and 'EditFav3'. Return the 
        enum of the respond state function.
        '''

        conn = sqlite3.connect(EditFav.sqlfile)
        cur = conn.cursor()
        cur.execute('SELECT * FROM Favs WHERE id = ?', (user,))
        fav_dict = cur.fetchone()
        
        favs = {"fav1":"", "fav2":"", "fav3":""}
        if fav_dict is not None: # bad repeated code
            if fav_dict[1] is not None: # bad index
                lat = fav_dict[1]
                lon = fav_dict[2]
                
                try:
                    corres_addr = geocoder.google([lat, lon], method='reverse', \
                            key=EditFav.key)
                    favs["fav1"] = corres_addr.address
                except:
                    print("error using geocoder")
                    EditFav.tb.send_message(user, "Sorry the geocoder currently "
                        "is not operating. Can't get the information of the "
                        "address now. :(")
                    return [EditFav.END, None]
                
            if fav_dict[3] is not None:
                lat = fav_dict[3]
                lon = fav_dict[4]

                try:
                    corres_addr = geocoder.google([lat, lon], method='reverse',\
                            key=EditFav.key)
                    favs["fav2"] = corres_addr.address
                except:
                    print("error using geocoder")
                    EditFav.tb.send_message(user, "Sorry the geocoder currently "
                        "is not operating. Can't get the information of the "
                        "address now. :(")
                    return [EditFav.END, None]
                
            if fav_dict[5] is not None:
                lat = fav_dict[5]
                lon = fav_dict[6]
                
                try:
                    corres_addr = geocoder.google([lat, lon], method='reverse',\
                            key=EditFav.key)
                    favs["fav3"] = corres_addr.address
                except:
                    print("error using geocoder")
                    EditFav.tb.send_message(user, "Sorry the geocoder currently "
                        "is not operating. Can't get the information of the "
                        "address now. :(")
                    return [EditFav.END, None]
        
        conn.close()

        request_msg = 'Here is the list of your favorites locations. '\
        'You can have at most three favorite locations.\nfav1 : {favs1}\n'\
        'fav2 : {favs2}\nfav3 : {favs3}\n'\
        'Which one would you like to edit?'.format(\
        favs1=favs["fav1"], favs2=favs["fav2"], favs3=favs["fav3"])

        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('EditFav1')
        itembtn2 = types.KeyboardButton('EditFav2')
        itembtn3 = types.KeyboardButton('EditFav3')
        markup.add(itembtn1)
        markup.add(itembtn2)
        markup.add(itembtn3)
        EditFav.tb.send_message(user, request_msg, reply_markup=markup)

        return [EditFav.RESPOND, None]

#-------------------------------------------------------------------------------

    @staticmethod
    def check_respond(msg):

        '''
        Check if the msg is a valid command for the respond state. Return true 
        if it is valid. Otherwise, return false.
        '''

        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is not 'text':
            return False
        
        if msg['text'] == 'EditFav1' or msg['text'] == 'EditFav2' or \
        msg['text'] == 'EditFav3':
            return True
        else:
            return False
       

 #-------------------------------------------------------------------------------

    @staticmethod
    def state_respond(user, msg, args=None):

        '''
        The respond state function. Ask user to type the address. Return the 
        enum of the search state and the args indicating which favorite location 
        user would like to edit.
        '''

        return_args = []
        if msg['text'] == 'EditFav1':
            return_args = [1, 0, 0] # bad index
        elif msg['text'] == 'EditFav2':
            return_args = [2, 0, 0]
        else: 
            return_args = [3, 0, 0]

        EditFav.bot.sendMessage(user, 'Please enter the address')
       
        return [EditFav.SEARCH, return_args]
        
#-------------------------------------------------------------------------------

    @staticmethod
    def check_textaddr(msg):

        '''
        Check function for the address (msg). Return true if is is valid. 
        Otherwise, return false.
        '''
        
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is not 'text':
            return False
        return True

#-------------------------------------------------------------------------------

    @staticmethod
    def state_search(user, msg, args):

        '''
        The search state function. Search the address in msg. Send the 
        corresponding address to the user and request the user to reply if it is
        correct or not with a customized keyborad. Return the enum of the check
        correct state and the args included the address.
        '''
        
        content_type, chat_type, chat_id = telepot.glance(msg)
        location = None
        addr = msg['text']

        try:
            g = geocoder.google(addr, key=EditFav.key)
            location = {'latitude': g.latlng[0], 'longitude': g.latlng[1]}
            corres_addr = geocoder.google([g.latlng[0], g.latlng[1]], \
                    method='reverse', key=EditFav.key)
            args[1] = g.latlng[0] # bad index
            args[2] = g.latlng[1]
        except:
            print("error using geocoder")
            EditFav.tb.send_message(user, "Sorry the geocoder currently "
                "is not operating. Can't get the information of the "
                "address now. :(")
            return [EditFav.END, None]


        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('Correct')
        itembtn2 = types.KeyboardButton('Wrong')
        markup.add(itembtn1)
        markup.add(itembtn2)
        reply_msg = "Add address [" + corres_addr.address + "], is it correct?"
        EditFav.tb.send_message(user, reply_msg, reply_markup=markup)

        return [EditFav.CHECKCORRECT, args]

#-------------------------------------------------------------------------------

    @staticmethod
    def check_correctwrong(msg):

        '''
        Check if the command (msg) is valid for check correct state function. 
        Return true if it is valid, otherwise, return false.
        '''
        
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is not 'text':
            return False
        elif msg['text'] == 'Correct' or msg['text'] == 'Wrong':
            return True
        return False

#-------------------------------------------------------------------------------

    @staticmethod
    def state_edit(user, msg, args):

        '''
        The edit state function. If the user replied 'wrong', send the user 
        message 'Please enter the address' and return the enum of the search 
        state function. Otherwise, the user replied 'correct', then edit the
        user favorite location with the information from args. Return the enum
        of the end state function.
        '''

        if msg['text'] == 'Wrong':
            EditFav.bot.sendMessage(user, 'Please enter the address')
            return [EditFav.SEARCH, args]

        else:
            conn = sqlite3.connect(EditFav.sqlfile)
            cur = conn.cursor()
            
            lat = args[1]
            lon = args[2]
            
            cur.execute('SELECT * FROM Favs WHERE id = ?', (user,))
            getfavs = cur.fetchone()
            if getfavs is None:
                cur.execute('INSERT INTO Favs (id, fav1lati, fav1lon, fav2lati,'
                    'fav2lon, fav3lati, fav3lon) VALUES ( ?, ?, ?, ?, ?, ?, ?)',\
                    (user, None, None, None, None, None, None))
                conn.commit()

            if args[0] is 1: # bad index
                cur.execute('UPDATE Favs SET fav1lati = ? WHERE id = ?', (lat, user))
                cur.execute('UPDATE Favs SET fav1lon = ? WHERE id = ?', (lon, user))
            elif args[0] is 2:
                cur.execute('UPDATE Favs SET fav2lati = ? WHERE id = ?', (lat, user))
                cur.execute('UPDATE Favs SET fav2lon = ? WHERE id = ?', (lon, user))
            else: 
                cur.execute('UPDATE Favs SET fav3lati = ? WHERE id = ?', (lat, user))
                cur.execute('UPDATE Favs SET fav3lon = ? WHERE id = ?', (lon, user))
            conn.commit()
            EditFav.bot.sendMessage(user, 'Finished edit!')

            conn.close()

        return [EditFav.END, None]

#-------------------------------------------------------------------------------    
    
    def __init__(self, bot, tb, sqlfile):

        '''
        The EditFav Class is initialized so the command execution will be 
        operated by the given the bot and the tb object (telepot and telebot 
        object). The user information is in the sqlfile.
        '''

        EditFav.bot = bot
        EditFav.tb = tb
        EditFav.statefun = [EditFav.state_request, EditFav.state_respond, \
                            EditFav.state_search, EditFav.state_edit]
        EditFav.check_cmd = [EditFav.check_start, EditFav.check_respond, \
                            EditFav.check_textaddr, EditFav.check_correctwrong]
        EditFav.sqlfile = sqlfile
        EditFav.key = ""
        try:
            with open('geocoder_key', 'r') as f:
                EditFav.key = f.read().strip()
            f.close()
            assert(len(EditFav.key) != 0)
        except:
            print("error in accessing geocoder key")
            EditFav.bot.sendMessage(user, "Sorry there's problem using geocoder")

#-------------------------------------------------------------------------------
    
    @staticmethod # Should be inherit
    def run(user, state, msg=None, args=None):

        '''
        Execute the function of the program at the given state and return the 
        next state
        '''

        return EditFav.statefun[state](user, msg, args)
        

################################################################################

if __name__ == "__main__":
    
    ''' for testing
    '''
    TOKEN = input("Enter the TOKEN: ") 
    bot = telepot.Bot(TOKEN)
    tb = telebot.TeleBot(TOKEN)

    sqlfile = None
    with open('sqlfilename', 'r') as f:
        sqlfile = f.read()
    f.close()
    editFav_class = EditFav(bot, tb, sqlfile)

