from datetime import timedelta

import requests
from django.utils import timezone
from requests import Response

from config import settings
from habbits.models import Habit


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
    response = requests.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage", params=params)

    return response


def send_reminders():
    """
    Функция рассылает напоминания по расписанию каждому пользователю.
    """

    now = timezone.now()
    target_time = now + timedelta(minutes=5)

    habits = Habit.objects.filter(time__gt=now.time(), time__lt=target_time.time()).select_related("owner")
    reminders_sent = 0

    for habit in habits:
        chat_id = habit.owner.tg_chat_id
        response_reminder = get_reminder(habit.time, chat_id)

        if response_reminder.status_code == 200:
            reminders_sent += 1
            print(f"Сообщение пользователю с ID {chat_id} отправлено")
        else:
            print(f"Сообщение пользователю с ID {chat_id} не отправлено")
