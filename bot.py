import telebot
from telebot import types
import os
import logging
from db import engine, Base
from models import User, LinkVideo
from config import BotConfig, Youtube_dl_options
import youtube_dl

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(os.getenv('TOKEN'))
Base.metadata.create_all(engine)


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


@bot.callback_query_handler(func=lambda call: 'joined_channel' in call.data)
def callback_inline_join_menu(call):
    valid_status = ('creator', 'administrator', 'member')
    channel = bot.get_chat(BotConfig.CHANNEL)
    chat_member = bot.get_chat_member(channel.id, call.message.chat.id)
    if chat_member.status in valid_status:
        send_welcome(call.message)


def join_menu(message):
    inline_markup = types.InlineKeyboardMarkup()
    joined_button = types.InlineKeyboardButton("در کانال ثبت نام کردم", callback_data='joined_channel')
    inline_markup.add(joined_button)
    msg = """
        برای پشتیبانی از محصولات ما در کانال {sponsor_id} عضو شوید .
    """.format(sponsor_id=BotConfig.CHANNEL)
    bot.send_message(message.chat.id, msg, reply_markup=inline_markup)


@bot.message_handler(commands=['start', 'help'])
@is_joined_to_channel
def send_welcome(message):
    kwargs = {}
    for f in User.fields:
        kwargs[f] = getattr(message.chat, f)
    user, created = User.objects.get_or_create(**kwargs)
    msg = '''
    سلام خوش اومدید
    لینک خودتون رو وارد کنید تا برات دانلودش کنیم
    '''
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message(chat_id=message.chat.id, reply_to_message_id=message.message_id, text='OK!')


@bot.message_handler(regexp='https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
@is_joined_to_channel
def download_from_url(message):
    with youtube_dl.YoutubeDL(Youtube_dl_options) as ydl:
        try:
            result = ydl.extract_info(url=message.text)
        except youtube_dl.DownloadError:
            logger.log(level=logging.INFO, msg='link is not valid')
            return None
        link_video = LinkVideo.objects.get(link=message.text)
        if not link_video:
            try:
                video = open('files/' + result.get('title') + '-' + result.get('id') + '.' + result.get('ext'), 'rb')
            except IOError:
                logger.log(level=logging.INFO, msg='error in reading file')
                return None

            try:
                res = bot.send_video(chat_id=message.chat.id,
                                     reply_to_message_id=message.message_id,
                                     data=video)
                LinkVideo.objects.create(link=message.text, video_id=res.video.file_id)
            except:
                logger.log(level=logging.INFO, msg='video dont send')
        else:
            try:
                bot.send_video(chat_id=message.chat.id,
                               reply_to_message_id=message.message_id,
                               data=link_video.video_id)
            except:
                logger.log(level=logging.INFO, msg='video dont send')


bot.polling()
