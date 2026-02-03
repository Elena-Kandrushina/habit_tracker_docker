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

Деплой: Автоматический деплой на сервер при пуше.

## Запуск проекта через Docker Compose
## Отредактируйте файл .env и заполните минимальные настройки:
```
SECRET_KEY=ваш-секретный-ключ
DEBUG=True
NAME=habit_tracker
USER=postgres
PASSWORD=ваш-пароль
HOST=db
PORT=5432
TELEGRAM_TOKEN=ваш-телеграм-токен
```
## Основная команда для запуска:
```
docker-compose up -d
```
## Проверка статуса запуска:
```
docker-compose ps
```
## Проверка работоспособности каждого сервиса:
Проверка бэкенда (Django):
откройте в браузере: http://localhost:8000
Проверка логов бэкенда:
```
docker-compose logs --tail=10 web
```
Создание суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```
## Проверка базы данных:
```
docker-compose exec db psql -U postgres -d habit_tracker -c "SELECT version();"
```
## Проверка Redis:
```
docker-compose exec redis redis-cli ping
```
## Проверка Celery Worker(логи):
```
docker-compose logs --tail=10 celery
```
## Проверка Celery Beat (вывод логов):
```
docker-compose logs --tail=10 celery-beat
```

## Настройка сервера:
Установите Docker и Docker Compose
```
sudo apt-get update
sudo apt-get install docker.io docker-compose
```
## CI/CD с GitHub Actions
Добавьте следующие секреты:
SERVER_HOST, SERVER_USER, SSH_PRIVATE_KEY, SECRET_KEY
При каждом push в любую ветку запускаются тесты, после успешных тестов происходит деплой

# Просмотр логов

```
docker-compose logs
```
# Отдельные сервисы
```
docker-compose logs web
docker-compose logs nginx
docker-compose logs db
docker-compose logs redis
```
# Приложение доступно по адресу:
```
http://89.169.180.227/
```
админка:
```
http://89.169.180.227/admin/
```
# Вывод документации для проекта  
```
http://89.169.180.227/swagger/
```
или 
```
http://89.169.180.227/redoc/
```


## Документация:

Дополнительную информацию о структуре проекта можно найти в [документации](docs/README.md).

## Лицензия:

Проект распространяется под [лицензией MIT](LICENSE).