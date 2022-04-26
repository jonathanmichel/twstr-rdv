import json
import logging
from time import sleep

from status import Status
from pushover import Pushover
from twstr_parser import TwstrParser
from telegram_bot import TwstrTelegramBot
from healthchecks import Healthchecks

if __name__ == "__main__" :
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
    log = logging.getLogger()

    # Get pushover API keys
    with open(r'credentials.json') as file:
        credentials = json.load(file)

    healthchecks = Healthchecks(credentials["healthchecks_uuid"])
    
    pushover = Pushover(
        token=credentials["pushover_token"],
        user=credentials["pushover_user"]
    )

    twstr = TwstrParser(
        base_url="https://twistair.ch/ecole-parapente/", 
        path_rendez_vous="62-rendez-vous",
        path_meteo="55-meteo-de-tonio-a-vercorin"
    )

    status = Status("status.json")

    telegram = TwstrTelegramBot(
        credentials["telegram_token"], 
        status,
        twstr,
        credentials["telegram_dev_ids"]
    )

    telegram.start_polling()

    while True:
        healthchecks.start()

        # Get last saved messages locally
        saved_rendezvous = status.get_saved_rendezvous()

        # Get last rendezvous on the website
        current_rendezvous = twstr.get_last_rendez_vous()

        # If we were not able to get last rendezvous on the site2
        if current_rendezvous != None:
            # Compare theme
            if current_rendezvous != saved_rendezvous:
                # If different ...
                # ... send notification
                telegram.broadcast_message(
                    twstr.format_rendezvous(current_rendezvous), disable_web_page_preview=True
                )
                # ... update local save
                status.update_rendezvous(current_rendezvous)
        else:
            log.error("Unable to get rendez-vous")
            pushover.send_message(
                title="Impossible de récupérer le rendez-vous",
                message="Format de page inconnu"
            )

        # Get last saved messages locally
        saved_forecast = status.get_saved_forecast()["section"]

        # Get last weather forecast on the website
        current_forecast = twstr.get_forecast(0)

        # If we were not able to get last message on the site2
        if current_forecast != None:
            # Compare theme
            if current_forecast["section"] != saved_forecast:
                # If different ...
                # ... send notification
                telegram.broadcast_message(
                    twstr.format_meteo(current_forecast), disable_web_page_preview=True
                )
                # ... update local save
                status.update_forecast(current_forecast)
        else:
            log.error("Unable to get forecast")
            pushover.send_message(
                title="Impossible de récupérer la météo de Tonio",
                message="Format de page inconnu",
            )

        # Update check datetime
        status.update_check()
        log.info("Check done")

        healthchecks.success()

        # Try next time
        sleep(5) # 60 * 60)
