import json
import logging.config
import os
import random

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

from db_questions import check_answer
from log_config import LOGGING_CONFIG, TelegramLogsHandler

logger = logging.getLogger(__file__)

PONDERING, RECREATION = range(2)


def start(update: Update, context: CallbackContext):
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    text = (
        f"Для начала викторины нажми «Новый вопрос»\n"
        f"Для выхода из викторины команда /cancel"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )
    return RECREATION


def handle_new_question_request(update: Update, context: CallbackContext):
    questions = context.bot_data['questions']
    question, answer = random.choice(questions).values()
    redis_db = context.bot_data['db']
    redis_db.set(update.effective_chat.id, answer)
    update.message.reply_text(question)
    return PONDERING


def handle_solution_attempt(update: Update, context: CallbackContext):
    redis_db = context.bot_data['db']
    answer = redis_db.get(update.effective_chat.id)
    attempt = update.message.text
    if check_answer(answer, attempt):
        text = 'Правильно! Поздравляю!\nДля следующего вопроса нажми «Новый вопрос»'
        update.message.reply_text(text)
        return RECREATION
    else:
        text = 'Неправильно… Попробуешь ещё раз?'
        update.message.reply_text(text)
        return PONDERING


def handle_score(update: Update, context: CallbackContext):
    # update.message.reply_text('Ваш счет: ')
    return RECREATION


def give_up(update: Update, context: CallbackContext):
    redis_db = context.bot_data['db']
    answer = redis_db.get(update.effective_chat.id)
    update.message.reply_text(
        f'Привильный ответ - {answer}\n'
        f'Для следующего вопроса нажми «Новый вопрос»'
    )
    return RECREATION


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Введи команду /start что бы снова начать',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    load_dotenv()
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
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['db'] = redis_db
    dispatcher.bot_data['questions'] = questions
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            RECREATION: [
                MessageHandler(Filters.regex("^Новый вопрос$"),
                               handle_new_question_request),
                MessageHandler(Filters.regex("^Мой счет$"), handle_score),
            ],
            PONDERING: [
                MessageHandler(Filters.regex("^Сдаться$"),
                               give_up),
                MessageHandler(Filters.text & (~Filters.command),
                               handle_solution_attempt),
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)
    logger.info('The Telegram Bot is running')
    updater.start_polling()


if __name__ == '__main__':
    main()
