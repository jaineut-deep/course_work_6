import requests
from requests import Response

from config import settings


def get_reminder(time, chat_id) -> Response:
    """
    Функция отправляет сообщение чат-боту по шаблону для обработки.
    :param time:
    :param chat_id:
    :return: Response
    """

    text = f"Выполнение вашей привычки скоро стартует в: {time}"

    params = {
        "text": text,
        "chat_id": chat_id,
    }
    response = requests.get(f"{settings.TELEGRAM_URL}{settings.BOT_TOKEN}/sendMessage", params=params)

    return response
