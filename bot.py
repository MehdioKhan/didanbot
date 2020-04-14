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


# @bot.callback_query_handler(func=lambda call: True)
# def check_joined_to_channel(call):
#     callback_data = call.reply_markup.data
#     caht_id = call.chat.id
#     bot.next_step_handlers('', main_menu)
@bot.callback_query_handler(func=lambda call: 'joined_channel' in call.data)
def callback_inline_join_menu(call):
    valid_status = ('creator', 'administrator', 'member')
    channel = bot.get_chat(BotConfig.CHANNEL)
    chat_member = bot.get_chat_member(channel.id, call.message.chat.id)
    if chat_member.status in valid_status:
        send_welcome(call.message)
    else:
        join_menu(call.message)


@bot.callback_query_handler(func=lambda call: 'about_me' in call.data)
def callback_inline_about_me(call):
    pass


@bot.callback_query_handler(func=lambda call: 'start_app' in call.data)
def callback_inline_start_app(call):
    start_menu(call.message)


@bot.callback_query_handler(func=lambda call: 'youtube' in call.data)
def callback_inline_youtube(call):
    bot.send_message(call.message.chat.id, 'لطفا لینک خود را وارد کنید :')


@bot.callback_query_handler(func=lambda call: 'radio_javan' in call.data)
def callback_inline_radio_javan(call):
    pass


@bot.callback_query_handler(func=lambda call: 'aparat' in call.data)
def callback_inline_aparat(call):
    pass


def join_menu(message):
    inline_markup = types.InlineKeyboardMarkup()
    joined_button = types.InlineKeyboardButton("در کانال ثبت نام کردم", callback_data='joined_channel')
    inline_markup.add(joined_button)
    msg = """
        برای پشتیبانی از محصولات ما در کانال {sponsor_id} عضو شوید .
    """.format(sponsor_id=BotConfig.CHANNEL)
    bot.send_message(message.chat.id, msg, reply_markup=inline_markup)


def main_menu(message):
    """
    this method create main menu with inline mode
    :return:
    """
    inline_markup = types.InlineKeyboardMarkup()
    about_me = types.InlineKeyboardButton('درباره ما', callback_data='about_me')
    start_app = types.InlineKeyboardButton('شروع', callback_data='start_app')
    inline_markup.row(start_app)
    inline_markup.row(about_me)
    msg = """
        این ربات برای راحتی دانلود شما توسعه داده شده است
    """
    bot.send_message(message.chat.id, msg, reply_markup=inline_markup)


def start_menu(message):
    """
    this method create start menu with inline mode
    :return:
    """
    inline_markup = types.InlineKeyboardMarkup()
    youtube = types.InlineKeyboardButton('دانلود از youtube :', callback_data='youtube')
    radio_javan = types.InlineKeyboardButton('دانلود از رادیو جوان :', callback_data='radio_javan')
    aparat = types.InlineKeyboardButton('دانلود از آپارات :', callback_data='aparat')
    inline_markup.row(youtube)
    inline_markup.row(radio_javan)
    inline_markup.row(aparat)
    msg = """
        این ربات برای راحتی دانلود شما توسعه داده شده است
    """
    bot.send_message(message.chat.id, msg, reply_markup=inline_markup)


def is_joined_to_channel(func):
    """decorator to check if a user is joined to a chat or not"""

    def check_joined_to_channel(message):
        valid_status = ('creator', 'administrator', 'member')
        chat = bot.get_chat(BotConfig.CHANNEL)
        user_id = message.chat.id
        try:
            chat_member = bot.get_chat_member(chat.id, user_id)
        except:
            logger.log(level=logging.INFO, msg='Bot is not admin in channel')
            return None
        if chat_member.status in valid_status:
            return func(message)
        else:
            return join_menu(message)

    return check_joined_to_channel


@bot.message_handler(commands=['start', 'help'])
@is_joined_to_channel
def send_welcome(message):
    kwargs = {}
    for f in User.fields:
        kwargs[f] = getattr(message.chat, f)
    user, created = User.objects.get_or_create(**kwargs)
    main_menu(message)


@bot.message_handler(regexp='https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
@is_joined_to_channel
def download_from_url(message):
    pass


bot.polling()
