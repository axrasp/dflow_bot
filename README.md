# Бот-помощник службы поддержки клиентов (Telegram + VK)


Бот позволяет отвечать на типичные вопросы пользователей с помощью данных из DialogFlow
Учебный проект в [dvmn.org](https://dvmn.org/)

![](https://s4.gifyu.com/images/IMG_0992.gif)

## Установка

Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть конфликт с Python2) для установки зависимостей:

```
pip install -r requirements.txt
```

### Получение чувствительных данных

Создайте бота в телеграме через [https://t.me/BotFather](https://t.me/BotFather)

Создайте файл ``.env`` и добавьте в него следующие данные вида:

```
TOKEN=5662038928:AAEm652uxCui7HbiuKu7CKl1STF3faKpW3Q
PROJECT_ID=dflow-329614
GOOGLE_APPLICATION_CREDENTIALS=dflow-361614-694810ee70a6.json
NEW_INTENTS_FILE_PATH=""
VK_TOKEN="vk1.a.-xrccnJWctU7lAnbe9-Cx43cbBMczQMx-U9L7sWgc5JHIv_MibxSFWpgE-Gkms149mR4tbDJJaJzBZ3oDJQ6Kcu7arg3S17NpSY6MbpKFsVG8UuVP91NRoi8j9ZA0ZoLJnj4Ek0DR0_UUSPJqV-7lIEUxs0z--TjJtigMtbNa87u0KSfqTo6kPShd7k2r-o6jDst0VPNSV
CHAT_ID="79939547"
```

- DEVMAN_TOKEN - токен в вашем личном кабинете [школы Devman](https://dvmn.org/api/docs/) 
- PROJECT_ID - Номер проекта в [Google Cloud ](https://console.cloud.google.com/)
- GOOGLE_APPLICATION_CREDENTIALS - путь до файла ``json`` c [ключом](https://cloud.google.com/docs/authentication/client-libraries)
- NEW_INTENTS_FILE_PATH - путь до файла с обучающими фразами (если есть)
- VK_TOKEN - [токен](https://vk.com/@articles_vk-token-groups?ysclid=lb26bno4x7379535242) из вашего сообщества VK
- CHAT_ID= - ID чата в который будут приходить уведомление об ошибках бота

## Подключение DialogFlow

[DialogFlow](https://dialogflow.cloud.google.com/#/login) - облачный сервис распознавания естественного языка от Google, который поддерживает различные языки, в том числе русский.
[Подробнее](https://habr.com/ru/post/502688/)

Установка:
1. [Создаем проект](https://cloud.google.com/dialogflow/es/docs/quick/setup) и получаем ID проекта
2. [Cоздаем Агента](https://cloud.google.com/dialogflow/es/docs/quick/build-agent)
3. [Создаем JSON ключ](https://dvmn.org/modules/chat-bots/lesson/support-bot/#6). Вам потребуется ID проекта, который вы получили, когда создавали проект
session_id — это строка, уникальная для каждого пользователя бота, чтобы он мог отличать одного пользователя от другого. Для этого замечательно подойдёт id пользователя из Telegram. Не забудьте добавить необходимых прав доступа для Агента ``Role`` в [IAM](https://console.cloud.google.com/iam-admin): ``Dialogflow API Client``,
``Dialogflow API Reader``, ``Dialogflow Service Agent``.
4. Добавляем ``GOOGLE_APPLICATION_CREDENTIALS`` в ``.env``. 

## Обучение DialogFlow

Для обучения вашего Агента DialogFlow, используйте json-файл вида:

```json
{
  "Устройство на работу": {
    "questions": [
      "Как устроиться к вам на работу?",
      "Как устроиться к вам?",
      "Как работать у вас?",
      "Хочу работать у вас",
      "Возможно-ли устроиться к вам?",
      "Можно-ли мне поработать у вас?",
      "Хочу работать редактором у вас"
    ],
    "answer": "Если вы хотите устроиться к нам, напишите на почту game-of-verbs@gmail.com мини-эссе о себе и прикрепите ваше портфолио."
  },
  "Забыл пароль": {
    "questions": [
      "Не помню пароль",
      "Не могу войти",
      "Проблемы со входом",
      "Забыл пароль",
      "Забыл логин",
      "Восстановить пароль",
      "Как восстановить пароль",
      "Неправильный логин или пароль",
      "Ошибка входа",
      "Не могу войти в аккаунт"
    ],
    "answer": "Если вы не можете войти на сайт, воспользуйтесь кнопкой «Забыли пароль?» под формой входа. Вам на почту прийдёт письмо с дальнейшими инструкциями. Проверьте папку «Спам», иногда письма попадают в неё."
  },
  ...
}

```

Укажите путь до этого файла в ``NEW_INTENTS`` в файле ``.env``.
Запустите обучающий скрипт:

```
python3 bot_learning.py
```

## Запуск TG-бота на локальном сервере

Запустите бот командой:

```
python3 bot.py
```

Запусите бота в телегамме ``/start``

## Запуск VK-бота на локальном сервере

Запустите бот командой:

```
python3 vk_bot.py
```

## Деплой на свой сервер

Загрузите репозиторий на сервер (в этом примере грузим в /opt/your_bot_name).
Создайте виртуальное окружение в папке бота:

```commandline
python3 -m venv venv
```

Активируйте виртуальное окружение:

```
source venv/bin/activate
```
Установите зависимости и чувствительные данные (см. раздел Установка)

### Демонизация бота

#### VK
Создайте новый файл в папке ``/etc/systemd/system`` с названием:
``your_bot_name_vk.service`` для VK-бота c таким содержимым:

```
[Service]
ExecStart=/opt/your_bot_name/venv/bin/python3 /opt/your_bot_name/vk_bot.py
Restart=always


[Install]
WantedBy=multi-user.target
```

Добавляем бота в автозагрузку

```commandline
systemctl enable your_bot_name_vk
```

Запускаем бота:

```commandline
systemctl start your_bot_name_vk
```

#### Telegram
Создайте новый файл в папке ``/etc/systemd/system`` с названием:
``your_bot_name_tg.service`` для VK-бота c таким содержимым:

```
[Service]
ExecStart=/opt/your_bot_name/venv/bin/python3 /opt/your_bot_name/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Добавляем бота в автозагрузку

```commandline
systemctl enable your_bot_name
```

Запускаем бота:

```commandline
systemctl start your_bot_name
```

Подробнее о systemd [здесь](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
Туториал [здесь](https://4te.me/post/systemd-unit-ubuntu/)