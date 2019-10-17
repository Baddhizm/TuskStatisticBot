import json
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

with open('configuration.json') as json_data_file:
    conf = json.load(json_data_file)

PRESSURE = range(1)


def start(update, context):
    update.message.reply_text(
        "Hello. I'm statistic bot. \n"
        "I'll fix your data arterial pressure end save it. "
    )
    update.message.reply_text(
        "Enter your arterial pressure: "
    )

    return PRESSURE


def pressure(update, context):
    update.message.reply_text(
        'Fix, it \n'
        'Enter your next arterial pressure: '
    )

    return PRESSURE


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
            PRESSURE: [MessageHandler(Filters.text, pressure)]
        },
        fallbacks=[CommandHandler('end', end)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
