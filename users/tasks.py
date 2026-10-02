from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from habbits.models import Habit

from .services import get_reminder


@shared_task
def send_reminders():
    """
    Функция рассылает напоминания по расписанию каждому пользователю.
    """

    now = timezone.now()
    target_time = now + timedelta(minutes=1)

    habits = Habit.objects.filter(time__gt=now.time(), time__lt=target_time.time()).select_related("owner")
    reminders_sent = 0

    for habit in habits:
        chat_id = habit.owner.tg_chat_id
        if chat_id:
            print(f"Чат ID пользователя {habit.owner.pk} получен . . .")
            response_reminder = get_reminder(habit.time, chat_id)

            if response_reminder.status_code == 200:
                reminders_sent += 1
                print(f"Сообщение пользователю с ID {chat_id} отправлено")
            else:
                print(f"Сообщение пользователю с ID {chat_id} не отправлено")
