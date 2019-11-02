import json
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
from datetime import datetime

from graphs import paint_zones, paint_general, paint_detail_graphs
from backend import get_data, set_data

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
markup = ReplyKeyboardMarkup(
    reply_keyboard,
    resize_keyboard=True,
    one_time_keyboard=True
)

CHOOSING, PRESSURE = range(2)
list_graph = {'General': paint_general, 'Details': paint_detail_graphs, 'Zones': paint_zones}


def split_message(text):
    edge_values = [[40, 220], [40, 110], [20, 220]]
    list_enter = text.split(' ')
    data = []

    if len(list_enter) >= 4:
        for n, value in enumerate(list_enter[:3]):
            if value.isdigit() and edge_values[n][0] <= int(value) <= edge_values[n][1]:
                data.append(value)
            elif n == 2 and value == '-':
                if len(data) == 2:
                    data.append(None)
            else:
                data = []
                break
        if data:
            comment = ' '.join(list_enter[3:])
            if len(comment) <= 200 and text != ' ':
                data.append(comment)
            else:
                data = []

    return data


def start(update, context):
    update.message.reply_text(
        "Hello. I'm statistic bot. \n"
        "I'll fix your data arterial pressure, pulse end save it. ",
        reply_markup=markup
    )
    update.message.reply_text(
        "Enter your measurement or print graph."
    )

    return CHOOSING


def graph(update, context):

    chat_id = update.message['chat']['id']

    error, *data = get_data(chat_id)

    if len(data[1]) < 7:
        update.message.reply_text(
            'You need more measurements (more than 7).',
            reply_markup=markup
        )
        return CHOOSING

    if error:
        update.message.reply_text(
            'Error: {0}'.format(error)
        )
        return CHOOSING

    update.message.reply_text(
        "Your graphs: ",
        reply_markup=markup
    )

    for name, func in list_graph.items():

        buffer = func(*data)

        update.message.reply_text(
            f"{name}: ",
            reply_markup=markup
        )

        context.bot.send_photo(
            chat_id=chat_id,
            photo=buffer
        )

    return CHOOSING


def enter_pressure(update, context):

    update.message.reply_text(
        'Enter your arterial pressure in format:\n'
        '   "systolic diastolic pulse comment".\n'
        'If pulse or comment don\'t need for current measurement, write "-" on this place.\n'
        'For example:\n'
        '   1) 120 80 65 hello\n'
        '   2) 120 80 - hello\n'
        '   3) 120 80 - -\n'
    )

    return PRESSURE


def pressure(update, context):

    measurements = [update.message['chat']['id']]
    data = split_message(update.message['text'])
    if data:
        measurements.extend(data)
    else:
        update.message.reply_text(
            "Invalid enter",
            reply_markup=markup
        )
        return CHOOSING
    measurements.append(datetime.now())
    error = set_data(measurements)

    if error:
        update.message.reply_text(
            'Error: {0}'.format(error)
        )
        return CHOOSING

    update.message.reply_text(
        'Fix it.',
        reply_markup=markup
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
