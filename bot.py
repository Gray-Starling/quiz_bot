from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties
from aiogram import F
from config import TOKEN, main_logger
from handlers.start import cmd_start
from handlers.quiz import cmd_new_quiz, restart_quiz_confirm, restart_quiz, cmd_resume_quiz, right_answer, wrong_answer, callback_resume_quiz
from handlers.results import cmd_results_request
from utils.callback_data import CallbackAnswers

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

#####################################################################################
# Регистрация событий

# Слушатель запуска бота
dp.message.register(cmd_start, Command("start"))

# Слушатели начала квиза
dp.message.register(cmd_new_quiz, F.text == "Начать игру")
dp.message.register(cmd_new_quiz, Command("quiz"))

# Слушатели продолжения квиза
dp.message.register(cmd_resume_quiz, F.text == "Продолжить игру")
dp.message.register(cmd_resume_quiz, Command("resume"))

# Слушатель правильного ответа
# dp.callback_query.register(right_answer, F.data == "right_answer")
dp.callback_query.register(right_answer, CallbackAnswers.filter(F.is_correct == "r"))

# Слушатель не правильного ответа
# dp.callback_query.register(wrong_answer, F.data == "w")
dp.callback_query.register(wrong_answer, CallbackAnswers.filter(F.is_correct == "w"))

# Слушатели перезапуска квиза
dp.message.register(restart_quiz_confirm, F.text == "Начать заново")
dp.message.register(restart_quiz_confirm, Command("restart"))
dp.callback_query.register(restart_quiz, F.data == "want_to_restart")
dp.callback_query.register(
    callback_resume_quiz, F.data == "dont_want_to_restart")

# Слушатели вывода результатов квиза
dp.message.register(cmd_results_request, F.text == "Результаты")
dp.message.register(cmd_results_request, Command("results"))


#####################################################################################
# start_bot
def on_startup():
    """ Функция, вызываемая при старте бота.  """
    main_logger.info("Запуск бота... Успешно")


async def start_bot():
    """
    Запускает бота для обработки сообщений.

    Регистрирует функцию on_startup для выполнения при запуске бота.
    Запускает опрос сообщений с помощью метода start_polling объекта dp.

    Использование:
        Вызывается для начала работы бота и запуска процесса обработки сообщений.
    """
    dp.startup.register(on_startup)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        main_logger.error(f"Ошибка при запуске бота. {e}")
