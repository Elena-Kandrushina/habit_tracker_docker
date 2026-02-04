from django.contrib import admin

from .models import Habit, HabitCompletion


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """Админка для привычек"""

    list_display = ('id', 'user_email', 'action', 'place', 'time',
                    'is_pleasant', 'is_public', 'periodicity', 'created_at')
    list_filter = ('is_pleasant', 'is_public', 'periodicity', 'created_at')
    search_fields = ('action', 'place', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Пользователь'

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'action', 'place', 'time')
        }),
        ('Настройки привычки', {
            'fields': ('is_pleasant', 'related_habit', 'periodicity', 'reward', 'duration')
        }),
        ('Дополнительно', {
            'fields': ('is_public', 'created_at', 'updated_at')
        }),
    )


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    """Админка для выполнения привычек"""

    list_display = ('id', 'habit_action', 'completion_date', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'completion_date', 'created_at')
    search_fields = ('habit__action', 'habit__user__email')
    readonly_fields = ('created_at',)
    list_per_page = 20

    def habit_action(self, obj):
        return obj.habit.action

    habit_action.short_description = 'Привычка'
