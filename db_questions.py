import json
import logging.config
import os

from log_config import LOGGING_CONFIG

logger = logging.getLogger(__file__)


def add_questions_in_base(file, questions_base):
    with open(file, 'r', encoding='KOI8-R') as file:
        file_contents = file.read()
    question_answer = {}
    for sentence in file_contents.split('\n\n'):
        sentence = sentence.replace('\n', '')
        sep_index = sentence.find(':') + 1
        if sentence.startswith('Вопрос'):
            question_answer['Вопрос'] = sentence[sep_index:]
        elif sentence.startswith('Ответ'):
            question_answer['Ответ'] = sentence[sep_index:]
            questions_base.append(question_answer)
            question_answer = {}


def main():
    logging.config.dictConfig(LOGGING_CONFIG)
    
    questions_base = []
    for root, dirs, files in os.walk('quiz-questions'):
        for file in files:
            question_file = os.path.join(root, file)
            add_questions_in_base(question_file, questions_base)
    with open('questions_base.json', 'w', encoding='utf-8') as file:
        json.dump(questions_base, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
