# build-in modules
import asyncio
import datetime
import logging

# third-party
import yaml
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    Defaults,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters
)

# local
from database.database import Database


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# default timezone UTC+3
TZONE = datetime.timezone(datetime.timedelta(hours=3))

NEW_NOTTY_MSG = "Ежедневное уведомление в {}:{} включено"
NOTTY_EXIST_MSG = "У вас уже включено уведомление в это время"

class App:
    config = None 
    _db: Database = None
    _application: Application
    
    @staticmethod
    def build_and_listen():
        with open("./cfg.yaml", "r") as stream:
            try:
                App.config = yaml.safe_load(stream)["app"]
            except yaml.YAMLError as exc:
                print(exc)

        App._db = Database()

        defaults = Defaults(tzinfo=TZONE)
        App._application = (
            Application.builder()
            .token(str(App.config["token"]))
            .defaults(defaults)
            .build()
        )

        App.load_noty_jobs()

        noty_set_conv = ConversationHandler(
            entry_points=[CommandHandler("time", App.time)],
            states={
                1: [MessageHandler(filters.Regex(r"^(1\d:\d{2}|2[0-3]:\d{2})\Z"), App.new_noty)]
            },
            fallbacks=[CommandHandler("cancel", App.cancel)]
        )

        App._application.add_handler(noty_set_conv)

        App._application.add_handler(CommandHandler("form", App.form))
        App._application.add_handler(CommandHandler("start", App.start))
        App._application.add_handler(CommandHandler("jobs", App.debug_show_jobs))
        # application.add_handler(CommandHandler(App.button))

        App._application.run_polling()


    @staticmethod
    async def start(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE 
    ) -> None:
        id_chat = update.effective_chat.id

        App._db.insert_if_not_exist(id_chat)

        await update.message.reply_text(
            "Привет, я помогу тебе отслеживать твое эмоциональное состояние!"
        )


    @staticmethod
    async def time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.send_message(update.effective_chat.id,
                                 "Напиши время уведомления в формате ЧЧ:ММ")
        return 1
    
    @staticmethod
    async def debug_show_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.info(App._application.job_queue.jobs)


    @staticmethod
    async def new_noty(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
        chat_id = update.effective_chat.id
        hours, minutes = update.effective_message.text.split(":")
        hours, minutes = int(hours), int(minutes)
        if App._db.add_notification(chat_id, hours, minutes):
            noty_time = datetime.time(hour=hours, minute=minutes)
            App.add_daily_noty(chat_id, noty_time)
            await context.bot.send_message(chat_id, 
                                           NEW_NOTTY_MSG.format(hours, minutes))
        else:
            await context.bot.send_message(chat_id, 
                                           NOTTY_EXIST_MSG)
        return ConversationHandler.END
    
    @staticmethod
    def add_daily_noty(chat_id, noty_time):
        App._application.job_queue.run_daily(App.send_mood_form, 
                                             time=noty_time, 
                                             chat_id=chat_id)
    
    @staticmethod
    def load_noty_jobs():
        notifications = App._db.get_notifications()
        for n in notifications:
            logging.info(n)
        
            App.add_daily_noty(chat_id=n[0], 
                                     noty_time=n[1])
        

    @staticmethod
    async def send_mood_form(context: ContextTypes.DEFAULT_TYPE):
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

        App._db.form_answer(id_chat, query.data)

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
    Database.parse_config("./database/cfg.yaml")
    App.build_and_listen()