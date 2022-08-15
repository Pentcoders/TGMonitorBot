START_MESSAGE = "hello"
#payment_bot/botrequests/bot_murkups/bot_inform_attention.py
ATTENTIONMESSAGE = '\n'.join([
    '<b>!!!!!Внимание!!!!!</b>'.upper(),
    'Вам в Телеграм прийдет служебное сообщение от Телеграм',
    "<b>Необходимо прислать этот код <u>через дефис '-'</u></b> ",
    "<b>!!!НЕЛЬЗЯ его копировать из канала и сразу отправлять!!!</b>",
    "Отправьте код в формате <b><u>12-345</u></b>",
    'ТЕСТ', 
    '<b>Выберете КАК ВЫ ВВЕДЕТЕ КОД:</b>'
])

CONGRATULATION_EXTENSION = '\n'.join(
    [
        "Поздравляю с успешной покупкой подписки.",
        "Для работы мониторинга необходимо пройти процедуру авторизации.",
        "Продолжить?"
    ]
)

BOT_ADMIN_SIGNALS = '@adminchannel_crm_bot'

BUG_MESSAGE = "Что-то пошло не так. Обратитесь к службе поддержки."
NOT_AUTHORIZED_MESSAGE = "Вы не подключены к системе мониторинга. Авторизуйтесь."

END_SUBSCRIPTION = "У вас кончается подписка! Осталось {}."

# payment_bot/botrequests/authorized_menu.py
FORMAT_INPUTE_CODE = "Формат ввода: 12-345"
SEND_CODE_AUTHORIZED = "Отправьте код авторизации:"
SUCCESSFUL_AUTHORIZATION = "Вы уже успешно авторизованы."
FLOODWAIT_MESSAGE = "У вас ограниченный досту за черезмерную активность."
BAD_AUTHORIZATION_MASSEGE = "Вы не справились. Прочитайте инструкцию еще раз."
BAD_CODE_AUTHORIZATION_MASSEGE = "Код подтверждения от Телеграмм введен не правильно и был скомпрометирован"
TWO_FACTOR_BAD_MESSAGE = "Неверный пароль от двух этапной аутентификации"
USERBOT_BAD_MESSAGE = "UserBot не инициализирован"
CODE_AUTHORIZED_BAD_MESSAGE = "Ошибка кода авторизации"
SUCCESSFUL_AUTHORIZATION_USERBOT = "UserBot успешно авторизован"

# payment_bot/botrequests/card_monitoring.py
SUCCESSFUL_CREATE_CARD = "Карточка успешно создана."
CHOICE_MAX_COUNT_CHANNEL = "Вы выбрали максимальное количество каналов"
CHOICE_MAX_COUNT_PATTERN = "Вы ввели максимальное количество паттернов"
UPDATE_LIST_CHANNELS = "Обновлен список каналов для мониторинга."
INPUT_NEW_PATTERN = "Введите новый паттерн мониторинга:"
DELETE_QUESTION_PATTERN = "Вы уверены что хотите удалить паттерн?"
DELETE_PATTERN = "Паттерн {} успешно удален."
ERROR_MESSAGE = "Ошибка [{}]. обратитесь в тех поддержку"

# payment_bot/botrequests/card_profile.py
INPUT_NEW_NAME_CARD = "Введите новое название карты:"
INPUT_NEW_DESCRIPTION_CARD = "Введите новое назначение карты:"
DELETE_QUESTION_CARD = "Вы уверены что хотите удалить карточку мониторинга?"
DELETE_CARD = "Карточка {} успешно удалена."
RUN_MONITORING_MESSAGE = "Мониторинг карточки запущен"
STOP_MONITORING_MESSAGE = "Мониторинг карточки остановлен"
RUN_UPDATE_LIST_CHANNELS_MESSAGE = "Запущен процесс обновления списка каналов."

#payment_bot/botrequests/payment_menu.py
CONGRATULATION_EXTENSION = "Поздравляю с продлением подписки."

#payment_bot/botrequests/settings_menu.py
EMPTY_LIST_CARD = "У вас нет ни одной карточки мониторинга"
ALL_RUN_CARD = "У вас запущены все карты мониторинга" 
ALL_RUN_CARD_QUESTION = "Вы уверены что хотите запустить карточки:"
ALL_STOP_CARD = "У вас остановлены все карты мониторинга"
ALL_STOP_CARD_QUESTION = "Вы уверены что хотите остановить карточки:"

#payment_bot/botrequests/bot_murkups/bot_menu_markup.py
PREVIEW_MESSAGE = "Какая-то превьюха...."
BUY_SUBSCRIPTION = "Вы не зарегистрированы! Купите подписку."
MAIN_MENU_MESSAGE = "Тут информация для авторизованных пользователей"

#payment_bot/botrequests/bot_murkups/bot_password_markup.py
PASSWORD_QUESTION = "У вас есть пароль от двухэтапной аутентификации Telegram?"
INPUT_PASSWORD_MESSAGE = "Введите пароль от двухэтапной аутентификации Telegram"

#payment_bot/botrequests/bot_murkups/bot_phone_number_markup.py
SEND_PHONE_NUMBER = "Отправьте номер телефона"

# Кнопки
BUTTON_BUY_SUBSCRIPTION = "💰 Приобрести подписку"
BUTTON_HELP = "🆘 Помощь"
BUTTON_SUPPORT = "📞 Чат тех поддержки"
BUTTON_REBUY_SUBSCRIPTION = "💰 Продлить подписку"
BUTTON_SETTINGS = "🛠 Настройки"
BUTTON_MONITORING = "🔍 Мониторинг"

BT_PAYMENT_MENU_BUY_SUB = "Купить подписку"
BT_PAYMENT_MENU_DESCRIPTION_SUB = "Ознакомиться с соглашением"

INFO_SETTINGS_MENU = "Настройки пользователя:"
BT_SETTINGS_AUTHORIZED = "⚙️ Пройти авторизацию"
BT_SETTINGS_UPDATE_CHANNELS = "🔁 Обновить список каналов"
BT_SETTINGS_RUN_ALL_CARD = "🔄 Запустить мониторинг"
BT_SETTINGS_STOP_ALL_CARD = "🛑 Остановить мониторинг"
BT_BACK = "Назад"

SUBSCRIPTION_ERROR = "Сервис не доступен."

INFO_CREATE_CARD = "Создать карточку мониторинга"
BT_CREATE_CARD = "Создайте карточку мониторинга"
BT_CARD_MONITORING = "Мониторинг"
BT_CARD_PATTERN = "Паттерны"
BT_CARD_OPTIONS = "Опции"

BT_PATTERN_CREATE = "Создать паттерн мониторинга"
BT_PATTERN_CHANGE = "🪛 Паттерн"
BT_PATTERN_DELETE = "❌"

BT_CARD_OPTION_NAME = "🪛 Название"
BT_CARD_OPTION_DESC = "🪛 Назначение"
BT_CARD_OPTION_STOP = "⏹ Stop [card]"
BT_CARD_OPTION_START = "▶️ Start [card]"
BT_CARD_OPTION_DELETE = "❌ Удалить карту"

BT_LIST_CHANNELS_EMPTY = "У вас нет ни одного канала для мониторинга"
BT_LIST_CHANNELS_CHOISE = "Выберете каналы/чаты для мониторинга"
 