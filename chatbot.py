from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import os
# import configparser
import logging
import requests

from news_file import get_news_from_keyword

#Chen Zixin 
from bs4 import BeautifulSoup
import itertools
import random
import time
from firebase import firebase
firebase = firebase.FirebaseApplication(os.environ['FireBase_url'], None)
#Chen Zixin 

def main():
    # Load your token and create an Updater for your Bot
    
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("news", news))
    dispatcher.add_handler(CommandHandler("comment", comment_command))
    

#Chen Zixin 
    dispatcher.add_handler(CommandHandler("food", food_command))
    dispatcher.add_handler(CommandHandler("24", twentyfour_command))
    dispatcher.add_handler(CommandHandler("gamename", gamename_command))
    dispatcher.add_handler(CommandHandler("yes", yes_command))
    dispatcher.add_handler(CommandHandler("no", no_command))
    dispatcher.add_handler(CommandHandler("24ranking", ranking_command))

#Chen Zixin 

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
    update.message.reply_text('command: /help, /add, /hello')

def news(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /news is issued."""
    try:
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        global news_list
        news_list = get_news_from_keyword(msg)[1]
        for i in range(0,len(news_list)):
            update.message.reply_text('Index ' + str(i))
            update.message.reply_text(news_list[i])
            update.message.reply_text("Commnet:" + firebase.get('/comments/'+news_list[0][i], None))
            global index
            index = i
        update.message.reply_text('You cancomment each news by typing /review_comments or /comment <index> of the news')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /news <keyword>')

def comment_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /comment is issued."""
    try:
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        comment = context.args[1]
        try: 
            news_list[int[msg]]
            url = news_list[0][index]
            firebase.post('/comments/'+url, str(comment))
        except:update.message.reply_text('Invalid input. Usage: /review_comments <number>')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /comment <keyword>')

def twentyfour_command(update:Update, context:CallbackContext)->None:
    update.message.reply_text('Welcome to game 24 point!')
    update.message.reply_text('Enter your game name by /gamename')
    update.message.reply_text('View ranking by enter /24ranking')
    #update.message.reply_text(number)
    #update.message.reply_text(ans)

def gamename_command(update:Update, context:CallbackContext)->None:
    logging.info(context.args[0])
    global name
    name = context.args[0]
    number =[]
    for i in range(0,4):
        number.append(random.randint(1,10))
    global ans
    ans = twentyfour(number)
    update.message.reply_text(name+',your question is'+str(number).strip('[]')+'!')
    global start
    start = time.time()
    update.message.reply_text('Answer /yes or /no')


def yes_command(update:Update, context:CallbackContext)->None:
    if ans !=False:
        update.message.reply_text('You win!')
        update.message.reply_text(ans)
        global end
        end = time.time()
        timeuse = end -start
        timeuse = round(timeuse, 2)
        update.message.reply_text('Timeuse:'+str(timeuse))
        firebase.put('/gamename',name,str(timeuse))
    if ans ==False:
        update.message.reply_text('You lose!')


def no_command(update:Update, context:CallbackContext)->None:
    if ans == False:
        update.message.reply_text('You win!')
        global end
        end = time.time()
        timeuse = end -start
        timeuse = round(timeuse, 2)
        update.message.reply_text('Timeuse:'+str(timeuse))
        firebase.put('/gamename',name,str(timeuse))
    if ans !=False:
        update.message.reply_text('You lose!')

def ranking_command(update:Update, context:CallbackContext)->None:
    r=firebase.get('/gamename',None)
    for k, v in r.items():
        r[k] = float(v)
    r={k: v for k,v in sorted(r.items(), key=lambda item: item[1])}
    update.message.reply_text(r)





def twentyfour(cards):
    for nums in itertools.permutations(cards): # 四个数
        for ops in itertools.product('+-*/', repeat=3): # 三个运算符（可重复！）
            # 构造三种中缀表达式 (bsd)
            bds1 = '({0}{4}{1}){5}({2}{6}{3})'.format(*nums, *ops)  # (a+b)*(c-d)
            bds2 = '(({0}{4}{1}){5}{2}){6}{3}'.format(*nums, *ops)  # (a+b)*c-d
            bds3 = '{0}{4}({1}{5}({2}{6}{3}))'.format(*nums, *ops)  #  a/(b-(c/d))
            
            for bds in [bds1, bds2, bds3]: # 遍历
                try:
                    if abs(eval(bds) - 24.0) < 1e-10:   # eval函数
                        return bds
                except ZeroDivisionError: # 零除错误！
                    continue
    
    return False


def food_command(update:Update, context:CallbackContext)->None:
    logging.info(context.args[0])
    msg = context.args[0]
    userSeach=msg
    mainUrl='https://search.bilibili.com/all?keyword='+userSeach
    mainSoup = BeautifulSoup(requests.get(mainUrl).text, "html.parser")
    item=mainSoup.find_all('li',class_="video-item matrix")[0]
    val=item.find('a',class_="img-anchor")
    
    subUrl=val["href"];
    subSoup = BeautifulSoup(requests.get('https:'+subUrl).text.strip(), "html.parser")
    
    update.message.reply_text(val["title"])
    update.message.reply_text(subSoup.find(itemprop="image")["content"])
    update.message.reply_text('https:'+val["href"])



if __name__ == '__main__':
    main()
