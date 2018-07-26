# coding=UTF-8
# https://github.com/eternnoir/pyTelegramBotAPI
import sys
import time

from requests import RequestException
from telebot import TeleBot, types

from my_logging import checked_load_logging_config, basic_logger_config, get_logger
from sheet import retrieve_team_status, get_welfare_status_for

log = None
highlights = {}


def startup_bot(arguments):
    global log
    checked_load_logging_config("~/.python/logging.conf")

    basic_logger_config()

    log = get_logger(__name__)
    log.info('starting %s' % __name__)
    try:
        return TeleBot(arguments[1])
    except:
        log.error('usage: python %s <TOKEN>', arguments[0])
        sys.exit(255)


bot = startup_bot(sys.argv)


def main():
    start_telegram_poll()


def start_telegram_poll():
    while True:
        try:
            log.info('started %s. polling...' % __name__)
            bot.polling()
            log.info('finished polling')
            break
        except RequestException, e:
            log.warn('restarting after RequestException: %s', e.message)
            bot.stop_polling()
            time.sleep(5)


@bot.message_handler(commands=['start', ])
def start(message):
    bot.reply_to(message, 'Hello %s!' % message.from_user.first_name)
    print_help(message)


@bot.message_handler(commands=['start', 'help'])
def print_help(message):
    bot.send_message(message.chat.id, 'available commands:\n'
                                      '/howarewe - get status of team\n'
                     )


@bot.message_handler(commands=['howarewe'])
def howarewe(message):
    _thinking(message)
    bot.send_message(message.chat.id,
                     '\n'.join([get_welfare_status_for(name) for name in retrieve_team_status().keys()]))


@bot.message_handler(regexp='#highlight')
def collect_highlight(message):
    highlights[message.from_user.first_name] = str(message.text)
    bot.send_message(message.chat.id, 'collecting highlight for %s: [%s]' % (
        message.from_user.first_name, highlights[message.from_user.first_name]))


@bot.message_handler(commands=['show_highlights'])
def show_highlights(message):
    if highlights:
        bot.send_message(message.chat.id, 'the following highlights are available: %s' % '\n'.join(
            '%s: %s' % (key, val) for (key, val) in highlights.iteritems()))
    else:
        bot.send_message(message.chat.id, 'no highlights available')


@bot.message_handler(commands=['send_highlights'])
def send_highlights(message):
    show_highlights(message)
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('yes')
    itembtn2 = types.KeyboardButton('no')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, 'really send?', reply_markup=markup)
    bot.register_next_step_handler(message, handle_send_reply)


def handle_send_reply(message):
    if 'yes' == message.text:
        bot.send_message(message.chat.id, 'sending highlights...')
        highlights.clear()
    else:
        bot.send_message(message.chat.id, 'ok, not sending highlights.')

def _thinking(message):
    bot.send_message(message.chat.id, 'calculating welfare status of team...')
    bot.send_chat_action(message.chat.id, 'typing')


if __name__ == '__main__':
    main()
