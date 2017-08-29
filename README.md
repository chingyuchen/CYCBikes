# CYCTelebot

## About
CYCTelebot is a telegram bot project in python3. The bot provides the real-time 
information of the world-wide bike-share system. The bot is currently running on 
telegram (@cycbikes_bot).

## Installation
pip3 install git+https://github.com/chingyuchen/CYCTelebot.git

## Usage

### Request bike-share information from CYCBikes
Simply add (@cycbikes_bot) as friend on telegram and start the chat.

### Run on your own bot
To run the cyctelebot on your own telegram (i.e. let your own bot provides the 
bike-share information service), you need to: 

1. download all the files in CYCTelebot. 
2. Create file cycbikes_TOKEN in the same directory and write the token of your 
own bot in the file.
3. use python3 to execute cyctelebot.py
`python3 cyctelebot.py` or `./cyctelebot.py` or `./cycbikes`

Then your bot can start to look for bike-share information for the users!

### Add commands
All the command programs are subclasses of PgmAbstract in pgmabstract module 
(pgmabstract.py). One can add new command program by writing a subclass of new 
program which inherits PgmAbstact in the same directory. Then add the 
corresponding ("/new_command" : "NewProgramSubclassName") in the list of the 
commandsmap.json file.