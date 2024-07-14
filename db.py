import aiosqlite
from config import DB_NAME, db_logger, main_logger
from utils.questions_loader import questions_loader
import random

questions_data = questions_loader.get_data()


#####################################################################################
# get_result


async def get_result(user_id):
    """
    Получает данные о текущем состоянии квиза для пользователя.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        dict: Словарь с данными о состоянии квиза (отвеченные, правильные, неправильные вопросы).

    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute('SELECT answered_questions, wrong_questions, correct_questions FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    answered_questions = row[0].split(',') if row[0] else []
                    wrong_questions = row[1].split(',') if row[1] else []
                    correct_questions = row[2].split(',') if row[2] else []
                else:
                    answered_questions = []
                    wrong_questions = []
                    correct_questions = []

                result = {
                    'answered_questions': answered_questions,
                    'wrong_questions': wrong_questions,
                    'correct_questions': correct_questions
                }
                return result
    except Exception as e:
        db_logger.error(f"Ошибка в get_result: {e}")


#####################################################################################
# get_next_question_id


async def get_next_question_id(user_id, current_id):
    """
    Возвращает следующий идентификатор вопроса, на который пользователь еще не отвечал.

    Args:
        user_id (int): Идентификатор пользователя.
        current_id (int): Текущий идентификатор вопроса.

    Returns:
        int: Идентификатор следующего вопроса.
    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute('SELECT answered_questions FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    answered_questions = row[0]
                    answered_questions_list = answered_questions.split(',')

                    unanswered_questions = [q['id'] for q in questions_data if str(
                        q['id']) not in answered_questions_list]

                    if not unanswered_questions:
                        return None

                    next_question_id = random.choice(unanswered_questions)
                    return next_question_id

                else:
                    return random.choice([q['id'] for q in questions_data])

    except Exception as e:
        db_logger.error(f"Ошибка в get_next_question_id: {e}")
        return None


#####################################################################################
# get_questions_list


async def get_questions_list(user_id, question_type):
    """
    Получает список вопросов определенного типа (правильные, неправильные) для пользователя.

    Args:
        user_id (int): Идентификатор пользователя.
        question_type (str): Тип вопросов ('correct' или 'wrong').

    Returns:
        list: Список идентификаторов вопросов данного типа для пользователя.

    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute(f'SELECT {question_type}_questions FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    questions = row[0]
                    questions_list = questions.split(',') if questions else []
                else:
                    questions_list = []
        return questions_list
    except Exception as e:
        db_logger.error(f"Ошибка в get_questions_list: {e}")


#####################################################################################
# get_questions_list


async def update_questions_list(user_id, question_id, question_type):
    """
    Обновляет список вопросов определенного типа (правильные, неправильные) для пользователя.

    Args:
        user_id (int): Идентификатор пользователя.
        question_id (int): Идентификатор вопроса.
        question_type (str): Тип вопросов ('correct' или 'wrong').

    """
    try:
        questions_list = await get_questions_list(user_id, question_type)
        if str(question_id) not in questions_list:
            questions_list.append(str(question_id))
            questions = ','.join(questions_list)
            async with aiosqlite.connect(DB_NAME) as db:
                await db.execute(f'UPDATE quiz_state SET {question_type}_questions = ? WHERE user_id = ?', (questions, user_id))
                await db.execute(f'INSERT OR IGNORE INTO quiz_state (user_id, {question_type}_questions) VALUES (?, ?)', (user_id, questions))
                await db.commit()
    except Exception as e:
        db_logger.error(f"Ошибка в update_questions_list: {e}")


#####################################################################################
# add_question_to_wrong


async def add_question_to_wrong(user_id, question_id):
    """
    Добавляет вопрос в список неправильных ответов для пользователя.

    Args:
        user_id (int): Идентификатор пользователя.
        question_id (int): Идентификатор вопроса.

    """
    try:
        await update_questions_list(user_id, question_id, 'wrong')
    except Exception as e:
        db_logger.error(f"Ошибка в add_question_to_wrong: {e}")


#####################################################################################
# add_question_to_correct


async def add_question_to_correct(user_id, question_id):
    """
    Добавляет вопрос в список правильных ответов для пользователя.

    Args:
        user_id (int): Идентификатор пользователя.
        question_id (int): Идентификатор вопроса.

    """
    try:
        await update_questions_list(user_id, question_id, 'correct')
    except Exception as e:
        db_logger.error(f"Ошибка в add_question_to_correct: {e}")


#####################################################################################
# add_question_to_answered


async def add_question_to_answered(user_id, question_id):
    """
    Добавляет вопрос в список отвеченных вопросов для пользователя.

    Args:
        user_id (int): Идентификатор пользователя.
        question_id (int): Идентификатор вопроса.

    """
    question_id = str(question_id)
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute('SELECT answered_questions FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    answered_questions = row[0]
                    answered_questions_list = answered_questions.split(
                        ',') if answered_questions else []
                else:
                    answered_questions_list = []

            if str(question_id) not in answered_questions_list:
                answered_questions_list.append(str(question_id))
                answered_questions = ','.join(answered_questions_list)

                await db.execute('UPDATE quiz_state SET answered_questions = ? WHERE user_id = ?', (answered_questions, user_id))
                await db.execute('INSERT OR IGNORE INTO quiz_state (user_id, answered_questions) VALUES (?, ?)', (user_id, answered_questions))
                await db.commit()
    except Exception as e:
        db_logger.error(f"Ошибка в add_question_to_answered: {e}")


#####################################################################################
# del_user_progress


async def del_user_progress(user_id):
    """
    Очищает данные о прогрессе пользователя в базе данных.

    Args:
        user_id (int): ID пользователя, чей прогресс нужно удалить.

    Использование:
        Вызывается для удаления данных о текущем прогрессе квиза у конкретного пользователя.
    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute('DELETE FROM quiz_state WHERE user_id = ?', (user_id,))
            await db.commit()
    except Exception as e:
        db_logger.error(f"Ошибка в del_user_progress: {e}")


#####################################################################################
# check_user_exists


async def check_user_exists(user_id):
    """
    Проверяет, существует ли пользователь с указанным ID в базе данных квиза.

    Args:
        user_id (int): ID пользователя для проверки.

    Returns:
        bool: True, если пользователь существует в базе данных, False в противном случае.

    Использование:
        Вызывается для проверки наличия пользователя в базе данных перед началом игры или продолжением.
    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT EXISTS(SELECT 1 FROM quiz_state WHERE user_id = ?)", (user_id,)) as cursor:
                result = await cursor.fetchone()
                exists = result[0]
                return exists
    except Exception as e:
        db_logger.error(f"Ошибка в check_user_exists: {e}")


#####################################################################################
# update_user_current_quiz_id


async def update_user_current_quiz_id(user_id, id):
    """
    Обновляет идентификатор текущего вопроса для пользователя в базе данных.

    Если запись для данного user_id уже существует, обновляет поле current_question_id.
    Если запись не существует, вставляет новую запись с user_id и current_question_id.

    Args:
        user_id (int): Идентификатор пользователя.
        id (int): Идентификатор текущего вопроса.

    Использование:
        Эта функция вызывается для обновления состояния текущего вопроса в квизе для конкретного пользователя.
        Обычно вызывается из других функций, управляющих ходом квиза, таких как new_quiz или обработчики сообщений.

    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute('UPDATE quiz_state SET current_question_id = ? WHERE user_id = ?', (id, user_id))
            # Если запись для user_id не существует, вставляем новую
            await db.execute('INSERT OR IGNORE INTO quiz_state (user_id, current_question_id) VALUES (?, ?)', (user_id, id))
            await db.commit()
    except Exception as e:
        db_logger.error(f"Ошибка в update_user_current_quiz_id: {e}")


#####################################################################################
# get_quiz_id


async def get_quiz_id(user_id):
    """
    Получает текущий идентификатор вопроса для пользователя из базы данных.

    Если запись для данного user_id существует, возвращает текущий идентификатор вопроса.
    Если запись не существует, возвращает 1 как начальный идентификатор вопроса.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        int: Текущий идентификатор вопроса для пользователя или 1, если запись не найдена.

    Использование:
        Эта функция вызывается для получения текущего состояния квиза для пользователя.
        Обычно вызывается из других функций, управляющих ходом квиза, таких как new_quiz или get_question.

    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute('SELECT current_question_id FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
                results = await cursor.fetchone()
                if results is not None:
                    return results[0]
                else:
                    return 1
    except Exception as e:
        db_logger.error(f"Ошибка в get_quiz_id: {e}")


#####################################################################################
# init_db


async def init_db():
    """
    Инициализирует базу данных для хранения состояния квиза.

    Создает таблицу quiz_state, если она не существует, для хранения информации о текущем вопросе,
    ответах пользователя и статистике ответов.

    Использование:
        Вызывается при старте бота для инициализации структуры базы данных.
    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (
                                user_id INTEGER PRIMARY KEY,
                                current_question_id INTEGER,
                                answered_questions TEXT,
                                correct_questions TEXT,
                                wrong_questions TEXT)''')
            await db.commit()
        main_logger.info("Подключение к базе данных... Успешно")
    except Exception as e:
        main_logger.error(
            f"Не удалось создать или подключиться к базе данных. {e}")
