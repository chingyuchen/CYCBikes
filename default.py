################################################################################

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
    name = "/start"
    
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

class Default(PgmAbstract):
    
    ''' 
    "/default" command program. Ask the user whether to send current 
    location or choose the favorite pick up or drop off locations. Then use the
    respond message to find and send the station information.
    The default program is the standby running program.
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
        check if the msg is a valid command for the program at state 0 
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

        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('share location', request_location=True)
        itembtn2 = types.KeyboardButton('fav1')
        itembtn3 = types.KeyboardButton('fav2')
        markup.add(itembtn1)
        markup.add(itembtn2)
        markup.add(itembtn3)
        Default.tb.send_message(user, "Where do you want to search?", \
            reply_markup=markup)

        return [Default.RESPOND, None]

#-------------------------------------------------------------------------------

    @staticmethod
    def check_respond(msg):

        '''
        check if the msg is a valid command for the program at state 1. If msg 
        is valid will move to state 1 function execution. Otherwise, 
        "error command" message will be sent.
        '''

        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is 'location':
            return True
        elif content_type is 'text':
            if msg['text'] == 'fav1' or msg['text'] == 'fav2':
                return True
            else:
                return False
        else:
            return False

 #-------------------------------------------------------------------------------

    @staticmethod
    def state_respond(user, msg, args=None):

        '''
        The customized (given user) state 1 function for execution. Return the 
        state increment.
        '''

        content_type, chat_type, chat_id = telepot.glance(msg)
        location = None
        if content_type is 'location':
            location = msg['location']

        else:
            conn = sqlite3.connect(Default.sqlfile)
            cur = conn.cursor()
            cur.execute('SELECT * FROM Favs WHERE id = ?', (user,))
            fav_dict = cur.fetchone()
            
            if msg['text'] == 'fav1': 
                if fav_dict is None or fav_dict[1] is None or fav_dict[2] is None: # bad index
                    Default.bot.sendMessage(user, '1st Favorite location is not'
                        ' set, please use /addFav to set')
                    conn.close()
                    return [Default.END, None]
                else:
                    location = {'latitude': fav_dict[1], 'longitude': fav_dict[2]}
                    
            
            else:
                if fav_dict is None or fav_dict[3] is None or fav_dict[4] is None: # bad index
                    Default.bot.sendMessage(user, '2nd Favorite location is not'
                        ' set, please use /addFav to set')
                    conn.close()
                    return [Default.END, None]
                else:
                    location = {'latitude': fav_dict[3], 'longitude': fav_dict[4]}
            
            conn.close()
            

        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('PickUp')
        itembtn2 = types.KeyboardButton('DropOff')
        markup.add(itembtn1)
        markup.add(itembtn2)
        Default.tb.send_message(user, "Pick up or drop off?", reply_markup=markup)
        
        # search and show
        return [Default.SEARCH, location]
        
#-------------------------------------------------------------------------------

    @staticmethod
    def check_pickordrop(msg):
        
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
        # args = {'latitude': 0.0, 'longitude': 0.0}

        client = citybikes.Client()
        net, dist = next(iter(client.networks.near(args['latitude'], args['longitude'])))
        sts = net.stations.near(args['latitude'], args['longitude'])

        # 'Coordinates: {latitude}, {longitude}'.format(latitude='37.24N', longitude='-115.81W')
        for stai in sts:
            if msg['text'] == 'PickUp' and stai[0]['empty_slots'] != 0: 
                Default.tb.send_message(user, "station {name} has {count} empty slots".format(name=stai[0]['name'], count=stai[0]['empty_slots']))
                return [Default.END, None]
         
            if msg['text'] == 'DropOff' and stai[0]['free_bikes'] != 0: 
                Default.tb.send_message(user, "station {name} has {count} free bikes".format(name=stai[0]['name'], count=stai[0]['free_bikes']))
                return [Default.END, None]

        Default.tb.send_message(user, "Sorry no available stations")

        return [Default.END, None]

#-------------------------------------------------------------------------------    
    
    def __init__(self, bot, tb, sqlfile):

        '''
        the Default Class is initialized so the command execution will be 
        operated by the given the bot and the tb object (telepot and telebot 
        object). 
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