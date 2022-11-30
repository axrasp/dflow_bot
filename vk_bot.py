import logging
import random

import vk_api as vk
from environs import Env
from telegram import Bot
from vk_api.longpoll import VkEventType, VkLongPoll

from dflow_scripts import TelegramLogsHandler, get_df_reply

logger = logging.getLogger('Logger')


def send_vk_message(event, vk_api, text):
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
    bot_token = env.str("TG_TOKEN")
    tg_chat_id = env.str("TG_CHAT_ID")

    bot = Bot(bot_token)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(tg_bot=bot, chat_id=tg_chat_id))

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
                        text=[event.text],
                        language_code="ru-RU")
                    if reply_text:
                        send_vk_message(event, vk_api, reply_text)
        except Exception as e:
            print(e)
            logger.error('в ВК боте возникла ошибка: ')
            logger.error(e, exc_info=True)
            logger.warning('Перезапускаю бот')
            continue


if __name__ == "__main__":
    main()
