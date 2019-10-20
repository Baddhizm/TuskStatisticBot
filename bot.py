import json
import matplotlib.pyplot as plt
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
import io
import sqlite3
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


def split_message(text):
    list_enter = text.split(' ')
    if len(list_enter) == 2 and all(map(lambda c: c.isdigit(), list_enter)):
        return True, map(int, list_enter)
    else:
        return False, ''


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
    chat_id = update.message['chat']['id']

    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    sql = "SELECT systolic, diastolic, date FROM measurements WHERE id_chat = ? ORDER BY id"
    try:
        cursor.execute(sql, (chat_id,))
    except Exception as e:
        print(e)

    y1, y2, x = zip(*cursor)
    cursor.close()

    # y1, y2, x = zip(*cursor)
    update.message.reply_text(
        "Your graph: "
    )
    x = list(map(lambda y: datetime.strptime(y,  "%Y-%m-%d %H:%M:%S.%f"), x))
    plt.plot(x, y1, marker='o', label="systolic")
    plt.plot(x, y2, marker='^', label="diastolic")
    plt.gcf().autofmt_xdate()
    plt.legend()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    context.bot.send_photo(
        chat_id=chat_id,
        photo=buffer
    )
    plt.clf()

    return CHOOSING


def enter_pressure(update, context):

    update.message.reply_text(
        'Enter your arterial pressure: '
    )

    return PRESSURE


def pressure(update, context):

    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    sql = "INSERT INTO measurements (id_chat, systolic, diastolic, date) VALUES (?, ?, ?, ?)"

    measurement = [update.message['chat']['id']]
    check, data = split_message(update.message['text'])
    if check:
        measurement.extend(data)
    else:
        update.message.reply_text(
            "Invalid enter"
        )
        return CHOOSING

    measurement.append(datetime.now())
    try:
        cursor.execute(sql, tuple(measurement))
    except Exception as e:
        print(e)
    connection.commit()
    cursor.close()

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
    updater = Updater(
        conf['TOKEN'],
        request_kwargs=conf['REQUEST_KWARGS'],
        use_context=True
    )
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
