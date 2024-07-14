from utils.questions_loader import questions_loader

questions_data = questions_loader.get_data()

#####################################################################################
# get_question_by_id
async def get_question_by_id(question_id):
    """
    Получает вопрос из списка вопросов по его идентификатору.

    Ищет вопрос с заданным идентификатором в глобальном списке вопросов `questions_data`.
    Возвращает вопрос, если он найден, иначе возвращает None.

    Args:
        question_id (int): Идентификатор вопроса.

    Returns:
        dict: Словарь, содержащий данные вопроса, если найден.
        None: Если вопрос с заданным идентификатором не найден.

    Использование:
        Эта функция вызывается для извлечения вопроса из списка вопросов по его идентификатору.
        Обычно вызывается из других функций, управляющих ходом квиза, таких как get_question или new_quiz.

    """
    for question in questions_data:
        if question['id'] == question_id:
            return question
    return None