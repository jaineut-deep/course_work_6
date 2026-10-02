from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError

from config import settings

if TYPE_CHECKING:
    from habbits.models import Habit


def validation_habit_consistency(obj: Habit) -> None:
    """
    Валидатор, проверяющий указана ли для полезной привычки — связанной и вознаграждение одновременно.
    :param obj: Habit
    :return: None
    """

    if (obj.related_habit is not None) and obj.reward and (not obj.is_enjoyable):
        raise ValidationError("У полезной привычки не может быть связанной привычки и вознаграждения одновременно")


def validation_enjoyable_on(obj: Habit) -> None:
    """
    Валидатор, проверяющий, что, если привычка обозначена как приятная у нее нет ни вознаграждения
    ни связанной привычки.
    :param obj: Habit
    :return: None
    """

    if (obj.is_enjoyable is True) and obj.reward:
        raise ValidationError({"is_enjoyable": "У приятной привычки не может быть вознаграждения"})
    elif (obj.is_enjoyable is True) & (obj.related_habit is not None):
        raise ValidationError({"is_enjoyable": "У приятной привычки не может быть связанной привычки"})


def validation_related_enjoyable(obj: Habit) -> None:
    """
    Валидатор, проверяющий, чтобы в качестве связанной была только приятная привычка
    :param obj:
    :return: None
    """

    if obj.related_habit is not None:
        if not obj.related_habit.is_enjoyable:
            raise ValidationError({"related_habit": "Связанной привычкой может быть только приятная"})


def validation_max_duration(duration: int) -> None:
    """
    Валидатор проверяет допустимые значения для времени выполнения привычки.
    :param duration:
    :return: None
    """

    if duration < 15:
        raise ValidationError({"duration": "Время выполнения не должно быть меньше 15 секунд"})
    elif duration > settings.HABIT_VALIDATION["DURATION"]:
        raise ValidationError(
            {"duration": f"Время выполнения не должно быть больше {settings.HABIT_VALIDATION["DURATION"]} секунд"}
        )


def validate_completion_periodicity(habit: Habit, ending: datetime) -> bool:
    """
    Валидатор, принимающий привычку и время окончани выполнения привычки и проверяющий соответствует ли время
    окончания выполнения периодизации привычки.
    :param habit:
    :param ending:
    :return: None
    """

    last = habit.completions.order_by("-completed_at").first()
    if last is None:
        return True
    return ending - last.completed_at >= timedelta(days=habit.get_periodicity)
