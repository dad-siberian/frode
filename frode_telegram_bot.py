import json
import logging.config
import os
import random

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

from db_config import FRODE_DB
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
    with open('questions_base.json', 'r', encoding='utf-8') as file:
        questions = json.load(file)
    questin_number = random.randrange(0, len(questions))
    question = questions[questin_number].get('Вопрос')
    answer = questions[questin_number].get('Ответ')
    # Убрать до деплоя
    logger.info(answer)
    # context.user_data['answer'] = answer
    FRODE_DB.set(update.effective_chat.id, answer)
    update.message.reply_text(question)
    return PONDERING


def handle_solution_attempt(update: Update, context: CallbackContext):
    # answer = context.user_data.get('answer')
    answer = FRODE_DB.get(update.effective_chat.id)
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
    logger.info('Ваш счет: ')
    return RECREATION


def give_up(update: Update, context: CallbackContext):
    # answer = context.user_data.get('answer')
    answer = FRODE_DB.get(update.effective_chat.id)
    update.message.reply_text(
        f'Привильный ответ - {answer}\n'
        f'Для следующего вопроса нажми «Новый вопрос»'
    )
    # context.user_data.clear()
    return RECREATION


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Введи команду /start что бы снова начать',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def check_answer(correct_answer, attempt):
    correct_answer.replace('(', '.', 1)
    correct_answer = correct_answer.split('.')
    return attempt.lower() == correct_answer[0].lower()


def main():
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')

    logging.config.dictConfig(LOGGING_CONFIG)
    logger.addHandler(TelegramLogsHandler(telegram_token, chat_id))

    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher

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
