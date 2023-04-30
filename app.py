import yaml
import asyncio
import telegram
import telegram.ext
from telegram.ext import Application
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database.database import Database

class App:
    config = None 


    @staticmethod
    def build_and_listen():
        with open("./cfg.yaml", "r") as stream:
            try:
                App.config = yaml.safe_load(stream)["app"]
            except yaml.YAMLError as exc:
                print(exc)

        Database.parse_config()
        Database.connect()

        builder = Application.builder()

        builder.token(str(App.config["token"]))
        application = builder.build()

        application.add_handler(telegram.ext.CommandHandler("form", App.form))
        application.add_handler(telegram.ext.CallbackQueryHandler(App.button))

        application.run_polling()


    @staticmethod
    async def start(
        update: telegram.Update, 
        context: ContextTypes.DEFAULT_TYPE 
    ) -> None:
         

    @staticmethod 
    async def form(
        update: telegram.Update, 
        context: ContextTypes.DEFAULT_TYPE 
    ) -> None:
        keyboard = [
            [
                InlineKeyboardButton("1", callback_data="1"),
                InlineKeyboardButton("2", callback_data="2"),
                InlineKeyboardButton("3", callback_data="3"),
                InlineKeyboardButton("4", callback_data="3"),
                InlineKeyboardButton("5", callback_data="3"),
                InlineKeyboardButton("6", callback_data="3"),
                InlineKeyboardButton("7", callback_data="3"),
                InlineKeyboardButton("8", callback_data="3"),
                InlineKeyboardButton("9", callback_data="3"),
                InlineKeyboardButton("10", callback_data="3")
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
                "Оцените свое эмоциональное состояние по десятибальной шкале:", 
                reply_markup=reply_markup
        )


    @staticmethod
    async def button(
        update: telegram.Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        await query.answer()

        await query.edit_message_text(text=f"Selected option: {query.data}")
