# coding=UTF-8
# https://github.com/eternnoir/pyTelegramBotAPI
import os
import sys

from telebot import TeleBot, types

from config import WITH_WEB, TELEBOT_TOKEN, CONFIG_PATH
from highlights import Highlights, HIGHLIGHTS_PATTERN
from my_logging import checked_load_logging_config, get_logger
from sheet import per_user_status_details, get_welfare_status_for
from web import start_server, kill_server

log = None
highlights = Highlights()


def startup_bot(token):
    global log
    checked_load_logging_config(CONFIG_PATH)

    log = get_logger(__name__)
    if not token:
        log.error('usage: TELEBOT_TOKEN=<token> python %s' % os.path.basename(__file__))
        sys.exit(255)
    log.info('starting %s' % __name__)
    return TeleBot(token)


bot = startup_bot(os.getenv(TELEBOT_TOKEN))


def main():
    try:
        if os.getenv(WITH_WEB):
            start_server()
        start_telegram_poll()
    finally:
        if os.getenv(WITH_WEB):
            kill_server()


def start_telegram_poll():
    log.info('started %s. polling...' % __name__)
    bot.polling()
    log.info('finished polling')


@bot.message_handler(commands=['start', ])
def start(message):
    bot.reply_to(message, 'Hello %s!' % message.from_user.first_name)
    print_help(message)


@bot.message_handler(commands=['start', 'help'])
def print_help(message):
    bot.send_message(message.chat.id,
                     "I'm the bot of the *Südsterne* team.\n"
                     'I listen for #highlight messages and otherwise offer the following commands:\n'
                     '/howarewe - get status of team\n'
                     '/show_highlights - displays the currently available highlights\n'
                     '/send_highlights - sends highlights to yammer with current week tag\n'
                     )


@bot.message_handler(commands=['howarewe'])
def howarewe(message):
    _thinking(message)
    try:
        bot.send_message(message.chat.id,
                         '\n'.join([get_welfare_status_for(name) for name in per_user_status_details().keys()]))
    except Exception, e:
        bot.send_message(message.chat.id, 'failed to obtain status: [%s]' % e.message)


@bot.message_handler(regexp=HIGHLIGHTS_PATTERN)
def collect_highlight(message):
    user = message.from_user.first_name
    if highlights.add(user, unicode(message.text)):
        bot.send_message(message.chat.id, 'collecting highlight for %s: [%s]' % (user, highlights.get(user)))


@bot.message_handler(commands=['show_highlights'])
def show_highlights(message):
    if highlights.is_not_empty():
        bot.send_message(message.chat.id, 'the following highlights are available:\n%s' % highlights.message_string())
    else:
        bot.send_message(message.chat.id, 'no highlights available')


@bot.message_handler(commands=['send_highlights'])
def send_highlights(message):
    show_highlights(message)
    if highlights.is_not_empty():
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        itembtn1 = types.KeyboardButton('yes')
        itembtn2 = types.KeyboardButton('no')
        markup.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, 'really send?', reply_markup=markup)
        bot.register_next_step_handler(message, handle_send_reply)


def handle_send_reply(message):
    if 'yes' == message.text:
        try:
            message_url = highlights.send_to_yammer()
            bot.send_message(message.chat.id, 'highlights posted to yammer: [%s]' % message_url)
        except Exception, e:
            bot.send_message(message.chat.id, 'failed to post to yammer: [%s]' % e.message)

        highlights.clear()
    else:
        bot.send_message(message.chat.id, 'ok, not sending highlights.')


def _thinking(message):
    bot.send_message(message.chat.id, 'calculating welfare status of team...')
    bot.send_chat_action(message.chat.id, 'typing')


if __name__ == '__main__':
    main()
