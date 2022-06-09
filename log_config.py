
from logging import Handler

from telegram import Bot


class TelegramLogsHandler(Handler):

    def __init__(self, telegram_token, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.token = telegram_token

    def emit(self, record):
        bot = Bot(token=self.token)
        log_entry = self.format(record)
        bot.send_message(chat_id=self.chat_id, text=log_entry)


ERROR_LOG_FILENAME = "error.log"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s:c:%(process)d:%(lineno)d " "%(levelname)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(name)s - %(message)s",
        },
    },
    "handlers": {
        "logfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "filename": ERROR_LOG_FILENAME,
            "formatter": "default",
            "backupCount": 2,
        },
        "verbose_output": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "frode": {
            "level": "INFO",
            "handlers": [
                "verbose_output",
            ],
            'propagate': False
        },
    },
    "root": {"level": "INFO", "handlers": ["logfile", "verbose_output"]},
}
