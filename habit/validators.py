import datetime

from rest_framework.serializers import ValidationError


def validate_duration(value):
    """Валидация времени выполнения (максимум 120 секунд)"""
    if value > 120:
        raise ValidationError("Время выполнения не должно превышать 120 секунд")
    return value


def validate_related_habit_and_reward(data):
    """Валидация: нельзя одновременно указывать связанную привычку и вознаграждение"""
    related_habit = data.get("related_habit")
    reward = data.get("reward")

    if related_habit and reward:
        raise ValidationError(
            "Нельзя одновременно указывать связанную привычку и вознаграждение"
        )
    return data


def validate_pleasant_habit(data):
    """Валидация приятной привычки"""
    is_pleasant = data.get("is_pleasant", False)

    if is_pleasant:
        related_habit = data.get("related_habit")
        reward = data.get("reward")

        if related_habit or reward:
            raise ValidationError(
                "Приятная привычка не может иметь связанную привычку или вознаграждение"
            )
    return data


def validate_related_habit_is_pleasant(data):
    """Валидация: связанная привычка должна быть приятной"""
    related_habit = data.get("related_habit")

    if related_habit and not related_habit.is_pleasant:
        raise ValidationError("Связанная привычка должна быть приятной")
    return data


def validate_periodicity(value):
    """Валидация периодичности выполнения привычки"""
    if value < 1:
        raise ValidationError("Периодичность должна быть не менее 1 дня")
    if value > 7:
        raise ValidationError("Нельзя выполнять привычку реже, чем 1 раз в 7 дней")
    return value


def validate_habit_consistency(habit_instance):
    """Валидация: нельзя не выполнять привычку более 7 дней.
    Проверяет, что привычка выполняется хотя бы раз в неделю"""
    from .models import HabitCompletion

    week_ago = datetime.now().date() - datetime.timedelta(days=7)

    recent_completions = HabitCompletion.objects.filter(
        habit=habit_instance, completion_date__gte=week_ago, is_completed=True
    ).exists()

    if habit_instance.created_at.date() < week_ago and not recent_completions:
        raise ValidationError(
            "Нельзя не выполнять привычку более 7 дней. "
            "Привычка должна выполняться хотя бы раз в неделю."
        )


def validate_habit_frequency(periodicity, last_completion_date):
    """Валидация частоты выполнения привычки.
    Проверяет, что привычка выполняется не реже, чем указано в периодичности"""
    if not last_completion_date:
        return True

    days_since_last_completion = (datetime.now().date() - last_completion_date).days

    if days_since_last_completion > periodicity:
        raise ValidationError(
            f"Привычка должна выполняться раз в {periodicity} день(дня/дней). "
            f"Последнее выполнение было {days_since_last_completion} дней назад."
        )

    return True


def validate_habit_creation(data, user):
    """Комплексная валидация при создании привычки"""
    from .models import Habit

    if data.get("is_pleasant", False) and data.get("related_habit"):
        raise ValidationError("Приятная привычка не может быть связанной привычкой")

    if Habit.objects.filter(
        user=user,
        action=data.get("action"),
        time=data.get("time"),
        place=data.get("place"),
    ).exists():
        raise ValidationError(
            "У вас уже есть такая привычка с таким же временем и местом"
        )

    max_habits = 50
    if Habit.objects.filter(user=user).count() >= max_habits:
        raise ValidationError(f"Максимальное количество привычек: {max_habits}")

    return data


def validate_habit_update(data, instance):
    """Валидация при обновлении привычки"""

    if (
        "is_pleasant" in data
        and data["is_pleasant"] is False
        and instance.is_pleasant is True
    ):
        from .models import Habit

        if Habit.objects.filter(related_habit=instance).exists():
            raise ValidationError(
                "Нельзя изменить приятную привычку на полезную, "
                "так как она используется как связанная привычка в других привычках"
            )

    return data


def validate_habit_completion(habit, completion_date=None):
    """Валидация при отметке выполнения привычки"""
    from django.utils import timezone

    if not completion_date:
        completion_date = timezone.now().date()

    from .models import HabitCompletion

    last_completion = (
        HabitCompletion.objects.filter(habit=habit, is_completed=True)
        .order_by("-completion_date")
        .first()
    )

    if last_completion:
        days_since_last = (completion_date - last_completion.completion_date).days
        if days_since_last < habit.periodicity:
            raise ValidationError(
                f"Привычку можно выполнять раз в {habit.periodicity} день(дня/дней). "
                f"Последний раз вы выполняли её {days_since_last} дней назад."
            )

    if completion_date > timezone.now().date():
        raise ValidationError("Нельзя отметить выполнение привычки на будущую дату")

    if completion_date < habit.created_at.date():
        raise ValidationError(
            f"Нельзя отметить выполнение привычки раньше даты её создания "
            f"({habit.created_at.date()})"
        )

    return True
