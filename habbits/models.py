from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from config import settings

from .validators import (validate_completion_periodicity, validation_enjoyable_on, validation_habit_consistency,
                         validation_max_duration, validation_related_enjoyable)


class Habit(models.Model):
    PERIODICITY = [(key, key.upper()) for key in settings.HABIT_VALIDATION["ALLOWED_PERIODICITY"]]

    place = models.CharField(max_length=60, verbose_name="Место", help_text="Укажите место для совершения привычки")
    time = models.TimeField(verbose_name="Время", help_text="Укажите время совершения привычки")
    action = models.CharField(
        max_length=120, verbose_name="Действие", help_text="Укажите действие совершаемое в качестве привычки"
    )
    periodicity = models.CharField(
        choices=PERIODICITY,
        blank=False,
        null=False,
        default="daily",
        verbose_name="Периодичность",
        help_text="Выберите периодичность выполнения привычки",
    )
    duration = models.PositiveIntegerField(
        default=120,
        validators=[MinValueValidator(15), MaxValueValidator(settings.HABIT_VALIDATION["DURATION"])],
        verbose_name="Время_на_выполнение(в секундах)",
        help_text="Укажите время выполнения привычки - от 15 до 120 секунд",
    )
    is_public = models.BooleanField(
        default=False, verbose_name="Признак_публичности", help_text="Отметьте нужно ли опубликовать привычку"
    )
    is_enjoyable = models.BooleanField(
        default=False, verbose_name="Признак_приятной_привычки", help_text="Является ли привычка приятной"
    )
    reward = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Вознаграждение",
        help_text="Чем пользователь должен себя вознаградить после полезной привычки",
    )
    related_habit = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="related_habits",
        help_text="Укажите привычку, связанную с этой полезной",
    )
    owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits", verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.username}: {self.action} в {self.time}"

    def clean(self):
        validation_habit_consistency(self)

        validation_enjoyable_on(self)

        validation_related_enjoyable(self)

        validation_max_duration(self.duration)

        super().clean()

    def save(self, *args, **kwargs) -> None:
        """
        Переопределенный метод save() для сохранения результата после валидаций полей модели Habit
        :param args:
        :param kwargs:
        :return: None
        """

        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def get_periodicity(self) -> int:
        """
        Метод возвращает периодичность в днях из настроек.
        :return: int
        """

        return settings.HABIT_VALIDATION["ALLOWED_PERIODICITY"].get(self.periodicity)

    def can_be_completed_today(self) -> bool:
        """
        Метод проверяющий
        :return:
        """

        return validate_completion_periodicity(self, timezone.now())

    class Meta:
        verbose_name = "привычка"
        verbose_name_plural = "привычки"
        ordering = ["time"]
        constraints = [
            models.CheckConstraint(
                name="duration_max_seconds", condition=models.Q(duration__lte=settings.HABIT_VALIDATION["DURATION"])
            ),
            models.CheckConstraint(
                name="enjoyable_no_reward", condition=~(models.Q(is_enjoyable=True) & ~models.Q(reward=""))
            ),
            models.CheckConstraint(
                name="enjoyable_no_related",
                condition=~(models.Q(is_enjoyable=True) & models.Q(related_habit__isnull=False)),
            ),
            models.CheckConstraint(
                name="not_both_related_and_reward",
                condition=(models.Q(related_habit__isnull=True) | models.Q(reward="")),
            ),
        ]


class HabitCompletion(models.Model):
    habit = models.ForeignKey(to=Habit, on_delete=models.CASCADE, related_name="completions", verbose_name="Привычка")

    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Время_завершения")

    is_completed = models.BooleanField(default=True, verbose_name="Выполнена")

    note = models.TextField(blank=True, verbose_name="Заметка", help_text="Опишите проведение привычки")

    def __str__(self):
        status = "ok" if self.is_completed else "not_ok"
        return f"{status} {self.habit.action} — {self.completed_at.strftime("%Y-%m-%d %H:%M:%S")}"

    def clean(self):
        if not self.pk:
            if not validate_completion_periodicity(self.habit, timezone.now()):
                raise ValidationError(
                    {"completed_at": f"Привычку можно выполнять не чаще, чем раз в {self.habit.get_periodicity} дн."}
                )
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "выполнение_привычки"
        verbose_name_plural = "выполнение_привычек"
        ordering = ["completed_at"]
        indexes = [
            models.Index(fields=["habit", "completed_at"]),
        ]
