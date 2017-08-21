################################################################################
import abc
import geocoder
import telepot   
import telebot
import citybikes
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

class Address(PgmAbstract):
    
    ''' 
    "/addr" command program. 
    '''

    name = "/addr"
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
        Request address from the user
        '''

        Address.tb.send_message(user, "Please enter the address.")

        return [Address.RESPOND, None]

#-------------------------------------------------------------------------------

    @staticmethod
    def check_respond(msg):

        '''
        Return whether a msg is a valid command (text form). 
        '''

        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is 'text':
            return True
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
        addr = msg['text']

        g = geocoder.google(addr)
        location = {'latitude': g.latlng[0], 'longitude': g.latlng[1]}
        corres_addr = geocoder.google([g.latlng[0], g.latlng[1]], method='reverse')

        Address.bot.sendMessage(user, 'Search for ' + corres_addr.address)

        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('PickUp')
        itembtn2 = types.KeyboardButton('DropOff')
        itembtn3 = types.KeyboardButton('WrongAddress')
        markup.add(itembtn1)
        markup.add(itembtn2)
        markup.add(itembtn3)
        Address.tb.send_message(user, "Pick up or drop off?", reply_markup=markup)
        
        # search and show
        return [Address.SEARCH, location]
        
#-------------------------------------------------------------------------------

    @staticmethod
    def check_options(msg):
        
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is not 'text':
            return False
        elif msg['text'] == 'PickUp' or msg['text'] == 'DropOff' or msg['text'] == 'WrongAddress':
                return True
        else:
            return False

#-------------------------------------------------------------------------------

    @staticmethod
    def state_search(user, msg, args):

        if msg['text'] == 'WrongAddress':
            Address.tb.send_message(user, "Please enter the address.")
            return [Address.RESPOND, None]
        
        client = citybikes.Client()
        net, dist = next(iter(client.networks.near(args['latitude'], args['longitude'])))
        sts = net.stations.near(args['latitude'], args['longitude'])

        for stai in sts:
            if msg['text'] == 'PickUp' and stai[0]['empty_slots'] != 0: 
                Address.tb.send_message(user, "station {name} has {count} empty slots".format(name=stai[0]['name'], count=stai[0]['empty_slots']))
                return [Address.END, None]
         
            if msg['text'] == 'DropOff' and stai[0]['free_bikes'] != 0: 
                Address.tb.send_message(user, "station {name} has {count} free bikes".format(name=stai[0]['name'], count=stai[0]['free_bikes']))
                return [Address.END, None]

        Address.tb.send_message(user, "Sorry no available stations")

        return [Address.END, None]

#-------------------------------------------------------------------------------    
    
    def __init__(self, bot, tb, sqlfile):

        '''
        the Address Class is initialized so the command execution will be 
        operated by the given the bot and the tb object (telepot and telebot 
        object). 
        '''

        Address.bot = bot
        Address.tb = tb
        Address.statefun = [Address.state_request, Address.state_respond, \
                            Address.state_search]
        Address.check_cmd = [Address.check_start, Address.check_respond, \
                            Address.check_options]
        Address.sqlfile = sqlfile


#-------------------------------------------------------------------------------
    
    @staticmethod # Should be inherit
    def run(user, state, msg=None, args=None):

        '''
        Execute the function of the program at the given state and return the 
        next state
        '''

        return Address.statefun[state](user, msg, args)
        