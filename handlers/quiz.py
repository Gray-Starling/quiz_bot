from aiogram import types
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from config import quiz_logger
from db import update_user_current_quiz_id, get_quiz_id, add_question_to_answered, del_user_progress, get_next_question_id, add_question_to_correct, add_question_to_wrong
from utils.questions_loader import questions_loader
from utils.get_question_by_id import get_question_by_id
from handlers.results import callback_results_request
from utils.callback_data import CallbackAnswers
from utils.wait_for_result import wait_for_result
import random

questions_data = questions_loader.get_data()


#####################################################################################
# process_answer


async def process_answer(callback: types.CallbackQuery, is_correct: bool):
    """
    Обрабатывает ответ пользователя на вопрос.

    Args:
        callback (types.CallbackQuery): Объект коллбэк запроса от пользователя.
        is_correct (bool): Флаг, указывающий, был ли ответ правильным.

    Использование:
        Эта функция вызывается при выборе варианта ответа пользователем.
    """
    try:
        await callback.bot.edit_message_reply_markup(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )

        current_question_id = await get_quiz_id(callback.from_user.id)

        await add_question_to_answered(callback.from_user.id, current_question_id)

        callback_data = CallbackAnswers.unpack(callback.data)
        option_index = callback_data.option_index
        question = await get_question_by_id(callback_data.id)
        

        await callback.message.answer(f"Ваш ответ: <b>'{question["options"][option_index]}'</b>")
        await callback.message.answer("И это...")
        await wait_for_result(callback.message)

        if is_correct:
            await add_question_to_correct(callback.from_user.id, current_question_id)
            await callback.message.answer("<b>Верно! 👍</b>")
        else:
            await add_question_to_wrong(callback.from_user.id, current_question_id)
            await callback.message.answer("<b>Не верно! 😭</b>")

        next_question_id = await get_next_question_id(callback.from_user.id, current_question_id)

        if next_question_id:
            await update_user_current_quiz_id(callback.from_user.id, next_question_id)
            await get_question(callback.message, callback.from_user.id)
        else:
            await callback.message.answer("Это был последний вопрос. Квиз завершен!")
            await callback_results_request(callback)
    except Exception as e:
        quiz_logger.error(f"Ошибка в process_answer. {e}")


#####################################################################################
# wrong_answer


async def wrong_answer(callback: types.CallbackQuery):
    """
    Обрабатывает неправильный ответ пользователя.

    Args:
        callback (types.CallbackQuery): Объект коллбэк запроса от пользователя.
    """
    try:
        await process_answer(callback, is_correct=False)
    except Exception as e:
        quiz_logger.error(f"Ошибка в wrong_answer. {e}")


#####################################################################################
# right_answer


async def right_answer(callback: types.CallbackQuery):
    """
    Обрабатывает правильный ответ пользователя.

    Args:
        callback (types.CallbackQuery): Объект коллбэк запроса от пользователя.
    """
    try:
        await process_answer(callback, is_correct=True)
    except Exception as e:
        quiz_logger.error(f"Ошибка в right_answer. {e}")


#####################################################################################
# generate_options_keyboard


def generate_options_keyboard(answer_options, right_answer, current_question_id):
    """
    Создает клавиатуру с вариантами ответов для квиза.

    Добавляет кнопки с текстом вариантов ответов. Кнопка с правильным ответом получает callback_data "right_answer",
    а кнопки с неправильными ответами получают callback_data "wrong_answer".

    Args:
        answer_options (list): Список вариантов ответов.
        right_answer (str): Правильный ответ.

    Returns:
        types.InlineKeyboardMarkup: Клавиатура с вариантами ответов.

    Использование:
        Эта функция вызывается для создания клавиатуры с вариантами ответов для вопроса в квизе.
        Обычно вызывается из других функций, управляющих ходом квиза, таких как get_question.
    """
    try:
        builder = InlineKeyboardBuilder()
        for idx, option in enumerate(answer_options):
            builder.add(types.InlineKeyboardButton(
                text=option,
                callback_data=CallbackAnswers(is_correct="r" if option == right_answer else "w",id=current_question_id, option_index=idx).pack())
            )

        builder.adjust(1)
        return builder.as_markup()
    except Exception as e:
        quiz_logger.error(f"Ошибка в generate_options_keyboard. {e}")


#####################################################################################
# get_question


async def get_question(message, user_id):
    """
    Отправляет текущий вопрос квиза пользователю.

    Получает текущий идентификатор вопроса для пользователя, извлекает вопрос из базы данных,
    и отправляет его пользователю с клавиатурой вариантов ответов.

    Args:
        message (types.Message): Сообщение, вызвавшее команду. Содержит информацию о пользователе и тексте команды.
        user_id (int): Идентификатор пользователя.

    Использование:
        Эта функция вызывается для отправки следующего вопроса в квизе пользователю.
        Обычно вызывается из других функций, управляющих ходом квиза, таких как new_quiz или обработчики сообщений.

    """
    try:
        current_question_id = await get_quiz_id(user_id)
        question = await get_question_by_id(current_question_id)
        if question:
            correct_index = question['correct_option']
            opts = question['options']
            kb = generate_options_keyboard(opts, opts[correct_index], current_question_id)
            await message.answer(f"{question['question']}", reply_markup=kb)
    except Exception as e:
        quiz_logger.error(f"Ошибка в get_question. {e}")


