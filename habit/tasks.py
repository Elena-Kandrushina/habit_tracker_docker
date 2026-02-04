from datetime import time

from celery import shared_task
from django.utils import timezone

from habit.models import Habit
from habit.services import send_telegram_message


@shared_task
def send_habit_reminders():
    """Отправка напоминаний о привычках.
    Задача запускается периодически и проверяет,
    какие привычки нужно выполнить через 5 минут"""

    now = timezone.localtime(timezone.now())

    reminder_time = add_minutes(now.time(), 5)

    habits = Habit.objects.filter(
        time__hour=reminder_time.hour,
        time__minute=reminder_time.minute,
        user__chat_id__isnull=False
    )

    for habit in habits:
        send_reminder(habit)


def add_minutes(time_obj, minutes):
    """Добавляет минуты к времени."""
    total_minutes = time_obj.hour * 60 + time_obj.minute + minutes
    return time(hour=total_minutes // 60 % 24, minute=total_minutes % 60)


def send_reminder(habit):
    """Отправляет напоминание о привычке в Telegram."""
    message = f"Напоминание: {habit.action} в {habit.time.strftime('%H:%M')} в {habit.place}"
    send_telegram_message(habit.user.chat_id, message)
