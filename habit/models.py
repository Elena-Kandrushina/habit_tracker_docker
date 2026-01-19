from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User


class Habit(models.Model):
    """Модель привычки"""

    PERIODICITY_CHOICES = [
        (1, 'Ежедневно'),
        (2, 'Раз в 2 дня'),
        (3, 'Раз в 3 дня'),
        (4, 'Раз в 4 дня'),
        (5, 'Раз в 5 дней'),
        (6, 'Раз в 6 дней'),
        (7, 'Раз в неделю'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Пользователь'
    )

    place = models.CharField(
        max_length=255,
        verbose_name='Место выполнения'
    )

    time = models.TimeField(
        verbose_name='Время выполнения'
    )

    action = models.CharField(
        max_length=500,
        verbose_name='Действие'
    )

    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Признак приятной привычки'
    )

    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_habits',
        verbose_name='Связанная привычка',
        limit_choices_to={'is_pleasant': True}
    )

    periodicity = models.PositiveIntegerField(
        default=1,
        choices=PERIODICITY_CHOICES,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(7)
        ],
        verbose_name='Периодичность (в днях)'
    )

    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Вознаграждение'
    )

    duration = models.PositiveIntegerField(
        default=60,
        validators=[MaxValueValidator(120)],
        verbose_name='Время на выполнение (в секундах)'
    )

    is_public = models.BooleanField(
        default=False,
        verbose_name='Признак публичности'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email}: {self.action} в {self.time}"


class HabitCompletion(models.Model):
    """Модель для отслеживания выполнения привычек"""

    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name='completions',
        verbose_name='Привычка'
    )

    completion_date = models.DateField(
        verbose_name='Дата выполнения'
    )

    is_completed = models.BooleanField(
        default=False,
        verbose_name='Выполнено'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания записи'
    )

    class Meta:
        verbose_name = 'Выполнение привычки'
        verbose_name_plural = 'Выполнения привычек'
        unique_together = ['habit', 'completion_date']
        ordering = ['-completion_date']

    def __str__(self):
        return f"{self.habit.action} - {self.completion_date}"
