import requests
from django.conf import settings


def send_telegram_message(chat_id, message):
    """Функция отправки уведомления в телеграмм"""
    try:

        url = f"{settings.TELEGRAM_URL}{settings.TELEGRAM_TOKEN}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": message,

        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки Telegram сообщения: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return None
