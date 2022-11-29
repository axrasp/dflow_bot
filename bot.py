import logging

from environs import Env
from google.cloud import dialogflow
from telegram import Update, Bot
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)


logger = logging.getLogger('Logger')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def detect_intent_texts(project_id, session_id, texts, language_code):

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print("Session path: {}\n".format(session))

    for text in texts:
        text_input = dialogflow.TextInput(
            text=text,
            language_code=language_code
        )

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        return response.query_result.fulfillment_text
    

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    env = Env()
    env.read_env()
    context.user_data["project_id"] = env.str("PROJECT_ID")
    context.user_data["session_id"] = update.effective_user.id
    update.message.reply_markdown_v2(
        fr"Hi {user.mention_markdown_v2()}\! Давай выкладывай",
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(detect_intent_texts(
        project_id=context.user_data["project_id"],
        session_id=context.user_data["session_id"],
        texts=[update.message.text], language_code="ru-RU"))


def main() -> None:
    env = Env()
    env.read_env()
    bot_token = env.str("TOKEN")
    chat_id = env.str("CHAT_ID")
    updater = Updater(bot_token)
    bot = Bot(bot_token)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(tg_bot=bot, chat_id=chat_id))
    while True:
        try:
            # Get the dispatcher to register handlers
            dispatcher = updater.dispatcher

            # on different commands - answer in Telegram
            dispatcher.add_handler(CommandHandler("start", start))
            dispatcher.add_handler(CommandHandler("help", help_command))

            # on non command i.e message - echo the message on Telegram
            dispatcher.add_handler(MessageHandler(
                Filters.text & ~Filters.command, echo))
            # Start the Bot
            updater.start_polling()
            # Run the bot until you press Ctrl-C or the process receives SIGINT,
            # SIGTERM or SIGABRT. This should be used most of the time, since
            # start_polling() is non-blocking and will stop the bot gracefully.
            updater.idle()

        except Exception as e:
            logger.error('Возникла ошибка:')
            logger.error(e, exc_info=True)
            logger.warning('Перезапускаю бот')
            continue


if __name__ == "__main__":
    main()
