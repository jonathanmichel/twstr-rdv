import html
import json
import logging
import traceback

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Bot,
    BotCommand,
    Update
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
    PicklePersistence,
)

from telegram.constants import ParseMode

from para import Pilots, Locations, Flights, FlightEvents
import firebase_admin
from datetime import datetime
from firebase_admin import db, credentials

DEV_ID = 648038516

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
log = logging.getLogger()

MAIN_MENU, CLICK_AND_FLY, REGISTER_FLIGHT, DISPLAY_FLIGHTS, DISPLAY_LOCATIONS = map(chr, range(5))

BACK = str(chr(5))

# Shortcut for ConversationHandler.END
END = ConversationHandler.END

async def send_to_dev(message, **kwargs):
    message = "🤖 DEBUG\n{}".format(message)
    # TODO Enable this
    # self.bot.send_message(chat_id=DEV_ID, text=message, parse_mode=ParseMode.HTML, **kwargs)

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [ InlineKeyboardButton("🪂 Click & fly", callback_data=str(CLICK_AND_FLY)) ],
        [
            InlineKeyboardButton("💾 Enregister un vol", callback_data=str(REGISTER_FLIGHT)),
            InlineKeyboardButton("📜 Afficher tes vol", callback_data=str(DISPLAY_FLIGHTS)),
        ],
        [ InlineKeyboardButton("🌍 Afficher les sites de vol", callback_data=str(DISPLAY_LOCATIONS)) ],
        [
            InlineKeyboardButton("📟 Twist'Air rendez-vous", callback_data="/rendezvous"),
            InlineKeyboardButton("🌤️ Twist'Air bulletin météo", callback_data="/forecast"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    text = "Que veux-tu faire ?"
    if context.user_data:
        # Back to start menus - No need to send a new message
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        # New conversation - Start with a new message
        await update.message.reply_text("Salut, je suis Twist'Hervé, le bot de Twist'Air !")
        await update.message.reply_text(text=text, reply_markup=keyboard)
        # Usefull only here but has to be improved
        context.user_data["identied"] = True
    
    # await update.callback_query.answer()
    # await update.message.reply_text("Que veux-tu faires ?", reply_markup=reply_markup)

    return MAIN_MENU

async def clickAndFly(update: Update, context: CallbackContext):
    user_data = context.user_data
    chat_id = update.effective_chat.id

    text = "Please send me your location ...\n"

    buttons = [
        [InlineKeyboardButton(text="Envoyer ma position", callback_data=str(BACK))],
        [InlineKeyboardButton(text="Annuler", callback_data=str(BACK))],
        ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()

    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

    return CLICK_AND_FLY

async def getLocation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location

    await update.message.reply_text(
        f"Location get: {user_location.latitude} {user_location.longitude}"
    )

    return MAIN_MENU  

    # await context.bot.send_message(
    #     chat_id=chat_id, text=response,
    #     parse_mode=ParseMode.HTML, disable_web_page_preview=False
    # )

async def listFlights(update: Update, context: CallbackContext):
    user_data = context.user_data
    chat_id = update.effective_chat.id

    flights_events = Flights.getAllEventsForPilot(chat_id)

    text = "<b><u>Liste des vols</u></b>\n"
    for event in flights_events:
        loc = Locations.get(event["locationId"])

        type = "❓"
        if loc['type'] == Locations.LocationType.TAKEOFF.value:
            type = "🛫"
        elif loc['type'] == Locations.LocationType.LANDING.value:
            type = "🛬"
        
        dt = datetime.fromtimestamp(event["timestamp"])

        text += f"{type} at {loc['name']} on {dt} - {event['notes']}\n"

    buttons = [[InlineKeyboardButton(text="<< Retour", callback_data=str(BACK))]]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()

    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

    return DISPLAY_FLIGHTS

async def listLocations(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    locations_list = Locations.getAll()
    
    text = "<b>Liste des lieux de vol</b>\n"
    for locations_id in  locations_list:
        loc = locations_list[locations_id]
        
        googlemaps_url = f"https://www.google.com/maps/search/{loc['latitude']}, {loc['longitude']}"
        location_link = f"<a href='{googlemaps_url}'>Map</a>"

        type = "❓"
        if loc['type'] == Locations.LocationType.TAKEOFF.value:
            type = "🛫"
        elif loc['type'] == Locations.LocationType.LANDING.value:
            type = "🛬"

        text += f"{type} <b>{loc['name']}</b> - <i>{loc['description']}</i>  {location_link}\n"

    buttons = [[InlineKeyboardButton(text="<< Retour", callback_data=str(BACK))]]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()

    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

    return DISPLAY_LOCATIONS

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

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    await update.message.reply_text("Okay, bye.")

    return END

async def return_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation from InlineKeyboardButton."""
    await update.callback_query.answer()

    await start(update, context)

    return MAIN_MENU

if __name__ == "__main__" :
    with open(r'credentials.json') as file:
        credentials_file = json.load(file)

    persistence = PicklePersistence(filepath="TwistHerveBotPersistence.pickle")


    application = Application.builder().token(credentials_file["telegram_token"]).build() # .persistence(persistence)
    bot = application.bot

    # Add error handler
    # application.add_error_handler(error_handler)
    
    # # Available commands
    # # ("command", handler, "description")
    # commands = [
    #     ("start", start, "S'enregistrer en tant que pilote"),
    #     ("rendezvous", rendezvous_command_handler, "Afficher le dernier rendez-vous"),
    #     ("forecast", forecast_command_handler, "Afficher la dernière météo d'Antoine"),
    #     ("listflights", listFlights, "Liste les vols"),
    #     ("listlocations", listLocations, "Lister les lieux de vol"),
    # ]

    # # Generate help commands list and add commands handlers
    # my_commands = []
    # for c in commands:
    #     my_commands.append(BotCommand(c[0], c[2]))
    #     application.add_handler(CommandHandler(c[0], c[1]))
    # bot.set_my_commands(my_commands)


    conv_handler = ConversationHandler(
        entry_points = [ CommandHandler("start", start) ],
        states = {
            MAIN_MENU: [
                # CLICK_AND_FLY, REGISTER_FLIGHT, DISPLAY_FLIGHTS, DISPLAY_LOCATIONS
                CallbackQueryHandler(listFlights, pattern="^" + str(DISPLAY_FLIGHTS) + "$"),
                CallbackQueryHandler(listLocations, pattern="^" + str(DISPLAY_LOCATIONS) + "$"),
                CallbackQueryHandler(clickAndFly, pattern="^" + str(CLICK_AND_FLY) + "$"),
                ],
            DISPLAY_FLIGHTS: [
                CallbackQueryHandler(return_to_main, pattern="^" + str(BACK) + "$")
                ],
            DISPLAY_LOCATIONS: [
                CallbackQueryHandler(return_to_main, pattern="^" + str(BACK) + "$")
                ],
            CLICK_AND_FLY: [
                MessageHandler(filters.LOCATION, getLocation),
                CallbackQueryHandler(return_to_main, pattern="^" + str(BACK) + "$")
            ],            # DESCRIBING_SELF: [description_conv],
            # STOPPING: [CommandHandler("start", start)],
        },
        fallbacks = [ CommandHandler("stop", stop) ],
    )

    application.add_handler(conv_handler)

    print("Bot created")

    firebase_db_url = "https://twstr-bot-default-rtdb.europe-west1.firebasedatabase.app/"
    firebase_credentials = "twstr-bot-firebase-adminsdk.key.json"
    
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_db_url
        })
    
    print("Firebase connection established")

    print("Polling ...")
    application.run_polling()
