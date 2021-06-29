import telebot
import config
import requests
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
                     "Привет! Я - бот, который поможет тебе найти самое выгодное предложение такси.")
    bot.send_message(message.chat.id, "Выбери, какую из двух точек маршрута ты хочешь отметить. Отправь две геопозиции, а затем нажми третью кнопку.", reply_markup=keyboard())


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id,
                     "Выбери, какую из двух точек маршрута ты хочешь отметить. Затем отправь статичную геопозицию Telegram. Когда укажешь две точки, жми на $$$!")


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

        if switches[localid] == 1:              # switches == 1 -> определяем стартовую позицию
            startpos[localid] = lon + lat       # switches == 2 -> определяем конечную позицию
        elif switches[localid] == 2:
            finishpos[localid] = lon + lat

    bot.send_message(message.chat.id, 'Точка сохранена! Теперь отметь другую точку или узнай цену поездки по маршруту.')


@bot.message_handler(content_types=['text'])
def buttons(message):
    global chatids, switches
    chatid = message.chat.id
    if message.text == 'Начало поездки':
        switchto1(message)
        bot.send_message(chatid, "Отправь точку начала маршрута с помощью геопозиции Telegram...")
    elif message.text == 'Конец поездки':
        switchto2(message)
        bot.send_message(chatid, "Отправь точку конца маршрута с помощью геопозиции Telegram...")
    elif message.text == '$$$':
        localid = findlocalid(chatid)
        cost = int(getcost(localid))
        if cost == -1:
            poserror(chatid, localid)
        else:
            res = formatresult(localid, chatid, cost)
            bot.send_message(chatid, res, parse_mode='MarkdownV2')
    else:
        bot.send_message(message.chat.id, "Чего? (invalid input)")


def switchto1(message):
    global switches
    localid = findlocalid(message.chat.id)
    switches[localid] = 1


def switchto2(message):
    global switches
    localid = findlocalid(message.chat.id)
    switches[localid] = 2


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

    return localid


def getcost(localid):
    global startpos, finishpos, chatids, switches

    if startpos[localid] != 'TEST STRING' and finishpos[localid] != 'STRING TEST':
        route = startpos[localid] + str("~") + finishpos[localid]
        url = 'https://taxi-routeinfo.taxi.yandex.net/taxi_info?clid=' + config.clid + '&apikey=' + config.apikey + '&rll=' + route
        res = requests.get(url)
        json = res.json()
        cost = json['options'][0]['price']
    else:
        cost = -1;
    return cost;


def poserror(chatid, localid):
    global startpos, finishpos

    if startpos[localid] == 'TEST STRING' and finishpos[localid] == 'STRING TEST':
        bot.send_message(chatid, 'Сначала нужно отметить обе точки маршрута!')
    elif startpos[localid] != 'TEST STRING' and finishpos[localid] == 'STRING TEST':
        bot.send_message(chatid, 'Нужно отметить конец маршрута!')
    elif startpos[localid] == 'TEST STRING' and finishpos[localid] != 'STRING TEST':
        bot.send_message(chatid, 'Нужно отметить начало маршрута!')


def createlink(localid):
    global startpos, finishpos
    start = startpos[localid].split(sep=',')
    finish = finishpos[localid].split(sep=',')

    link = ('https://3.redirect.appmetrica.yandex.com/route?start-lat=' + start[1] + '&start-lon=' + start[0] +
            '&end-lat=' + finish[1] + '&end-lon=' + finish[0] + '&level=50&appmetrica_tracking_id=1178268795219780156')

    return link;


def formatresult(localid, chatid, cost):

    fake1 = cost + random.randint(cost//10*-1, cost//10)
    fake2 = cost + random.randint(cost//10*-1, cost//10)

    url = createlink(localid)
    url2 = 'https://youtu.be/dQw4w9WgXcQ'
    url3 = 'https://youtu.be/8aPpF15_gTA'
    res = ('[Яндекс:](' + url + ') ' + str(cost) + " р\n" + '[FakeTaxi 1:](' + url2 + ') ' +
                 str(fake1) + " р\n" + '[FakeTaxi 2:](' + url3 + ') ' + str(fake2) + " р\n")

    return res;

def keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Начало поездки")
    item2 = types.KeyboardButton("Конец поездки")
    item3 = types.KeyboardButton("$$$")
    markup.add(item1, item2, item3)

    return markup


bot.polling(none_stop=True)
