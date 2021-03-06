import json
import logging.config
import os
import random

import redis
import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from db_questions import check_answer
from log_config import LOGGING_CONFIG, TelegramLogsHandler

logger = logging.getLogger(__file__)


def handle_new_question_request(event, vk_api, keyboard, questions, redis_db):
    question, answer = random.choice(questions).values()
    redis_db.set(event.user_id, answer)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id(),
    )


def handle_solution_attempt(event, vk_api, keyboard, redis_db):
    answer = redis_db.get(event.user_id)
    attempt = event.text
    if check_answer(answer, attempt):
        text = (
            f'✅ Правильно! Поздравляю!\n'
            f'Для следующего вопроса нажми «Новый вопрос»'
        )
    else:
        text = '🚫 Неправильно… Попробуешь ещё раз?'
    vk_api.messages.send(
        user_id=event.user_id,
        message=text,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id(),
    )


def give_up(event, vk_api, keyboard, redis_db):
    answer = redis_db.get(event.user_id)
    text = (
        f'Привильный ответ - {answer}\n'
        f'Для следующего вопроса нажми «Новый вопрос»'
    )
    vk_api.messages.send(
        user_id=event.user_id,
        message=text,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id(),
    )


def main():
    vk_token = os.getenv('VK_TOKEN')
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    redis_password = os.getenv('REDIS_PASSWORD')

    logging.config.dictConfig(LOGGING_CONFIG)
    logger.addHandler(TelegramLogsHandler(telegram_token, chat_id))

    with open('questions_base.json', 'r', encoding='utf-8') as file:
        questions = json.load(file)
    redis_db = redis.StrictRedis(
        host=redis_host,
        port=redis_port,
        db=0,
        password=redis_password,
        charset="utf-8",
        decode_responses=True
    )

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    logger.info('The frode VkBot is running')

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Сдаться':
                give_up(event, vk_api, keyboard, redis_db)
            elif event.text == 'Новый вопрос':
                handle_new_question_request(
                    event, vk_api, keyboard, questions, redis_db)
            else:
                handle_solution_attempt(event, vk_api, keyboard, redis_db)


if __name__ == '__main__':
    main()
