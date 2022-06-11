# frode

Увлекательное и удобное время провождение с пользой, в ходе которого Вам предстоит отвечать на вопросы бота в [Telegram](https://t.me/frode_quiz_bot) и [ВКонтакте](https://vk.com/quiz_frode).

## Установка

1. Скачать код

```
git clone https://github.com/dad-siberian/frode.git
```

2. Создать виртуальное окружение:

```
python3 -m venv venv
source venv/bin/activate
```

3. Установить зависимости командой

```
pip install -r requirements.txt
```

## Настройка

Настройки берутся из переменных окружения. Чтобы их определить, создайте файл `.env` в корне проекта и запишите туда данные в формате: `ПЕРЕМЕННАЯ=значение`.

- `TELEGRAM_TOKEN` - токен, полученный у телеграм бота [@BotFather](https://telegram.me/BotFather) ([инструкция](https://botcreators.ru/blog/kak-sozdat-svoego-bota-v-botfather/)).
- `TG_CHAT_ID` - Telegram id администратора ботов для получения системных оповещений. Можно узнать, написав в Telegram специальному боту: [@userinfobot](https://t.me/userinfobot)
- `VK_TOKEN` - токен группы ВК. Для его получения пройдите в управление своей группы. В разделе "Работа с API" нажмите на кнопку "Создать ключ". Отметьте галочками первые два пункта (Разрешить приложению доступ к управлению сообществом и Разрешить приложению доступ к сообщениям сообществом) и создайте ключ кнопкой "Создать" (необходимо смс подтверждение)
- `REDIS_HOST` - адрес базы данных Redis вида: redis-13965.f18.us-east-4-9.wc1.cloud.redislabs.com
- `REDIS_PORT` - порт базы данных Redis
- `REDIS_PASSWORD` - пароль базы данных Redis

Зарегистрируйтесь на [redis](https://redis.com/) для получения адреса базы данных, его порта и пароля. Для работы с Redis на территории РФ может понадобиться VPN

## Вопросы викторины

1. Скачать [архив](https://dvmn.org/media/modules_dist/quiz-questions.zip) с вопросами.

2. Создать в корне проекта папку `quiz-questions` и скопировать в нее содержимое архива.

3. Запустить скрипт командой:

```
pytnon db_questions.py
```

Результатом работы скрипта будет файл `questions_base.json`. В нем будут собраны все вопросы и ответы из архива.

## Запуск ботов

1. Запуск Телеграм бота:

```
pytnon frode_telegram_bot.py
```

2. Запуск VK бота:

```
pytnon frode_vk_bot.py
```

## Запуск бота на сервере

Для постоянной работы бота необходимо запустить на сервере, например на [Heroku: Cloud Application Platform](https://www.heroku.com).
На сайте есть подробная [инструкция](https://devcenter.heroku.com/articles/getting-started-with-python).

Переменные окружения передаются на сервер командой

```
heroku config:set TELEGRAM_TOKEN={telegram token}
```

Для работы с Heroku на территории РФ может понадобиться VPN

## Цели проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
