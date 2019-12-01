from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
from telegram.ext.dispatcher import run_async
from datetime import datetime
import pytz
import os

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

reply_keyboard = [['Pressure', 'Graph'], ['Rules', 'Data']]
markup = ReplyKeyboardMarkup(
    reply_keyboard,
    resize_keyboard=True,
    one_time_keyboard=True
)

file_format = ReplyKeyboardMarkup(
    [['json', 'csv']],
    resize_keyboard=True,
    one_time_keyboard=True
)

CHOOSING, PRESSURE, CHOOSING_FORMAT = range(3)
list_graph = {'General': paint_general, 'Details': paint_detail_graphs, 'Zones': paint_zones}


def split_message(text):
    edge_values = [[40, 220], [40, 110], [20, 220]]
    list_enter = text.split(' ')
    data = []

    if len(list_enter) < 5:
        list_enter.extend(['-'] * (5 - len(list_enter)))

    if len(list_enter) >= 5:
        if list_enter[0] in ['r', 'l']:
            data.append(list_enter[0])
        for n, value in enumerate(list_enter[1:4]):
            if value.isdigit() and edge_values[n][0] <= int(value) <= edge_values[n][1]:
                data.append(value)
            elif n == 2 and value == '-':
                if len(data) == 3:
                    data.append(None)
            else:
                data = []
                break
        if data:
            comment = ' '.join(list_enter[4:])
            if len(comment) <= 200 and text != ' ':
                data.append(comment)
            else:
                data = []

    return data


@run_async
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


@run_async
def graph(update, context):

    chat_id = update.message['chat']['id']
    error, data = get_data(chat_id)

    if error:
        update.message.reply_text(
            'Error: {0}'.format(error)
        )
        return CHOOSING

    y1, y2, x, hand = zip(*data)

    if len(x) < 7:
        update.message.reply_text(
            'You need more measurements (more than 7).',
            reply_markup=markup
        )
        return CHOOSING

    update.message.reply_text(
        "Your graphs: ",
        reply_markup=markup
    )

    for name, func in list_graph.items():

        buffer = func(x, y1, y2, hand)

        update.message.reply_text(
            f"{name}: ",
            reply_markup=markup
        )

        context.bot.send_document(
            chat_id=chat_id,
            document=buffer
        )

    return CHOOSING


@run_async
def enter_pressure(update, context):

    update.message.reply_text(
        'Enter your arterial pressure:'
    )

    return PRESSURE


@run_async
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

    measurements.append(datetime.now(pytz.timezone(os.environ['TZ'])))
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


@run_async
def choosing_format(update, context):

    update.message.reply_text(
        'Choose format:',
        reply_markup=file_format
    )

    return CHOOSING_FORMAT


@run_async
def datafile(update, context):

    import io
    import pandas as pd

    choice = update.message['text']
    choice = choice if choice in ['json', 'csv'] else 'csv'

    chat_id = update.message['chat']['id']
    error, data = get_data(chat_id, 'a')

    if error:
        update.message.reply_text(
            'Error: {0}'.format(error)
        )
        return CHOOSING

    buffer = io.StringIO()
    df = pd.DataFrame(data=data)
    eval(f'df.to_{choice}(buffer)')
    buffer.seek(0)

    update.message.reply_text(
        'Your data:',
        reply_markup=markup
    )

    context.bot.send_document(
        chat_id=chat_id,
        document=io.BytesIO(buffer.read().encode('utf8')),
        filename=f'data.{choice}'
    )

    return CHOOSING


@run_async
def rules(update, context):

    update.message.reply_text(
        'Format for input arterial pressure:\n'
        '   "r/l (right/left hand) systolic(40-220) diastolic(40-110) pulse(20-220) comment".\n'
        'If you don\'t want enter pulse or comment write "-" on this place.\n'
        'For example:\n'
        '   1) r 120 80 65 hello\n'
        '   2) l 120 80 - hello\n'
        '   3) r 120 80 70\n'
        '   4) l 120 80\n',
        reply_markup=markup
    )

    return CHOOSING


@run_async
def end(update, context):

    update.message.reply_text(
        "Good buy"
    )

    return ConversationHandler.END


def main():
    updater = Updater(
        os.environ['TOKEN'],
        use_context=True
    )
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(Filters.regex('^Pressure$'), enter_pressure),
                MessageHandler(Filters.regex('^Graph$'), graph),
                MessageHandler(Filters.regex('^Data$'), choosing_format),
                MessageHandler(Filters.regex('^Rules$'), rules)
            ],
            PRESSURE: [MessageHandler(Filters.text, pressure)],
            CHOOSING_FORMAT: [
                MessageHandler(Filters.regex('^csv$'), datafile),
                MessageHandler(Filters.regex('^json$'), datafile),
            ],
        },
        fallbacks=[CommandHandler('end', end)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
