import asyncio
from config import main_logger
from db import init_db
from bot import start_bot

#####################################################################################
# main
async def main():
    """
    Основная функция запуска бота.

    Инициализирует подключение к базе данных, запускает бота для обработки сообщений.
    Логирует каждый этап запуска, обработки ошибок и завершения.

    Использование:
        Вызывается при запуске скрипта для старта бота и подключения к базе данных.
    """
    main_logger.info("Начало запуска...")
    try:
        main_logger.info("Подключение к базе данных...")
        await init_db()
       
        main_logger.info("Запуск бота...")
        await start_bot()
    except Exception as e:
        main_logger.error(f"Произошла ошибка во время выполнения: {e}")
        main_logger.exception("Исключение при запуске бота:")

if __name__ == "__main__":
    main_logger.info("---")
    asyncio.run(main())
