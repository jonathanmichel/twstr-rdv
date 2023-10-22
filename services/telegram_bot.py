import html
import json
import logging
import traceback

from telegram.bot import Bot, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.update import Update
from telegram.parsemode import ParseMode
from telegram import error

from twstr import Status
from twstr import TwstrParser
from twstr import SubscribersHandler

from para import Pilots, Locations, Flights, FlightEvents
import firebase_admin
from datetime import datetime
from firebase_admin import db, credentials

log = logging.getLogger()


class TwstrTelegramBot:
    def __init__(self, token, status: Status, twstr: TwstrParser, dev_id=""):
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.error_handlers
        self.status = status
        self.twstr = twstr
        self.dev_id = dev_id

        self.bot = Bot(token=token)

        self.subscribers = SubscribersHandler([dev_id])

        # Add "Les parapenteur" group in diffusion list
        # self.subscribers.add(-654440852)
	# Add Loïc F. in diffusion list
        self.subscribers.add(230034740)

        # Add error handler
        self.dispatcher.add_error_handler(self.error_handler)

        # Available commands
        # ("command", handler, "description")
        commands = [
            ("start", self.start_command_handler, "S'enregistrer en tant que pilote"),
            ("rendezvous", self.rendezvous_command_handler, "Afficher le dernier rendez-vous"),
            ("forecast", self.forecast_command_handler, "Afficher la dernière météo d'Antoine"),
            ("listflights", self.listFlights_command_handler, "Liste les vols"),
            ("listlocations", self.listLocations_command_handler, "Lister les lieux de vol"),
        ]

        # Generate help commands list and add commands handlers
        my_commands = []
        for c in commands:
            my_commands.append(BotCommand(c[0], c[2]))
            self.dispatcher.add_handler(CommandHandler(c[0], c[1]))

        self.bot.set_my_commands(my_commands)

        firebase_db_url = "https://twstr-bot-default-rtdb.europe-west1.firebasedatabase.app/"
        firebase_credentials = "twstr-bot-firebase-adminsdk.key.json"
        
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred, {
            'databaseURL': firebase_db_url
            })

    def start_polling(self):
        self.updater.start_polling()

    def broadcast_message(self, message, **kwargs):
        for sub in self.subscribers.get():
            try:
                self.bot.send_message(chat_id=sub, text=message, parse_mode=ParseMode.HTML, **kwargs)
            except error.Unauthorized as e:
                log.warning(f"chat_id: {sub} - {e}")

    def send_to_dev(self, message, **kwargs):
        message = "🤖 DEBUG\n{}".format(message)
        self.bot.send_message(chat_id=self.dev_id, text=message, parse_mode=ParseMode.HTML, **kwargs)

    def error_handler(self, update: object, context: CallbackContext) -> None:
        """Log the error and send a telegram message to notify the developer."""
        # Log the error before we do anything else, so we can see it even if something breaks.
        log.error(msg="Exception while handling an update:", exc_info=context.error)

        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = ''.join(tb_list)

        # Build the message with some markup and additional information about what happened.
        # You might need to add some logic to deal with messages longer than the 4096 character limit.
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f'An exception was raised while handling an update\n'
            f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
            '</pre>\n\n'
            f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
            f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
            f'<pre>{html.escape(tb_string)}</pre>'
        )

        self.send_to_dev(message)

    def start_command_handler(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id


        if chat_id > 0:
            context.bot.send_message(chat_id=chat_id, text=f"Hey {update.effective_chat.first_name}, c'est Twist'Hervé! Bon vol 🪂")
            self.send_to_dev(f"User {update.effective_chat.first_name} (@{update.effective_chat.username}, #{update.effective_chat.id}) added to diffusion list")
        else:
            context.bot.send_message(chat_id=chat_id, text=f"Hey c'est Twist'Hervé! Merci {update.effective_user.first_name} de m'avoir ajouté au groupe. Bon vol 🪂")
            self.send_to_dev(f"Group {update.effective_chat.title} #{update.effective_chat.id} added to diffusion list by {update.effective_user.first_name} (@{update.effective_user.username}, #{update.effective_user.id})")

        self.subscribers.add(chat_id)

    def forecast_command_handler(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id

        forecast = self.status.get_saved_forecast()
        context.bot.send_message(
            chat_id=chat_id, text=self.twstr.format_meteo(forecast), 
            parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )

    def rendezvous_command_handler(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id

        rendezvous = self.status.get_saved_rendezvous()
        context.bot.send_message(
            chat_id=chat_id, text=self.twstr.format_rendezvous(rendezvous),
            parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )


    def listFlights_command_handler(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        response = ""

        flights_events = Flights.getAllEventsForPilot(chat_id)

        for event in flights_events:
            loc = Locations.get(event["locationId"])

            type = "❓"
            if loc['type'] == Locations.LocationType.TAKEOFF.value:
                type = "🛫"
            elif loc['type'] == Locations.LocationType.LANDING.value:
                type = "🛬"
            
            dt = datetime.fromtimestamp(event["timestamp"])

            response += f"{type} at {loc['name']} on {dt} - {event['notes']}\n"

        context.bot.send_message(
            chat_id=chat_id, text=response,
            parse_mode=ParseMode.HTML, disable_web_page_preview=False
        )

    def listLocations_command_handler(self, update: Update, context: CallbackContext):
        response = ""
        chat_id = update.effective_chat.id

        locations_list = Locations.getAll()
        for locations_id in  locations_list:
            loc = locations_list[locations_id]
            
            googlemaps_url = f"https://www.google.com/maps/search/{loc['latitude']}, {loc['longitude']}"
            location_link = f"<a href='{googlemaps_url}'>Map</a>"

            type = "❓"
            if loc['type'] == Locations.LocationType.TAKEOFF.value:
                type = "🛫"
            elif loc['type'] == Locations.LocationType.LANDING.value:
                type = "🛬"

            response += f"{type} <b>{loc['name']}</b> - <i>{loc['description']}</i>  {location_link}\n"


        context.bot.send_message(
            chat_id=chat_id, text=response,
            parse_mode=ParseMode.HTML, disable_web_page_preview=False
        )

