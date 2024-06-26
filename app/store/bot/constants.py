BREAK_LINE = "%0A"


class BotTextCommands:
    create_game = "/create"
    get_info = "/info"


class BotEventCommands:
    join = "join"


class BotMessages:
    info = f"""
        Привет! Я бот, добавляющий в ваш чат игру 100 к 1{BREAK_LINE} \
        Мои команды:{BREAK_LINE} \
        /create - команда для создания игры{BREAK_LINE} \
        /info - команда для выводы инормации обо мне{BREAK_LINE}
    """
    create = f"""
        Игра создалась!{BREAK_LINE}
        Ожидаем подключения игроков в течении 10 секунд{BREAK_LINE}
    """
    back_timer = "Осталось {seconds} секунд..."
    time_over = "Время вышло!"
    start = "Начало игры через 5 секунд!"
    already_join = "Вы уже присоединились к этой игре"
    user_join = "Вы присоединились к игре"
    user_failed = "{user} неверно ответил на вопрос"
    user_lost = "{user} выбывает из игры"
    user_right = "{user} верно ответил на вопрос и получил {score} очков"
    end_game = "Игра окончена. Победитель: {user}, он набрал {score} очков"
