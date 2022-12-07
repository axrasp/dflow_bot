import logging

from environs import Env
from telegram import Bot, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

from dflow_scripts import TelegramLogsHandler, get_df_reply

logger = logging.getLogger('Logger')


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr"Hi {user.mention_markdown_v2()}\! Давай выкладывай",
    )


def send_df_reply(update: Update, context: CallbackContext) -> None:
    fallback, reply_text = get_df_reply(
        session_id=update.effective_user.id,
        project_id=context.bot_data["project_id"],
        text=update.message.text, language_code="ru-RU")
    update.message.reply_text(reply_text)


def main() -> None:
    env = Env()
    env.read_env()
    bot_token = env.str("TG_TOKEN")
    tg_chat_id = env.str("TG_CHAT_ID")
    project_id = env.str("PROJECT_ID")
    updater = Updater(bot_token)
    bot = Bot(bot_token)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(tg_bot=bot, chat_id=tg_chat_id))
    while True:
        try:
            dispatcher = updater.dispatcher
            dispatcher.bot_data["project_id"] = project_id

            dispatcher.add_handler(CommandHandler("start", start))
            dispatcher.add_handler(MessageHandler(
                Filters.text & ~Filters.command, send_df_reply))
            updater.start_polling()
            updater.idle()

        except Exception as e:
            logger.error('Возникла ошибка:')
            logger.error(e, exc_info=True)
            logger.warning('Перезапускаю бот')
            continue


if __name__ == "__main__":
    main()
