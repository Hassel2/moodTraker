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
        application.add_handler(telegram.ext.CommandHandler("start", App.start))
        application.add_handler(telegram.ext.CallbackQueryHandler(App.button))

        application.run_polling()


    @staticmethod
    async def start(
        update: telegram.Update, 
        context: ContextTypes.DEFAULT_TYPE 
    ) -> None:
        id_chat = update.effective_chat.id

        Database.insert_if_not_exist(id_chat)
        # Database.new_chat(
        #     id_chat=id_chat,
        #     gender='male',
        #     age=31,
        # )0

        await update.message.reply_text(
            "Привет, я помогу тебе отслеживать твое эмоциональное состояние!"
        )

    @staticmethod 
    async def form(
        update: telegram.Update, 
        context: ContextTypes.DEFAULT_TYPE 
    ) -> None:
        keyboard = [
            [
                InlineKeyboardButton("😢", callback_data="1"),
                InlineKeyboardButton("🙁", callback_data="2"),
                InlineKeyboardButton("😐", callback_data="3"),
                InlineKeyboardButton("🙂", callback_data="4"),
                InlineKeyboardButton("😀", callback_data="5"),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
                "Оцените свое эмоциональное состояние по пятибальной шкале:", 
                reply_markup=reply_markup
        )


    @staticmethod
    async def button(
        update: telegram.Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query
        id_chat = update.effective_chat.id

        Database.form_answer(id_chat, query.data)

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        await query.answer(
            text=["😢", "🙁", "😐", "🙂", "😀"][int(query.data) - 1]
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=["😢", "🙁", "😐", "🙂", "😀"][int(query.data) - 1]
        )

        await query.edit_message_text(text="Спасибо, ваш ответ записан!")


if __name__ == "__main__":
    App.build_and_listen()