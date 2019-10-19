import json
import matplotlib.pyplot as plt
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
import io
from datetime import datetime
plt.switch_backend('Agg')


"""
Get configuration
Template, for example:
{
    "TOKEN": "YOUR TOKEN",
    "REQUEST_KWARGS":{
        "proxy_url": "PROXY"
    }
}
"""
with open('configuration.json') as json_data_file:
    conf = json.load(json_data_file)


reply_keyboard = [['Pressure', 'Graph']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

CHOOSING, PRESSURE = range(2)
list_measurements = []
tt = [[120, 60], [140, 70], [150, 90]]


def split_message(text):
    return map(int, text.split(' '))


def start(update, context):
    update.message.reply_text(
        "Hello. I'm statistic bot. \n"
        "I'll fix your data arterial pressure end save it. ",
        reply_markup=markup
    )
    update.message.reply_text(
        "Enter your arterial pressure or print graph."
    )

    return CHOOSING


def graph(update, context):
    y1, y2, x = zip(*list_measurements)
    update.message.reply_text(
        "Your graph: "
    )
    plt.plot(x, y1, marker='o', label="systolic")
    plt.plot(x, y2, marker='^', label="diastolic")
    plt.gcf().autofmt_xdate()
    plt.legend()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    context.bot.send_photo(
        chat_id=update.message['chat']['id'],
        photo=buffer
    )

    return CHOOSING


def enter_pressure(update, context):

    update.message.reply_text(
        'Enter your arterial pressure: '
    )

    return PRESSURE


def pressure(update, context):

    measurement = list(split_message(update.message['text']))
    measurement.append(datetime.now())
    list_measurements.append(measurement)
    print(list_measurements)

    update.message.reply_text(
        'Fix it.'
    )

    return CHOOSING


def end(update, context):
    update.message.reply_text(
        "Good buy"
    )

    return ConversationHandler.END


def main():
    updater = Updater(conf['TOKEN'], request_kwargs=conf['REQUEST_KWARGS'], use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(Filters.regex('^Pressure$'), enter_pressure),
                MessageHandler(Filters.regex('^Graph$'), graph)
            ],
            PRESSURE: [MessageHandler(Filters.text, pressure)]
        },
        fallbacks=[CommandHandler('end', end)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