#####################################################################################
# new_quiz


async def new_quiz(message, user_id):
    """
    Начинает новый квиз для пользователя.

    Выбирает случайный вопрос из списка доступных вопросов, обновляет текущий идентификатор вопроса для пользователя
    и отправляет вопрос пользователю.

    Args:
        message (types.Message): Сообщение, вызвавшее команду. Содержит информацию о пользователе и тексте команды.

    Использование:
        Эта функция вызывается внутри других команд или обработчиков, таких как cmd_new_quiz, чтобы начать новый квиз.

    """
    try:
        current_question_id = random.randint(1, len(questions_data))
        await update_user_current_quiz_id(user_id, current_question_id)

        await get_question(message, user_id)
    except Exception as e:
        quiz_logger.error(f"Ошибка в new_quiz. {e}")


#####################################################################################
# cmd_resume_quiz


async def cmd_resume_quiz(message: types.Message):
    """
    Обрабатывает команду продолжения квиза.

    Args:
        message (types.Message): Сообщение, вызвавшее команду.
    """
    try:
        builder = ReplyKeyboardBuilder()

        builder.add(types.KeyboardButton(text="Начать заново"))
        builder.add(types.KeyboardButton(text="Результаты"))

        await message.answer("Отлично, продолжаем.", reply_markup=builder.as_markup(resize_keyboard=True))
        await get_question(message, message.from_user.id)
        quiz_logger.info(f"Пользователь: {message.from_user.id} возобновил игру")
    except Exception as e:
        quiz_logger.error(f"Ошибка в cmd_resume_quiz. {e}")


#####################################################################################
# callback_resume_quiz


async def callback_resume_quiz(callback: types.CallbackQuery):
    """
    Обрабатывает callback-запрос продолжения квиза.

    Args:
        callback (types.CallbackQuery): Callback-запрос от пользователя.
    """
    try:
        await callback.bot.edit_message_reply_markup(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )
        await callback.message.answer("Отлично, продолжаем.")
        await get_question(callback.message, callback.message.chat.id)
    except Exception as e:
        quiz_logger.error(f"Ошибка в callback_resume_quiz. {e}")


#####################################################################################
# restart_quiz


async def restart_quiz(callback: types.CallbackQuery):
    """
    Перезапускает квиз для пользователя после подтверждения.

    Удаляет прогресс текущего пользователя и запускает новый квиз.

    Args:
        callback (types.CallbackQuery): Объект коллбэк запроса от пользователя.

    Использование:
        Вызывается после того, как пользователь подтвердил желание начать квиз заново.
        Удаляет данные о текущем прогрессе пользователя и запускает новый квиз.
    """
    try:
        await callback.bot.edit_message_reply_markup(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )
        await del_user_progress(callback.from_user.id)
        await callback.message.answer("Квиз перезапущен. Начинаем новый квиз...")
        await new_quiz(callback.message, callback.message.chat.id)
    except Exception as e:
        quiz_logger.error(f"Ошибка в restart_quiz. {e}")


#####################################################################################
# restart_quiz_confirm


async def restart_quiz_confirm(message: types.Message):
    """
    Отправляет пользователю подтверждение о желании начать квиз заново.

    Args:
        message (types.Message): Сообщение от пользователя.

    Использование:
        Вызывается для отправки пользователю подтверждения о желании начать квиз заново.
        Создает клавиатуру с кнопками "Да" и "Нет" для выбора пользователем.
    """
    try:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Да",
            callback_data="want_to_restart")
        )
        builder.add(types.InlineKeyboardButton(
            text="Нет",
            callback_data="dont_want_to_restart")
        )

        builder.adjust(1)
        markup = builder.as_markup()
        await message.answer("Вы уверены, что хотите начать quiz заново?", reply_markup=markup)
    except Exception as e:
        quiz_logger.error(f"Ошибка в restart_quiz_confirm. {e}")


#####################################################################################
# cmd_new_quiz


async def cmd_new_quiz(message: types.Message):
    """
    Функция запускает квиз при команде /quiz или при нажатии кнопки "Начать игру".

    Заменяет текущую кнопку "Начать игру" на кнопки "Начать заново" и "Результаты".
    Отправляет приветственное сообщение и вызывает функцию new_quiz для начала нового квиза.

    Args:
        message (types.Message): Сообщение, вызвавшее команду. Содержит информацию о пользователе и тексте команды.

    Использование:
        Эта функция регистрируется как обработчик команд в диспетчере бота:

        dp.message.register(cmd_new_quiz, F.text == "Начать игру")
        dp.message.register(cmd_new_quiz, Command("quiz"))
    """
    try:
        builder = ReplyKeyboardBuilder()

        builder.add(types.KeyboardButton(text="Начать заново"))
        builder.add(types.KeyboardButton(text="Результаты"))

        await message.answer("Мы начинаем. Первый вопрос...", reply_markup=builder.as_markup(resize_keyboard=True))

        await new_quiz(message, message.from_user.id)
    except Exception as e:
        quiz_logger.error(f"Ошибка в cmd_new_quiz. {e}")