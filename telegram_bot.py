from ast import arg
from telegram.bot import Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram.update import Update


class TelegramBot:
    def __init__(self, token):
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.bot = Bot(token=token)

        self.subscribers = set()

        start_handler = CommandHandler("start", 
            lambda bot, update: self.start_command_handler(bot, update)
        )

        self.dispatcher.add_handler(start_handler)

    def start_polling(self):
        self.updater.start_polling()

    def broadcast_message(self, message):
        for sub in self.subscribers:
            self.bot.send_message(chat_id=sub, text=message)

    def start_command_handler(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id

        context.bot.send_message(chat_id=chat_id, text="Hey c'est Twist'Hervé ! Bon vol 🪂")
        self.subscribers.add(chat_id)
