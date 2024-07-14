from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config import bot_logger
from db import check_user_exists

#####################################################################################
# cmd_start
async def cmd_start(message: types.Message):
    """
    Обрабатывает команду /start от пользователя.

    Проверяет, существует ли пользователь в базе данных. В зависимости от результата,
    предлагает ему продолжить текущую игру или начать новую.

    Args:
        message (types.Message): Сообщение, вызвавшее команду. Содержит информацию о пользователе и тексте команды.

    Использование:
        Вызывается при получении команды /start от пользователя для инициализации игры или продолжения текущей игры.
    """
    builder = ReplyKeyboardBuilder()
    user_id = message.from_user.id
    bot_logger.info(f"Пользователь: {user_id} запустил бота")

    try:
        user_exists = await check_user_exists(user_id)

        if user_exists:
            bot_logger.info(f"Пользователь: {user_id} найден в базе данных")
            builder.add(types.KeyboardButton(text="Продолжить игру"))
            await message.answer("<b>С возвращением!</b>", reply_markup=builder.as_markup(resize_keyboard=True))
        else:
            bot_logger.info(f"Пользователь: {user_id} не найден в базе данных")
            builder.add(types.KeyboardButton(text="Начать игру"))
            await message.answer("<b>Добро пожаловать в квиз!</b>", reply_markup=builder.as_markup(resize_keyboard=True))

    except Exception as e:
        bot_logger.error(f"Не удалось выполнить команду /start {e}")
