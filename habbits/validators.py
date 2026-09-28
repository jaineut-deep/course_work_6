from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from config import settings

if TYPE_CHECKING:
    from habbits.models import HabitCompletion, Habit


def validation_habit_consistency(obj: Habit) -> None:
    """
    Валидатор, проверяющий указана ли для полезной привычки — связанной и вознаграждение одновременно.
    :param obj: Habit
    :return: None
    """

    if (obj.related_habit is not None) & (obj.reward is not None) & (obj.is_enjoyable == False):
        raise ValidationError("У полезной привычки не может быть связанной привычки и вознаграждения одновременно")


def validation_enjoyable_on(obj: Habit) -> None:
    """
    Валидатор, проверяющий, что, если привычка обозначена как приятная у нее нет ни вознаграждения
    ни связанной привычки.
    :param obj: Habit
    :return: None
    """

    if (obj.is_enjoyable == True) & (obj.reward is not None):
        raise ValidationError({"is_enjoyable": "У приятной привычки не может быть вознаграждения"})
    elif (obj.is_enjoyable == True) & (obj.related_habit is not None):
        raise ValidationError({"is_enjoyable": "У приятной привычки не может быть связанной привычки"})


def validation_related_enjoyable(obj: Habit):
    """

    :param obj:
    :return:
    """

    if obj.related_habit_id:
        if not obj.related_habit_id.is_enjoyable:
            raise ValidationError({"related_habit": "Связанной привычкой может быть только приятная"})


def validation_max_duration(duration: int):
    """

    :param duration:
    :return:
    """

    if duration < 15:
        raise ValidationError({"duration": "Время выполнения не должно быть меньше 15 секунд"})
    elif duration > settings.HABIT_VALIDATION["DURATION"]:
        raise ValidationError(
            {"duration": f"Время выполнения не должно быть больше {settings.HABIT_VALIDATION["DURATION"]} секунд"}
        )


def validate_completion_periodicity(habit: Habit, ending: datetime) -> None:
    """
    Валидатор, принимающий привычку и время окончани выполнения привычки и проверяющий соответствует ли время
    окончания выполнения периодизации привычки.
    :param habit:
    :param ending:
    :return: None
    """

    try:
        last_completed_habits = habit.completions.latest("completed_at")
    except HabitCompletion.DoesNotExist:
        last_completed_habits = None

    if last_completed_habits:
        if (ending - last_completed_habits.completed_at) < timedelta(days=1):
            raise ValidationError(
                {"completed_at": "Нельзя выполнять привычку чаще чем 1 раз в день"}
            )
        elif (ending - last_completed_habits.completed_at) > timedelta(days=7):
            raise ValidationError(
                {"completed_at": "Нельзя выполнять привычку чаще чем 1 раз в день"}
            )
