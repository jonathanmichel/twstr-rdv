import html
import json
import logging
import traceback

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot, BotCommand, Update
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

from para import Pilots, Locations, Flights, FlightEvents
import firebase_admin
from datetime import datetime
from firebase_admin import db, credentials

DEV_ID = 648038516

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
log = logging.getLogger()

async def send_to_dev(message, **kwargs):
    message = "🤖 DEBUG\n{}".format(message)
    # TODO Enable this
    #self.bot.send_message(chat_id=DEV_ID, text=message, parse_mode=ParseMode.HTML, **kwargs)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    await send_to_dev(message)

async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🪂 Click & fly", callback_data="3")],
        [
            InlineKeyboardButton("💾 Enregister un vol", callback_data="3"),
            InlineKeyboardButton("📜 Afficher tes vol", callback_data="/listflights"),
        ],
        [InlineKeyboardButton("🌍 Afficher les sites de vol", callback_data="/listlocations")],
        [
            InlineKeyboardButton("📟 Twist'Air rendez-vous", callback_data="/rendezvous"),
            InlineKeyboardButton("🌤️ Twist'Air bulletin météo", callback_data="/forecast"),
        ],

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Que veux-tu faires ?", reply_markup=reply_markup)

async def forecast_command_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    # forecast = self.status.get_saved_forecast()
    # context.bot.send_message(
    #     chat_id=chat_id, text=self.twstr.format_meteo(forecast), 
    #     parse_mode=ParseMode.HTML, disable_web_page_preview=True
    # )

async def rendezvous_command_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    # rendezvous = self.status.get_saved_rendezvous()
    # context.bot.send_message(
    #     chat_id=chat_id, text=self.twstr.format_rendezvous(rendezvous),
    #     parse_mode=ParseMode.HTML, disable_web_page_preview=True
    # )


async def listFlights_command_handler(update: Update, context: CallbackContext):
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

    await context.bot.send_message(
        chat_id=chat_id, text=response,
        parse_mode=ParseMode.HTML, disable_web_page_preview=False
    )


async def listLocations_command_handler(update: Update, context: CallbackContext):
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


    await context.bot.send_message(
        chat_id=chat_id, text=response,
        parse_mode=ParseMode.HTML, disable_web_page_preview=False
    )

async def button(update: Update, context: None) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # print(query)
    # print(query.data)

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"{query.data}")

    if query.data == "/listflights":
        await listFlights_command_handler(update, context)
    elif query.data == "/listlocations":
        await listLocations_command_handler(update, context)


if __name__ == "__main__" :
    # Get pushover API keys
    with open(r'credentials.json') as file:
        credentials_file = json.load(file)

    application = Application.builder().token(credentials_file["telegram_token"]).build()
    bot = application.bot


    # Add error handler
    application.add_error_handler(error_handler)
    
    # Available commands
    # ("command", handler, "description")
    commands = [
        ("start", start_command_handler, "S'enregistrer en tant que pilote"),
        ("rendezvous", rendezvous_command_handler, "Afficher le dernier rendez-vous"),
        ("forecast", forecast_command_handler, "Afficher la dernière météo d'Antoine"),
        ("listflights", listFlights_command_handler, "Liste les vols"),
        ("listlocations", listLocations_command_handler, "Lister les lieux de vol"),
    ]

    # Generate help commands list and add commands handlers
    my_commands = []
    for c in commands:
        my_commands.append(BotCommand(c[0], c[2]))
        application.add_handler(CommandHandler(c[0], c[1]))

    bot.set_my_commands(my_commands)

    application.add_handler(CallbackQueryHandler(button))

    firebase_db_url = "https://twstr-bot-default-rtdb.europe-west1.firebasedatabase.app/"
    firebase_credentials = "twstr-bot-firebase-adminsdk.key.json"
    
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_db_url
        })
    
    print("Bot created")

    application.run_polling()
    print("Polling...")
