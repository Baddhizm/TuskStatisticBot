import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap, Normalize
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
import io
import sqlite3
from datetime import datetime, timedelta
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
markup = ReplyKeyboardMarkup(
    reply_keyboard,
    resize_keyboard=True,
    one_time_keyboard=True
)

CHOOSING, PRESSURE = range(2)
edge_syst = [40, 100, 120, 130, 140, 150, 160, 170, 220]
edge_diast = [40, 55, 80, 85, 90, 95, 100, 110, 120]
colors = ['#00FFFF', '#00FFFF', '#00FF00', '#FFFF00', '#FFFF00', '#FFA500', '#FFA500', '#FF0000', '#FF0000']


def split_message(text):
    list_enter = text.split(' ')
    if len(list_enter) == 2 and all(c.isdigit() for c in list_enter):
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


def get_cmap(high, low, edges, name):

    def get_edge(value):
        return (value - low)/(high - low)

    colors_cmap = []
    for n, edge in enumerate(edges):
        colors_cmap.append((get_edge(edge), colors[n]))
    cmap = LinearSegmentedColormap.from_list('{0}'.format(name), colors_cmap, N=729)
    return cmap


def paint_graph(x, y1, y2):

    plt.figure(figsize=(12, 6))

    # Plot lines
    plt.plot(x, y1, '#D3D3D3', zorder=1)
    plt.plot(x, y2, '#D3D3D3', zorder=1)

    # Systolic points
    one = plt.scatter(
        x, y1, c=y1, s=50,
        cmap=get_cmap(220, 40, edge_syst, 'one'),
        norm=Normalize(vmin=40, vmax=220),
        edgecolors='black', zorder=2
    )
    # Diastolic points
    two = plt.scatter(
        x, y2, c=y2, s=50,
        cmap=get_cmap(120, 40, edge_diast, 'two'),
        norm=Normalize(vmin=40, vmax=120),
        edgecolors='black', zorder=2
    )

    # Set two colorbar right
    cbar_1 = plt.colorbar(one)
    cbar_1.set_label("systolic edges")
    cbar_2 = plt.colorbar(two)
    cbar_2.set_label("diastolic edges")

    # Set axis limit
    plt.ylim(40, 220)
    plt.xlim(min(x).date(), (max(x) + timedelta(days=1)).date())

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    plt.grid(True)
    plt.gcf().autofmt_xdate()


def graph(update, context):

    chat_id = update.message['chat']['id']

    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    sql = "SELECT systolic, diastolic, date FROM measurements WHERE id_chat = ? ORDER BY id;"
    try:
        cursor.execute(sql, (chat_id,))
    except Exception as e:
        update.message.reply_text(
            'Error: {0}'.format(e)
        )
        return CHOOSING

    y1, y2, x = zip(*cursor)
    cursor.close()

    update.message.reply_text(
        "Your graph: ",
        reply_markup=markup
    )
    x = list(map(lambda y: datetime.strptime(y,  "%Y-%m-%d %H:%M:%S.%f"), x))

    paint_graph(x, y1, y2)

    # Put graph in buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    context.bot.send_photo(
        chat_id=chat_id,
        photo=buffer
    )

    # Close plot
    plt.close()

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
            "Invalid enter",
            reply_markup=markup
        )
        return CHOOSING

    measurement.append(datetime.now())
    try:
        cursor.execute(sql, tuple(measurement))
    except Exception as e:
        update.message.reply_text(
            'Error: {0}'.format(e)
        )
        return CHOOSING

    connection.commit()
    cursor.close()

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
