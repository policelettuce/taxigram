import telebot
import config

from telebot import types

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands='start')
def send_welcome(message):
    bot.reply_to(message,
                 "Привет! Я - бот, который поможет тебе найти самое выгодное предложение такси. Для начала просто "
                 "отправь мне геопозицию Telegram с точкой, куда необходимо вызвать такси.")


@bot.message_handler(commands='help')
def send_help(message):
    bot.send_message(message.chat.id,
                     "Чтобы начать, просто отправь мне встроенную геопозицию Telegram, куда нужно заказать машину.")


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        print("latitude: %s; longitude: %s" % (message.location.latitude, message.location.longitude))


bot.polling(none_stop=True)
