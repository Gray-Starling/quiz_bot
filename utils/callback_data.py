from aiogram.filters.callback_data import CallbackData

class CallbackAnswers(CallbackData, prefix="callback_answers"):
    is_correct: str
    id: int
    option_index: int