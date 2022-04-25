import json
import logging
from pprint import pprint
from time import sleep

from pushover import Pushover
from twstr_rdv import TwstrRdv
from status import Status
from telegram_bot import TelegramBot


if __name__ == "__main__" :
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    # Get pushover API keys
    with open(r'credentials.json') as file:
        credentials = json.load(file)

    telegram = TelegramBot(credentials["telegram_token"])

    telegram.start_polling()

    exit()

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


