from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Habit, HabitCompletion
from .validators import (
    validate_duration,
    validate_related_habit_and_reward,
    validate_pleasant_habit,
    validate_related_habit_is_pleasant,
    validate_periodicity,
    validate_habit_creation,
    validate_habit_update,
)


class HabitCompletionSerializer(serializers.ModelSerializer):
    """Сериализатор для выполнения привычки"""

    class Meta:
        model = HabitCompletion
        fields = ("id", "habit", "completion_date", "is_completed", "created_at")
        read_only_fields = ("id", "created_at")

    def validate(self, data):
        """Валидация выполнения привычки"""
        from .validators import validate_habit_completion

        habit = data.get("habit") or (self.instance.habit if self.instance else None)

        if habit:
            validate_habit_completion(habit, data.get("completion_date"))

        return data


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычки"""

    user = serializers.SlugRelatedField(slug_field="email", read_only=True)
    related_habit = serializers.PrimaryKeyRelatedField(
        queryset=Habit.objects.filter(is_pleasant=True), required=False, allow_null=True
    )
    completions = HabitCompletionSerializer(many=True, read_only=True)

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
            "created_at",
            "updated_at",
            "completions",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")

    def validate(self, data):
        """Общая валидация привычки"""

        data = validate_related_habit_and_reward(data)
        data = validate_pleasant_habit(data)

        if "related_habit" in data and data["related_habit"]:
            validate_related_habit_is_pleasant(data)

        periodicity = data.get("periodicity")
        if periodicity:
            validate_periodicity(periodicity)

        periodicity = data.get("periodicity")
        if periodicity and periodicity > 7:
            raise ValidationError("Нельзя выполнять привычку реже, чем 1 раз в 7 дней")

        return data

    def validate_duration(self, value):
        """Валидация времени выполнения"""
        return validate_duration(value)

    def validate_periodicity(self, value):
        """Валидация периодичности"""
        return validate_periodicity(value)

    def create(self, validated_data):
        """Создание привычки с дополнительной валидацией"""
        user = self.context["request"].user

        validated_data = validate_habit_creation(validated_data, user)

        validated_data["user"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Обновление привычки с дополнительной валидацией"""
        validated_data = validate_habit_update(validated_data, instance)
        return super().update(instance, validated_data)


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных привычек (только для чтения)"""

    user = serializers.SlugRelatedField(slug_field="email", read_only=True)

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "periodicity",
            "duration",
            "created_at",
        )
        read_only_fields = fields
