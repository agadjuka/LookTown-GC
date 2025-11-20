#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска Telegram бота в режиме polling.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Настройка логирования с компактным форматом
class CompactFormatter(logging.Formatter):
    """Компактный форматтер."""
    
    def format(self, record):
        # Получаем короткое имя модуля (последняя часть пути)
        name_parts = record.name.split(".")
        short_name = name_parts[-1] if name_parts else record.name
        
        # Компактный формат: время | модуль | сообщение
        record.msg = f"{short_name} | {record.msg}"
        return super().format(record)

# Настройка логирования
handler = logging.StreamHandler()
handler.setFormatter(CompactFormatter(
    fmt="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S",
))
logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
    force=True
)

# Отключаем логи от внешних библиотек
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)
logging.getLogger("google.api_core").setLevel(logging.WARNING)
logging.getLogger("google.cloud").setLevel(logging.WARNING)
logging.getLogger("google.cloud.aiplatform").setLevel(logging.WARNING)
logging.getLogger("numexpr").setLevel(logging.WARNING)
logging.getLogger("numexpr.utils").setLevel(logging.WARNING)
logging.getLogger("traceloop").setLevel(logging.WARNING)
logging.getLogger("opentelemetry").setLevel(logging.ERROR)
logging.getLogger("opentelemetry.exporter.cloud_trace").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Главная функция для запуска бота."""
    # Переходим в папку скрипта
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Загружаем переменные из .env файла
    env_path = script_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        logger.warning(f"Файл .env не найден в {script_dir}")

    # Устанавливаем PYTHONPATH
    os.environ["PYTHONPATH"] = str(script_dir)

    # Получаем токен из переменной окружения
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error(
            "Токен Telegram бота не найден. "
            "Установите переменную окружения TELEGRAM_BOT_TOKEN"
        )
        sys.exit(1)

    # Импортируем бота
    from app.telegram.bot import TelegramBot

    # Создаем и запускаем бота
    logger.info("Telegram бот загружается...")
    bot = TelegramBot(token=token)
    try:
        await bot.start_polling()
        # Ожидаем бесконечно, пока бот работает
        stop_event = asyncio.Event()
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        await bot.stop()


if __name__ == "__main__":
    # Проверяем, что мы используем правильное окружение
    import sys
    if "uv" not in sys.executable.lower() and "venv" not in sys.executable.lower():
        print("=" * 80)
        print("ВНИМАНИЕ: Запускайте через 'uv run python start_telegram_bot.py'")
        print("=" * 80)
        print()
    
    asyncio.run(main())

