from dotenv import load_dotenv
import os
from utils.logger import setup_logger

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')

DB_NAME = 'quiz_bot.db'

main_logger = setup_logger("main")
bot_logger = setup_logger("bot")
db_logger = setup_logger("db")
quiz_logger = setup_logger("quiz")