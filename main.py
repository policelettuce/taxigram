import telebot
import config
import random

from telebot import types

bot = telebot.TeleBot(config.token)

chatids = []
switches = []
startpos = []
finishpos = []


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "Привет! Я - бот, который поможет тебе найти самое выгодное предложение такси. Для начала просто "
                     "отправь мне геопозицию Telegram с точкой, куда необходимо вызвать такси.")
    bot.send_message(message.chat.id, "Для начала выбери, какую из двух точек маршрута ты хочешь отметить.", reply_markup=keyboard())


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id,
                     "Для начала выбери, какую из двух точек маршрута ты хочешь отметить.")


@bot.message_handler(commands=['check'])
def check(message):
    global startpos, finishpos, chatids, switches
    print("check! ", switches, " ", chatids, " ", startpos, " ", finishpos)


@bot.message_handler(content_types=["location"])
def location(message):
    global startpos, finishpos, chatids, switches

    if message.location is not None:
        lat = str(message.location.latitude)
        lon = str(message.location.longitude) + str(",")
        localid = findlocalid(message.chat.id)  # передаем chat id и находим для этого чата локальный id

        if switches[localid] == 1:  # switches == 1 -> определяем стартовую позицию
            startpos[localid] = lon + lat  # switches == 2 -> определяем конечную позицию
        elif switches[localid] == 2:
            finishpos[localid] = lon + lat


@bot.message_handler(content_types=['text'])
def buttons(message):
    global chatids, switches
    if message.text == 'Начало поездки':
        switchto1(message)
        bot.send_message(message.chat.id, "Отправь точку начала маршрута с помощью геопозиции Telegram...")
    elif message.text == 'Конец поездки':
        switchto2(message)
        bot.send_message(message.chat.id, "Отправь точку конца маршрута с помощью геопозиции Telegram...")
    elif message.text == '$$$':
        bot.send_message(message.chat.id, "Выкачано 14 000 р. из 28 000 000 р. Продолжить?")
    else:
        bot.send_message(message.chat.id, "Чего? (invalid input)")


def switchto1(message):
    global switches
    localid = findlocalid(message.chat.id)
    switches[localid] = 1
    print("switch at localid ", localid, " changed to 1")


def switchto2(message):
    global switches
    localid = findlocalid(message.chat.id)
    switches[localid] = 2
    print("switch at localid ", localid, " changed to 2")


def findlocalid(userid):
    global startpos, finishpos, chatids, switches

    if userid not in chatids:  # проверяем, есть ли в базе такой chat id
        chatids.append(userid)  # если у нас появляется новый chat id, мы добавляем индекс в листы
        switches.append(1)  # для того, чтобы позже добавлять туда строки геопозиций
        startpos.append("TEST STRING")  # по факту это просто фикс out of range exception
        finishpos.append("STRING TEST")

    localid = -1

    for i in range(0, len(chatids)):  # находим и назначаем localid
        if chatids[i] == userid:
            localid = i

    print("func finished! ", switches, " ", chatids, " ", startpos, " ", finishpos)
    return localid


def keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Начало поездки")
    item2 = types.KeyboardButton("Конец поездки")
    item3 = types.KeyboardButton("$$$")
    markup.add(item1, item2, item3)

    return markup


bot.polling(none_stop=True)
