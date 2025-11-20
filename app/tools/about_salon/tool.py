"""
Инструмент AboutSalon для получения информации о салоне
"""
import json
import logging
from langchain_core.tools import tool
from app.tools.shared.about_salon_data_loader import _about_salon_data_loader

logger = logging.getLogger(__name__)


@tool
def about_salon_tool() -> str:
    """
    Получить полную информацию о салоне.
    Используй когда клиент спрашивает "расскажите о салоне", "что такое LookTown", "где вы находитесь" или подобные вопросы о салоне.
    
    Returns:
        Полный текст информации о салоне
    """
    try:
        data = _about_salon_data_loader.load_data()
        
        if not data:
            return "Информация о салоне не найдена"
        
        text = data.get('text', '')
        
        if not text:
            return "Информация о салоне пуста"
        
        return text
        
    except FileNotFoundError as e:
        logger.error(f"Файл с информацией о салоне не найден: {e}")
        return "Файл с информацией о салоне не найден"
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON: {e}")
        return "Ошибка при чтении информации о салоне"
    except Exception as e:
        logger.error(f"Ошибка при получении информации о салоне: {e}")
        return f"Ошибка при получении информации о салоне: {str(e)}"

