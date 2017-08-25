################################################################################
'''
File: default.py
Author: Ching-Yu Chen

Description:
Default pgm provides the bike station information by the given current location
or favorite locations from the users.

'''
################################################################################

import citybikes
import sqlite3
import abc
import telepot   
import telebot
from telebot import types
from geopy.distance import vincenty


################################################################################

class PgmAbstract(object):

    ''' 
    Abstract class of the pgm of the bot. 
    '''

    # pgm execute command
    name = "/default"
    
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

#-------------------------------------------------------------------------------
 
    @staticmethod
    def check_start(msg=None):

        '''
        Return true if the msg is a valid command for the start state. 
        Otherwise, return false. 
        '''
        
        return True

#-------------------------------------------------------------------------------

    @staticmethod
    def state_request(user, msg=None, args=None):
        
        '''
        The customized (given user) state 0 function for execution. The function
        will let user able to choose between 'share location', 'favPick' or 
        'favDrop' from the keyboard.
        '''

################################################################################

class Default(PgmAbstract):
    
    ''' 
    "/default" command program. Ask the user to send current location or choose 
    the favorite locations. Then use the respond message to find and send the 
    station information. The default program is the standby running program.
    '''

    name = "/default"
    bot = None
    tb = None

    REQUEST = 0
    RESPOND = 1
    SEARCH = 2
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
        Return true if the msg is a valid command for the start state. 
        Otherwise, return false. 
        '''
        
        return True

#-------------------------------------------------------------------------------

    @staticmethod
    def state_request(user, msg=None, args=None):
        
        '''
        The request state function, return the enum of the next state function 
        to execute. The function ask user to choose between 'share location', 
        'fav1', 'fav2' or 'fav3' from the customized keyboard. 
        '''

        markup = types.ReplyKeyboardMarkup(row_width=1)
        itembtn1 = types.KeyboardButton('share location', request_location=True)
        itembtn2 = types.KeyboardButton('fav1')
        itembtn3 = types.KeyboardButton('fav2')
        itembtn4 = types.KeyboardButton('fav3')
        markup.add(itembtn1)
        markup.add(itembtn2)
        markup.add(itembtn3)
        markup.add(itembtn4)
        Default.tb.send_message(user, "Where would you like to search?", \
            reply_markup=markup)

        return [Default.RESPOND, None]

#-------------------------------------------------------------------------------

    @staticmethod
    def check_respond(msg):

        '''
        Return true if the respond message for the request state function from 
        the user is valid. Otherwise, return false.
        '''

        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is 'location':
            return True
        elif content_type is 'text':
            if msg['text'] == 'fav1' or msg['text'] == 'fav2' or \
            msg['text'] == 'fav3':
                return True
            else:
                return False
        else:
            return False

#-------------------------------------------------------------------------------

    @staticmethod
    def state_respond(user, msg, args=None):

        '''
        The respond state function. According to the respond from the user, 
        return the enum of the next state function and the location to be 
        searched. The function ask user whether to pick up or drop off with a 
        customized keyboard. If the user respond favorite location is not in the 
        database, send message to ask the user set it first.
        '''

        content_type, chat_type, chat_id = telepot.glance(msg)
        location = None
        args = [None] * 2
        if content_type is 'location':
            args[0] = "your current location"
            location = msg['location']

        else:
            args[0] = "your favorite location"
            
            conn = sqlite3.connect(Default.sqlfile)
            cur = conn.cursor()
            cur.execute('SELECT * FROM Favs WHERE id = ?', (user,))
            fav_dict = cur.fetchone()
            
            if msg['text'] == 'fav1': 
                if fav_dict is None or fav_dict[1] is None: # bad index
                    Default.bot.sendMessage(user, 'The 1st favorite location is'
                        ' not set yet. Please use /editFav to set')
                    conn.close()
                    return [Default.END, None]
                else:
                    location = {'latitude': fav_dict[1], 'longitude': fav_dict[2]}
                    
            
            elif msg['text'] == 'fav2':
                if fav_dict is None or fav_dict[3] is None: # bad index
                    Default.bot.sendMessage(user, 'The 2nd favorite location is'
                        ' not set yet. Please use /editFav to set')
                    conn.close()
                    return [Default.END, None]
                else:
                    location = {'latitude': fav_dict[3], 'longitude': fav_dict[4]}

            else:
                if fav_dict is None or fav_dict[5] is None: # bad index
                    Default.bot.sendMessage(user, 'The 3rd favorite location is'
                        ' not set yet. Please use /editFav to set')
                    conn.close()
                    return [Default.END, None]
                else:
                    location = {'latitude': fav_dict[5], 'longitude': fav_dict[6]}
            
            conn.close()
            args[1] = location
            

        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('PickUp')
        itembtn2 = types.KeyboardButton('DropOff')
        markup.add(itembtn1)
        markup.add(itembtn2)
        Default.tb.send_message(user, "Pick up or drop off?", reply_markup=markup)
        
        return [Default.SEARCH, args]
        
#-------------------------------------------------------------------------------

    @staticmethod
    def check_pickordrop(msg):

        '''
        Return true if the respond message from the user is either 'PickUp' or
        'DropOff'. Otherwise, return false.
        '''
        
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is not 'text':
            return False
        elif msg['text'] == 'PickUp' or msg['text'] == 'DropOff':
                return True
        else:
            return False

#-------------------------------------------------------------------------------

    @staticmethod
    def state_search(user, msg, args):
        
        '''
        The search state function. Use the location in the args to search the 
        nearest bike station. Send the information of the bike station to the 
        user and return the enum of the end state function.
        '''

        location_s = args[0]
        location_geo = args[1]
        posi1 = (location_geo['latitude'], location_geo['longitude'])
        
        client = citybikes.Client()
        net, dist = next(iter(client.networks.near(\
            location_geo['latitude'], location_geo['longitude'])))
        sts = net.stations.near(location_geo['latitude'], location_geo['longitude'])

        for stai in sts:
            if msg['text'] == 'PickUp' and stai[0]['free_bikes'] != 0: 
                Default.tb.send_location(user, \
                    stai[0]['latitude'], stai[0]['longitude'])
                
                posi2 = (stai[0]['latitude'], stai[0]['longitude'])
                distval = vincenty(posi1, posi2).meters
                distS = "{:100.2f}".format(distval)
                
                Default.tb.send_message(user, "The station {name} has {count} "\
                    "free bikes. It is {dist} meters away from {targetloca}."\
                    .format(name=stai[0]['name'], count=stai[0]['free_bikes'],\
                     dist=distS, targetloca=location_s))
                
                return [Default.END, None]
         
            if msg['text'] == 'DropOff' and stai[0]['empty_slots'] != 0: 
                Default.tb.send_location(user, \
                    stai[0]['latitude'], stai[0]['longitude'])
                
                posi2 = (stai[0]['latitude'], stai[0]['longitude'])
                distval = vincenty(posi1, posi2).meters
                distS = "{:100.2f}".format(distval)
                
                Default.tb.send_message(user, "The station {name} has {count}"\
                    "empty slots. It is {dist} meters away from {targetloca}."\
                    .format(name=stai[0]['name'], count=stai[0]['empty_slots'],\
                     dist=distS, targetloca=location_s))
                
                return [Default.END, None]

        Default.tb.send_message(user, "Sorry no available stations.")

        return [Default.END, None]

#-------------------------------------------------------------------------------    
    
    def __init__(self, bot, tb, sqlfile):

        '''
        the Default Class is initialized so the command execution will be 
        operated by the given the bot and the tb object (telepot and telebot 
        object). The user information is in the given sqlfile.
        '''

        Default.bot = bot
        Default.tb = tb
        Default.statefun = [Default.state_request, Default.state_respond, \
                            Default.state_search]
        Default.check_cmd = [Default.check_start, Default.check_respond, \
                            Default.check_pickordrop]
        Default.sqlfile = sqlfile


#-------------------------------------------------------------------------------
    
    @staticmethod # Should be inherit
    def run(user, state, msg=None, args=None):

        '''
        Execute the function of the program at the given state and return the 
        next state
        '''

        return Default.statefun[state](user, msg, args)
        

################################################################################

if __name__ == "__main__":
    
    ''' 
    For testing
    '''
    TOKEN = input("Enter the TOKEN: ") 
    bot = telepot.Bot(TOKEN)
    tb = telebot.TeleBot(TOKEN)

    sqlfile = None
    with open('sqlfilename', 'r') as f:
        sqlfile = f.read()
    f.close()
    default_class = Default(bot, tb, sqlfile)

