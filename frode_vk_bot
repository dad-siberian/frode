import json
import logging.config
import os
import random

import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from db_config import FRODE_DB
from log_config import LOGGING_CONFIG, TelegramLogsHandler

logger = logging.getLogger(__file__)


def handle_new_question_request(event, vk_api, keyboard):
    with open('questions_base.json', 'r', encoding='utf-8') as file:
        questions = json.load(file)
    questin_number = random.randrange(0, len(questions))
    question = questions[questin_number].get('Вопрос')
    answer = questions[questin_number].get('Ответ')
    FRODE_DB.set(event.user_id, answer)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id(),
    )


def handle_solution_attempt(event, vk_api, keyboard):
    answer = FRODE_DB.get(event.user_id)
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


def check_answer(correct_answer, attempt):
    correct_answer.replace('(', '.', 1)
    correct_answer = correct_answer.split('.')
    return attempt.lower() == correct_answer[0].lower()


def give_up(event, vk_api, keyboard):
    answer = FRODE_DB.get(event.user_id)
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
    load_dotenv()
    vk_token = os.getenv('VK_TOKEN')
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')

    logging.config.dictConfig(LOGGING_CONFIG)
    logger.addHandler(TelegramLogsHandler(telegram_token, chat_id))

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
                give_up(event, vk_api, keyboard)
            elif event.text == 'Новый вопрос':
                handle_new_question_request(event, vk_api, keyboard)
            else:
                handle_solution_attempt(event, vk_api, keyboard)


if __name__ == '__main__':
    main()
