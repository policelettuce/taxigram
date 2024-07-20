import telebot
import config
import requests
import random
import sqlite3

from telebot import types

bot = telebot.TeleBot(config.token)

con = sqlite3.connect("taxigram.db", check_same_thread=False)
cursor = con.cursor()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "Привет! Я - бот, который поможет тебе найти самое выгодное предложение такси.")
    bot.send_message(message.chat.id, "Выбери, какую из двух точек маршрута ты хочешь отметить. Отправь две геопозиции, а затем нажми третью кнопку.", reply_markup=keyboard())


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id,
                     "Выбери, какую из двух точек маршрута ты хочешь отметить. Затем отправь статичную геопозицию Telegram. Когда укажешь две точки, жми на $$$!")


@bot.message_handler(commands=['check'])
def check(message):
    pass
    # global startpos, finishpos, chatids, switches
    # print("check! ", switches, " ", chatids, " ", startpos, " ", finishpos)


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:                            # if the message, received by bot, is a tg geoposition
        lat = str(message.location.latitude)
        lon = str(message.location.longitude)
        check_if_entry_exists(message.chat.id)                  # if there is no entry in DB for this chat - make one
        ptr = cursor.execute("SELECT pointer FROM Data WHERE chat_id = " + str(message.chat.id) + ";").fetchall()[0][0]

        if ptr == 1:              # pointer == 1 -> setting starting geoposition
            cursor.execute("UPDATE Data SET latitude_1 = " + lat + ", longitude_1 = " + lon + " WHERE chat_id = " + str(message.chat.id) + ";")
            con.commit()
        elif ptr == 2:            # pointer == 2 -> setting finishing geoposition
            cursor.execute("UPDATE Data SET latitude_2 = " + lat + ", longitude_2 = " + lon + " WHERE chat_id = " + str(message.chat.id) + ";")
            con.commit()

    bot.send_message(message.chat.id, 'Точка сохранена! Теперь отметь другую точку или узнай цену поездки по маршруту.')


@bot.message_handler(content_types=['text'])
def buttons(message):
    chat_id = message.chat.id
    if message.text == 'Начало поездки':
        switchto1(message)
        bot.send_message(chat_id, "Отправь точку начала маршрута с помощью геопозиции Telegram...")
    elif message.text == 'Конец поездки':
        switchto2(message)
        bot.send_message(chat_id, "Отправь точку конца маршрута с помощью геопозиции Telegram...")
    elif message.text == '$$$':
        check_if_entry_exists(chat_id)
        cost = int(getcost(chat_id))
        if cost == -1:
            poserror(chat_id)
        else:
            res = formatresult(chat_id, cost)
            bot.send_message(chat_id, res, parse_mode='MarkdownV2')
    else:
        bot.send_message(message.chat.id, "Чего? (invalid input)")


def switchto1(message):
    check_if_entry_exists(message.chat.id)
    cursor.execute("UPDATE Data SET pointer = 1 WHERE chat_id = " + str(message.chat.id) + ";")
    con.commit()


def switchto2(message):
    check_if_entry_exists(message.chat.id)
    cursor.execute("UPDATE Data SET pointer = 2 WHERE chat_id = " + str(message.chat.id) + ";")
    con.commit()

# if there is no entry in DB for this chat - make one
def check_if_entry_exists(userid):
    chat_id = cursor.execute("SELECT chat_id FROM Data WHERE chat_id = " + str(userid) + ";").fetchall()  # fetch 'list' of 'tuple', .fetchall()[0][0] - get actual int

    if not chat_id:     # if there is no such chat in DB - make a new entry
        cursor.execute("INSERT INTO Data (chat_id, latitude_1, longitude_1, latitude_2, longitude_1, pointer) VALUES ("
                       + str(userid) + ", 'NOT_DEFINED', 'NOT_DEFINED', 'NOT_DEFINED', 'NOT_DEFINED', 1);")
        con.commit()

    return userid


def getcost(chat_id):
    positions_list = cursor.execute("SELECT * FROM Data WHERE chat_id = " + str(chat_id) + ";").fetchall()

    start_lat = str(positions_list[0][1])
    start_lon = str(positions_list[0][2])
    finish_lat = str(positions_list[0][3])
    finish_lon = str(positions_list[0][4])

    # check if both geo positions has been set
    # if so - make a formatted string for a GET request and get a trip price from resulting JSON
    if start_lat != 'NOT_DEFINED' and finish_lat != 'NOT_DEFINED':
        route = start_lon + str(",") + start_lat + str("~") + finish_lon + str(",") + finish_lat
        url = 'https://taxi-routeinfo.taxi.yandex.net/taxi_info?clid=' + config.clid + '&apikey=' + config.apikey + '&rll=' + route
        res = requests.get(url)
        json = res.json()
        cost = json['options'][0]['price']
    else:
        cost = -1
    return cost


def poserror(chat_id):
    positions_list = cursor.execute("SELECT * FROM Data WHERE chat_id = " + str(chat_id) + ";").fetchall()
    start_lat = str(positions_list[0][1])
    finish_lat = str(positions_list[0][3])

    if start_lat == 'NOT_DEFINED' and finish_lat == 'NOT_DEFINED':
        bot.send_message(chat_id, 'Сначала нужно отметить обе точки маршрута!')
    elif start_lat != 'NOT_DEFINED' and finish_lat == 'NOT_DEFINED':
        bot.send_message(chat_id, 'Нужно отметить конец маршрута!')
    elif start_lat == 'NOT_DEFINED' and finish_lat != 'NOT_DEFINED':
        bot.send_message(chat_id, 'Нужно отметить начало маршрута!')


def createlink(chat_id):
    positions_list = cursor.execute("SELECT * FROM Data WHERE chat_id = " + str(chat_id) + ";").fetchall()

    start_lat = str(positions_list[0][1])
    start_lon = str(positions_list[0][2])
    finish_lat = str(positions_list[0][3])
    finish_lon = str(positions_list[0][4])

    link = ('https://3.redirect.appmetrica.yandex.com/route?start-lat=' + start_lat + '&start-lon=' + start_lon +
            '&end-lat=' + finish_lat + '&end-lon=' + finish_lon + '&level=50&appmetrica_tracking_id=1178268795219780156')

    return link


def formatresult(chat_id, cost):

    fake1 = cost + random.randint(cost//10*-1, cost//10)
    fake2 = cost + random.randint(cost//10*-1, cost//10)

    url = createlink(chat_id)
    url2 = 'https://youtu.be/dQw4w9WgXcQ'
    url3 = 'https://youtu.be/8aPpF15_gTA'
    res = ('[Яндекс:](' + url + ') ' + str(cost) + " р\n" + '[FakeTaxi 1:](' + url2 + ') ' +
                 str(fake1) + " р\n" + '[FakeTaxi 2:](' + url3 + ') ' + str(fake2) + " р\n")

    return res

def keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Начало поездки")
    item2 = types.KeyboardButton("Конец поездки")
    item3 = types.KeyboardButton("$$$")
    markup.add(item1, item2, item3)

    return markup


bot.polling(none_stop=True)
