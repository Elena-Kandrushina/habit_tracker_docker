# Проект "Трекер привычек"

## Описание:
- Создание полезных и приятных привычек
- Настройка периодичности выполнения (от 1 до 7 дней)
- Указание места и времени выполнения
- Награды за выполнение полезных привычек
- Связывание полезных привычек с приятными
- Публичные привычки для общего доступа
- Автоматические напоминания в Telegram
- Напоминания за 5 минут до времени выполнения
- Интеграция с Celery для периодических задач
- Поддержка Redis как брокера сообщений
- Кастомная модель пользователя с email вместо username
- JWT аутентификация

## Тестирование:
```
coverage run --source='.' manage.py test
```
подсчет покрытия и вывести отчет:
```
coverage report
```
для сохранения отчета в htmlcov:
```
coverage html
```
Покрытие составляет:
```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
config\__init__.py                          2      0   100%
config\asgi.py                              4      4     0%
config\celery.py                            6      0   100%
config\settings.py                         42      0   100%
config\urls.py                             13      0   100%
config\wsgi.py                              4      4     0%
habit\__init__.py                           0      0   100%
habit\admin.py                             23      2    91%
habit\apps.py                               4      0   100%
habit\migrations\0001_initial.py            7      0   100%
habit\migrations\0002_initial.py            7      0   100%
habit\migrations\__init__.py                0      0   100%
habit\models.py                            35      2    94%
habit\pagination.py                         5      0   100%
habit\permissions.py                       14      4    71%
habit\serializers.py                       53      9    83%
habit\services.py                          15     15     0%
habit\tasks.py                             18     18     0%
habit\tests.py                             99      0   100%
habit\urls.py                               7      0   100%
habit\validators.py                        75     43    43%
habit\views.py                             23      0   100%
manage.py                                  11      2    82%
users\__init__.py                           0      0   100%
users\admin.py                             13      0   100%
users\apps.py                               4      0   100%
users\migrations\0001_initial.py            6      0   100%
users\migrations\0002_user_chat_id.py       4      0   100%
users\migrations\__init__.py                0      0   100%
users\models.py                            36      2    94%
users\serializers.py                       51      1    98%
users\tests.py                            147      0   100%
users\urls.py                               6      0   100%
users\views.py                             26      0   100%
-----------------------------------------------------------
TOTAL                                     760    106    86%
```

## Установка:

1. Клонируйте репозиторий:
```
git@github.com:Elena-Kandrushina/habit_tracker_docker.git
```

2. Установите зависимости:
```
poetry install
```
Проект использует GitHub Actions для автоматизации:

Линтинг: Flake8, isort проверка

Тестирование: Django tests с PostgreSQL и Redis

Сборка Docker: Тестирование Docker конфигурации

Деплой: Автоматический деплой на сервер при пуше в develop

## Документация:

Дополнительную информацию о структуре проекта можно найти в [документации](docs/README.md).

## Лицензия:

Проект распространяется под [лицензией MIT](LICENSE).