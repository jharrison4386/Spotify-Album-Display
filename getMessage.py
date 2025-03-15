#Needed imports
import os
import telebot
import datetime
from datetime import datetime,timedelta

import os.path

#loading calendar scopes and telegram bot token
BOT_TOKEN = "Use telegram bot token"
bot = telebot.TeleBot(BOT_TOKEN)

#var to store message
messageSent=['']

#Hello world command
@bot.message_handler(commands=['hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?") 

#Send message to bot, bot will read second message sent after using command
@bot.message_handler(commands=['message'])
def date_handler(message):
    text = "What is your important message?"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, parse_dates)

#Write message to text file and store in current message list
def writeMessage(message):
    txt = message.text
    f = open('message.txt', 'w')
    f.write(txt)
    f.close
    messageSent[0]=txt
    bot.send_message(message.chat.id, "Message Delivered!", parse_mode="Markdown")

#Turn on telegram bot 
bot.infinity_polling()
