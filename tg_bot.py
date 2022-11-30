import logging

from environs import Env
from google.cloud import dialogflow
from telegram import Update, Bot
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)
from dflow_scripts import TelegramLogsHandler


logger = logging.getLogger('Logger')


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


def send_df_reply(update: Update, context: CallbackContext) -> None:
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

            # on non command i.e message - echo the message on Telegram
            dispatcher.add_handler(MessageHandler(
                Filters.text & ~Filters.command, send_df_reply))
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
