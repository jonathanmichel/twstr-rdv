import logging
from telegram.bot import Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.update import Update
from telegram.parsemode import ParseMode
from telegram import error

from subscribers_handler import SubscribersHandler


log = logging.getLogger()


class TelegramBot:
    def __init__(self, token, subscribers=[]):
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.bot = Bot(token=token)

        self.subscribers = SubscribersHandler(subscribers)

        self.dispatcher.add_handler(CommandHandler("start", 
            lambda bot, update: self.start_command_handler(bot, update)
        ))

    def start_polling(self):
        self.updater.start_polling()

    def broadcast_message(self, message):
        for sub in self.subscribers.get():
            try:
                self.bot.send_message(chat_id=sub, text=message, parse_mode=ParseMode.HTML)
            except error.Unauthorized as e:
                log.warning(f"chat_id: {sub} - {e}")


    def start_command_handler(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id

        context.bot.send_message(chat_id=chat_id, text="Hey c'est Twist'Hervé ! Bon vol 🪂")
        self.subscribers.add(chat_id)
