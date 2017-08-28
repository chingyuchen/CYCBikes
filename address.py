################################################################################
'''
File: address.py
Author: Ching-Yu Chen

Description:
address.py contains Address class, which is a program object of the "/addr" 
command. Address pgm allows to search the bikes station with the address.

'''
################################################################################

import abc
import geocoder
import telepot   
import telebot
from telebot import types
import citybikes
from geopy.distance import vincenty
from pgmabstract import PgmAbstract  

################################################################################

class Address(PgmAbstract):
    
    ''' 
    "/addr" command program. User can search the bikes station with the address.
    '''

    name = "/addr"

    # enum of the state of the program

    REQUEST = 0
    RESPOND = 1
    SEARCH = 2
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

    def check_start(self, msg=None):

        return True

#-------------------------------------------------------------------------------

    def state_start(self, user, msg=None, args=None):
        
        '''
        Request state function. Send message to request the address from the 
        user. Return the enum of the respond state.
        '''

        self.tb.send_message(user, "Please enter the address.")

        return [Address.RESPOND, None]

#-------------------------------------------------------------------------------

    def check_respond(self,  msg):

        '''
        Return whether a msg is a valid command (text form) for the respond 
        state. 
        '''

        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is 'text':
            return True
        else:
            return False

 #-------------------------------------------------------------------------------

    def state_respond(self, user, msg, args=None):

        '''
        The respond state function. Use the address (msg) from the user to 
        search the corresponding address. Send the user message of the 
        corresponding address and ask the user to choose between 'PickUp', 
        'DropOff' or 'WrongAddress'. Return the enum of the search state and the
        corresponding address.
        '''

        content_type, chat_type, chat_id = telepot.glance(msg)
        location = None
        addr = msg['text']

        try:
            g = geocoder.google(addr, key=Address.key)
            location = {'latitude': g.latlng[0], 'longitude': g.latlng[1]}
            corres_addr = geocoder.google([g.latlng[0], g.latlng[1]], method='reverse', key=Address.key)
            self.bot.sendMessage(user, 'Search for ' + corres_addr.address)
        except:
            print("Error accessing geocoder")
            self.tb.send_message(user, "Sorry the geocoder can't find the address :(")
            return [Address.END, None]

        markup = types.ReplyKeyboardMarkup(row_width=1)
        itembtn1 = types.KeyboardButton('PickUp')
        itembtn2 = types.KeyboardButton('DropOff')
        itembtn3 = types.KeyboardButton('WrongAddress')
        markup.add(itembtn1)
        markup.add(itembtn2)
        markup.add(itembtn3)
        self.tb.send_message(user, "Pick up or drop off?", reply_markup=markup)
        
        return [Address.SEARCH, location]
        
#-------------------------------------------------------------------------------

    def check_options(self, msg):

        '''
        The check function for the search state. If the command(msg) is valid
        return true. Otherwise, return false.
        '''
        
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type is not 'text':
            return False
        elif msg['text'] == 'PickUp' or msg['text'] == 'DropOff' or \
        msg['text'] == 'WrongAddress':
                return True
        else:
            return False

#-------------------------------------------------------------------------------

    def state_search(self, user, msg, args):

        '''
        The search state function. If the user replied 'WrongAddress', send 
        message to request the address again and return to the enum of the 
        respond state. Otherwise, search the nearest bike station and send the 
        information to the user. Return the enum of the end state.
        '''

        if msg['text'] == 'WrongAddress':
            self.tb.send_message(user, "Please enter the address.")
            return [Address.RESPOND, None]
        
        try:
            client = citybikes.Client()
            net, dist = next(iter(client.networks.near(args['latitude'], args['longitude'])))
            posi1 = (args['latitude'], args['longitude'])
            sts = net.stations.near(args['latitude'], args['longitude'])
        except:
            print("Error accessing citybikes information")
            self.tb.send_message(user, "Sorry the citybikes network currently"
                "is not operating. Can't access the bike station information. :(")
            return [Address.END, None]

        for stai in sts:
            if msg['text'] == 'DropOff' and stai[0]['empty_slots'] != 0: 
                self.tb.send_location(\
                    user, stai[0]['latitude'], stai[0]['longitude'])
                
                posi2 = (stai[0]['latitude'], stai[0]['longitude'])
                distval = vincenty(posi1, posi2).meters
                distS = "{:.1f}".format(distval)
                num = stai[0]['empty_slots']
                emoji = u"\U0001F17F"*min(10, num)     
                self.tb.send_message(user, "The station {name} has {count} "\
                    "empty slots.\n{bikes}\nIt is {dist} meters away from the address."\
                    .format(name=stai[0]['name'], count=stai[0]['empty_slots'],\
                     dist=distS, bikes=emoji))
                return [Address.END, None]
         
            if msg['text'] == 'PickUp' and stai[0]['free_bikes'] != 0: 
                self.tb.send_location(\
                    user, stai[0]['latitude'], stai[0]['longitude'])
                
                posi2 = (stai[0]['latitude'], stai[0]['longitude'])
                distval = vincenty(posi1, posi2).meters
                distS = "{:.1f}".format(distval)
                num = stai[0]['free_bikes']
                emoji = u"\U0001F6B2"*min(10, num)          
                self.tb.send_message(user, "The station {name} has {count} "\
                    "free bikes.\n{slots}\nIt is {dist} meters away from the address."\
                    .format(name=stai[0]['name'], count=stai[0]['free_bikes'],\
                     dist=distS, slots=emoji))
                return [Address.END, None]

        self.tb.send_message(user, "Sorry no available stations.")

        return [Address.END, None]

#-------------------------------------------------------------------------------    
    
    def __init__(self):

        '''
        The Address Class is initialized so the command execution will be 
        operated by the bot and the tb object (telepot and telebot 
        object) initiated in superclass. Each state corresponding execute 
        function and check function are specified.
        '''

        self.statefun = [self.state_start, self.state_respond, \
                            self.state_search]
        self.check_cmd = [self.check_start, self.check_respond, \
                            self.check_options]
        
        super().__init__()

################################################################################

if __name__ == "__main__":
    '''
    For testing
    '''
    address_class = Address()
