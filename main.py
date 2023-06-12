import json
import logging
from time import sleep
import asyncio

from twstr import Status
from twstr import TwstrParser
from services import Pushover
from services import TwstrTelegramBot
from services import Healthchecks

async def main():
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

    await telegram.create()

    await telegram.start_polling()

    while True:
        continue

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
                formated = twstr.format_rendezvous(current_rendezvous, True)
                if formated is None:
                    telegram.send_to_dev("Rendez-vous mis à jour mais pour une date incorrecte")
                    telegram.send_to_dev(current_rendezvous)
                else:
                    telegram.broadcast_message(
                        formated, disable_web_page_preview=True
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
                if formated is None:
                    telegram.send_to_dev("Nouvelle météo publiée mais pour une date incorrecte")
                else:
                    telegram.broadcast_message(
                        formated, disable_web_page_preview=True
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

        healthchecks.success()

        # Try next time
        sleep(15 * 60) # 15 minutes

if __name__ == "__main__" :
    asyncio.run(main())