# build-in modules
import asyncio
import datetime

# third-party
import yaml
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application, 
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters
)

# local
from database.database import Database


class App:
    config = None 
    database: Database = None
    
    @staticmethod
    def build_and_listen():
        with open("./cfg.yaml", "r") as stream:
            try:
                App.config = yaml.safe_load(stream)["app"]
            except yaml.YAMLError as exc:
                print(exc)

        App.database = Database()

        builder = Application.builder()

        builder.token(str(App.config["token"]))
        application = builder.build()

        noty_set_conv = ConversationHandler(
            entry_points=[CommandHandler("time", App.time)],
            states={
                1: [MessageHandler(filters.Regex(r"^(1\d:\d{2}|2[0-3]:\d{2})\Z"), App.new_notty)]
            },
            fallbacks=[CommandHandler("cancel", App.cancel)]
        )

        application.add_handler(noty_set_conv)

        application.add_handler(CommandHandler("form", App.form))
        application.add_handler(CommandHandler("start", App.start))
        # application.add_handler(CommandHandler(App.button))

        application.run_polling()


    @staticmethod
    async def start(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE 
    ) -> None:
        id_chat = update.effective_chat.id

        Database.insert_if_not_exist(id_chat)

        await update.message.reply_text(
            "Привет, я помогу тебе отслеживать твое эмоциональное состояние!"
        )


    @staticmethod
    async def time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.send_message(update.effective_chat.id,
                                 "Напиши время уведомления в формате ЧЧ:ММ")
        return 1


    @staticmethod
    async def new_notty(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
        time = update.effective_message.text
        chat_id = update.effective_chat.id
        if Database.add_notification(chat_id, time):
            await App.add_daily_notty(chat_id, time, context)
            await context.bot.send_message(chat_id, f"Уведолмение в {time} каждый день добавлено.")
        else:
            await context.bot.send_message(chat_id, f"Произошла ошибка во время добавления уведомления!")
        return ConversationHandler.END
    
    @staticmethod
    async def add_daily_notty(chat_id, time, context: ContextTypes.DEFAULT_TYPE):
        hours, minutes = time.split(":")
        task_time = datetime.time(hour=int(hours), minute=int(minutes))
        context.job_queue.run_daily(App.send_test_message, time=task_time, chat_id=chat_id)
        

    @staticmethod
    async def send_test_message(context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(context.job.chat_id, 
                                       text=f"УВЕДОМЛЕНИЕ!!")
        
    
    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE)->int:
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id, "Действие отменено")

    @staticmethod 
    async def form(
        update: Update, 
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
        update: Update, 
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