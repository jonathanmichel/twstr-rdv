import json
import logging
from pprint import pprint
from time import sleep

from telegram.bot import Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
from telegram.update import Update

from pushover import Pushover
from twstr_rdv import TwstrRdv
from status import Status

users_list = set()
groups_list = set()

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Hey c'est Twist'Hervé ! Bon vol 🪂")
    if chat_id > 0:
        users_list.add(chat_id)
        context.bot.send_message(chat_id=chat_id, text=f"Utilisateur {chat_id} ajouté à la liste de diffusion")
    else:
        groups_list.add(chat_id)
        context.bot.send_message(chat_id=chat_id, text=f"Groupe {chat_id} ajouté à la liste de diffusion")

def debug(update: Update, context: CallbackContext):
    debug = {
        "version": 0.1,
        "chat_id": update.effective_chat.id
    }
    context.bot.send_message(chat_id=update.effective_chat.id, text=debug)

def broadcast(update: Update, context: CallbackContext):
    broadcast_message("Salut")

def broadcast_message(message):
    for u in users_list:
        bot.send_message(chat_id=u, text=message)

    for g in groups_list:
        bot.send_message(chat_id=g, text=message)

if __name__ == "__main__" :
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    # Get pushover API keys
    with open(r'credentials.json') as file:
        credentials = json.load(file)

    updater = Updater(credentials["telegram_token"], use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    debug_handler = CommandHandler('debug', debug)
    dispatcher.add_handler(debug_handler)

    broadcast_handler = CommandHandler('broadcast', broadcast)
    dispatcher.add_handler(broadcast_handler)

    bot = Bot(token=credentials["telegram_token"])

    updater.start_polling()

    while True:
        sleep(15)
        url = "https://twistair.ch/ecole-parapente/62-rendez-vous"

        notif = Pushover(
            token=credentials["pushover_token"],
            user=credentials["pushover_user"]
        )

        twstr = TwstrRdv(url)

        status = Status("status.json")

        # Get last saved messages locally
        saved_message = status.get_saved_message()

        # Get last message on the website
        current_message = twstr.get_last_message()

        # If we were not able to get last message on the site2
        if current_message == None:
            continue
            # notif.send_message(
            #     title="Impossible de récupérer le rendez-vous",
            #     message="Format de page inconnu",
            #     url=url,
            #     url_title="Voir la page rendez-vous"
            # )

        # Compare theme
        if current_message != saved_message:
            # If different ...
            # ... send notification
            broadcast_message(f"Nouveau rendez-vous\n{current_message}")
            # ... update local save
            pprint(status.update_message(current_message))
        else:
            # If no new message ...
            # ... send debug notif
            # notif.send_message(message="Pas de nouveau rendez-vous", url=url, url_title="Voir le site")
            # ... update last check time locally
            pprint(status.update_check())


