import logging
import random

import vk_api as vk
from environs import Env
from google.cloud import dialogflow
from telegram import Bot
from vk_api.longpoll import VkEventType, VkLongPoll

from bot import TelegramLogsHandler

logger = logging.getLogger('Logger')


def get_df_reply(project_id, session_id, texts, language_code):

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    for text in texts:
        text_input = dialogflow.TextInput(
            text=text,
            language_code=language_code
        )

        query_input = dialogflow.QueryInput(text=text_input)
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        if not response.query_result.intent.is_fallback:
            return response.query_result.fulfillment_text


def echo(event, vk_api, text):
    vk_api.messages.send(
        user_id=event.user_id,
        message=text,
        random_id=random.randint(1, 1000)
    )


def main():
    env = Env()
    env.read_env()
    project_id = env.str("PROJECT_ID")
    vk_token = env.str("VK_TOKEN")
    bot_token = env.str("TOKEN")
    chat_id = env.str("CHAT_ID")

    bot = Bot(bot_token)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(tg_bot=bot, chat_id=chat_id))

    while True:
        try:
            vk_session = vk.VkApi(token=vk_token)
            vk_api = vk_session.get_api()
            longpoll = VkLongPoll(vk_session)

            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    reply_text = get_df_reply(
                        project_id=project_id,
                        session_id=event.user_id,
                        texts=[event.text],
                        language_code="ru-RU")
                    if reply_text:
                        echo(event, vk_api, reply_text)
        except Exception as e:
            logger.error('Возникла ошибка:')
            logger.error(e, exc_info=True)
            logger.warning('Перезапускаю бот')
            continue


if __name__ == "__main__":
    main()
