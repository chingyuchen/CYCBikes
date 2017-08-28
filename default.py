################################################################################
'''
File: default.py
Author: Ching-Yu Chen

Description:
default.py contains Default class, which is a program object of the "/default" 
command. Default pgm provides the bike station information by the given current 
location or favorite locations from the users.

'''
################################################################################

import citybikes
import sqlite3
import abc
import telepot   
import telebot
from telebot import types
from geopy.distance import vincenty
from pgmabstract import PgmAbstract

################################################################################

class Default(PgmAbstract):
    
    ''' 
    "/default" command program. Ask the user to send current location or choose 
    the favorite locations. Then use the respond message to find and send the 
    station information. The default program is the standby running program.
    '''

    name = "/default"
    
    
    # enum of the state of the program

    START = 0
    RESPOND = 1
    SEARCH = 2
    END = -1


#-------------------------------------------------------------------------------

    def check_start(self, msg=None):
        return True

#-------------------------------------------------------------------------------

    def state_start(self, user, msg=None, args=None):
        
        '''
        The start state function, return the enum of the next state function 
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
        self.tb.send_message(user, "Where would you like to search?", \
            reply_markup=markup)

        return [Default.RESPOND, None]

#-------------------------------------------------------------------------------

    def check_respond(self, msg):

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

    def state_respond(self, user, msg, args=None):

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
            
            conn = sqlite3.connect(self.sqlfile)
            cur = conn.cursor()
            cur.execute('SELECT * FROM Favs WHERE id = ?', (user,))
            fav_dict = cur.fetchone()
            
            if msg['text'] == 'fav1': 
                if fav_dict is None or fav_dict[1] is None: # bad index
                    self.bot.sendMessage(user, 'The 1st favorite location is'
                        ' not set yet. Please use /editFav to set')
                    conn.close()
                    return [Default.END, None]
                else:
                    location = {'latitude': fav_dict[1], 'longitude': fav_dict[2]}
                    
            
            elif msg['text'] == 'fav2':
                if fav_dict is None or fav_dict[3] is None: # bad index
                    self.bot.sendMessage(user, 'The 2nd favorite location is'
                        ' not set yet. Please use /editFav to set')
                    conn.close()
                    return [Default.END, None]
                else:
                    location = {'latitude': fav_dict[3], 'longitude': fav_dict[4]}

            else:
                if fav_dict is None or fav_dict[5] is None: # bad index
                    self.bot.sendMessage(user, 'The 3rd favorite location is'
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
        self.tb.send_message(user, "Pick up or drop off?", reply_markup=markup)
        
        return [Default.SEARCH, args]
        
#-------------------------------------------------------------------------------

    def check_pickordrop(self, msg):

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

    def state_search(self, user, msg, args):
        
        '''
        The search state function. Use the location in the args to search the 
        nearest bike station. Send the information of the bike station to the 
        user and return the enum of the end state function.
        '''
        
        location_s = args[0]
        lat = args[1]['latitude']
        lon = args[1]['longitude']
        posi1 = (lat, lon)
        
        try:
            client = citybikes.Client()
            net, dist = next(iter(client.networks.near(lat, lon)))
            sts = net.stations.near(lat, lon)
        except:
            print("Error accessing citybikes information")
            self.tb.send_message(user, "Sorry the citybikes network currently"
                "is not operating. Can't access the bike station information. :(")
            return [Default.END, None]


        for stai in sts:
            if msg['text'] == 'PickUp' and stai[0]['free_bikes'] != 0: 
                self.tb.send_location(user, \
                    stai[0]['latitude'], stai[0]['longitude'])
                
                posi2 = (stai[0]['latitude'], stai[0]['longitude'])
                distval = vincenty(posi1, posi2).meters
                distS = "{:1.1f}".format(distval)
                num = stai[0]['free_bikes']
                emoji = u"\U0001F6B2"*min(10, num)
                self.tb.send_message(user, "The station {name} has {count} "\
                    "free bikes.\n{bikes}\nIt is {dist} meters away from {targetloca}."\
                    .format(name=stai[0]['name'], count=num,\
                     dist=distS, targetloca=location_s, bikes=emoji))
                
                return [Default.END, None]
         
            if msg['text'] == 'DropOff' and stai[0]['empty_slots'] != 0: 
                self.tb.send_location(user, \
                    stai[0]['latitude'], stai[0]['longitude'])
                
                posi2 = (stai[0]['latitude'], stai[0]['longitude'])
                distval = vincenty(posi1, posi2).meters
                distS = "{:.1f}".format(distval)
                num = stai[0]['empty_slots']
                emoji = u"\U0001F17F"*min(10, num)
                self.tb.send_message(user, "The station {name} has {count}"\
                    " empty slots.\n{slots}\nIt is {dist} meters away from {targetloca}."\
                    .format(name=stai[0]['name'], count=stai[0]['empty_slots'],\
                     dist=distS, targetloca=location_s, slots=emoji))
                
                return [Default.END, None]

        self.tb.send_message(user, "Sorry no available stations.")

        return [Default.END, None]

#-------------------------------------------------------------------------------    
    
    def __init__(self):

        '''
        The Default Class is initialized so the command execution will be 
        operated by the bot and the tb object (telepot and telebot 
        object) initiated in superclass. Each state corresponding execute 
        function and check function are specified.
        '''

        self.statefun = [self.state_start, self.state_respond, \
                            self.state_search]
        self.check_cmd = [self.check_start, self.check_respond, \
                            self.check_pickordrop]
        super().__init__()
        

################################################################################

if __name__ == "__main__":
    
    ''' 
    For testing
    '''
   
    default_class = Default()

