from typing import Callable, Any
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import os
# import configparser
import logging
import datanews
import re
import redis

global redis1

def main():
    # Load your token and create an Updater for your Bot
    
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host=(os.environ['HOST']), password=(os.environ['PASSWORD']), port=(os.environ['REDISPORT']))

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))


    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_markdown('''This bot allows you to query news articles from Datanews API.
Available commands:
/help, /start - show this help message.
/{SEARCH_COMMAND} <query> - retrieve news articles containing <query>.
   Example: "/{SEARCH_COMMAND} covid"
/{PUBLISHER_COMMAND} <domain> - retrieve newest articles from <publisher>.
   Example: "/{PUBLISHER_COMMAND} techcrunch.com"
''')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg +  ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def hello(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /hello is issued."""
    try:
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        update.message.reply_text('Good day, ' + msg + '!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <keyword>')

def _fetch_data(update: Update, context: CallbackContext, fetcher: Callable[[str], Any]) -> None:
    if not context.args:
        help_command(update, context)
        return

    query = '"' + ' '.join(context.args) + '"'
    result = fetcher(query)

    if result['status'] == 401:
        update.message.reply_text('API key is invalid')
        return

    if not result['hits']:
        update.message.reply_text('No news is good news')
        return

    last_message = update.message
    for article in reversed(result['hits']):
        text = article['title'] + ': ' + article['url']
        last_message = last_message.reply_text(text)

if __name__ == '__main__':
    main()
