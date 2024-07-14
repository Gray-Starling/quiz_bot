from aiogram import types
from db import get_result
from utils.questions_loader import questions_loader
from config import quiz_logger

questions_data = questions_loader.get_data()


#####################################################################################
# show_results


async def show_results(message, user_id):
    """
    Отображает результаты квиза для пользователя.

    Args:
        message (aiogram.types.Message): Сообщение, в ответ на которое будут отправлены результаты.
        user_id (int): Идентификатор пользователя, для которого отображаются результаты.
    """
    try:
        result = await get_result(user_id)

        count_of_all_questions = len(questions_data)
        count_of_answered_questions = len(result["answered_questions"])
        count_of_correct_questions = len(result["correct_questions"])
        count_of_wrong_questions = len(result["wrong_questions"])
        await message.answer("Ваш результат:")
        await message.answer(f"Вы ответили на <b>{count_of_answered_questions}</b> вопросов из <b>{count_of_all_questions}</b>")
        await message.answer(f"Правильных ответов: <b>{count_of_correct_questions}</b>")
        await message.answer(f"Не правильных ответов: <b>{count_of_wrong_questions}</b>")
    except Exception as e:
        quiz_logger.error(f"Ошибка в show_results. {e}")


#####################################################################################
# cmd_results_request


async def cmd_results_request(message: types.Message):
    """
    Обработчик команды для запроса результатов квиза.

    Args:
        message (aiogram.types.Message): Сообщение, содержащее команду.
    """
    try:
        await show_results(message, message.from_user.id)
    except Exception as e:
        quiz_logger.error(f"Ошибка в cmd_results_request. {e}")


#####################################################################################
# callback_results_request


async def callback_results_request(callback: types.CallbackQuery):
    """
    Обработчик callback-запроса для показа результатов квиза.

    Args:
        callback (aiogram.types.CallbackQuery): Callback-запрос.
    """
    try:
        await show_results(callback.message, callback.message.chat.id)
    except Exception as e:
        quiz_logger.error(f"Ошибка в callback_results_request. {e}")
