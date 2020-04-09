import telebot
import os
import logging
from db import engine, Base
from models import User


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(os.getenv('TOKEN'))
Base.metadata.create_all(engine)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	kwargs={}
	for f in User.fields:
		kwargs[f]=getattr(message.chat,f)
	user,created = User.objects.get_or_create(**kwargs)
	bot.reply_to(message, "Hello {}".format(user.get_fullname()))


bot.polling()