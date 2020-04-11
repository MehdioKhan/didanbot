import telebot
from telebot import types
import os
import logging
from db import engine, Base
from models import User
from config import BotConfig


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(os.getenv('TOKEN'))
Base.metadata.create_all(engine)


@bot.callback_query_handler(func=lambda call: True)
def check_joined_to_channel(call):
	callback_data=call.reply_markup.data
	caht_id=call.chat.id
	bot.next_step_handlers('',main_menu)


def not_joined_error(chat_id):
	"""
	this method is called when sending an error message to a user
	:param msg: error message to be sent to user
	:param chat_id: chat_id of user
	"""
	inline_markup = types.InlineKeyboardMarkup()
	joined_button = types.InlineKeyboardButton("yahoo",callback_data='y')
	inline_markup.add(joined_button)
	msg = """
		In order to use @{bot_uname} join to sponsor channel
		{sponsor_id}
	""".format(bot_uname=bot.get_me().username,sponsor_id=BotConfig.CHANNEL)
	bot.send_message(chat_id,msg,reply_markup=inline_markup)


def is_joined_to_channel(func):
	"""
	decorator to check if a user is joined to a chat or not
	"""
	def check_joined_to_channel(message):
		valid_status = ('creator', 'administrator', 'member')
		chat = bot.get_chat(BotConfig.CHANNEL)
		user_id = message.chat.id
		try:
			chat_member = bot.get_chat_member(chat.id,user_id)
		except:
			print('Bot is not admin in channel')
			return None
		if chat_member.status in valid_status:
			return func(message)
			# return not_joined_error(user_id)
		else:
			return not_joined_error(user_id)
	return check_joined_to_channel


def main_menu(message):
	markup=types.ReplyKeyboardMarkup()
	about_button = types.KeyboardButton('About')
	support_button = types.KeyboardButton('Support')
	markup.add(about_button,support_button)
	bot.send_message(message.chat.id,'now u can use',reply_markup=markup)


@bot.message_handler(commands=['start', 'help'])
@is_joined_to_channel
def send_welcome(message):
	kwargs={}
	for f in User.fields:
		kwargs[f]=getattr(message.chat,f)
	user,created = User.objects.get_or_create(**kwargs)
	bot.send_message(message.chat.id, "Hello {}".format(user.get_fullname()))
	main_menu(message)


bot.polling()