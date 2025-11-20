"""
Инструмент Masters для получения информации о мастерах салона
"""
import json
import logging
from langchain_core.tools import tool
from app.tools.shared.masters_data_loader import _masters_data_loader

logger = logging.getLogger(__name__)


@tool
def masters_tool() -> str:
    """
    Получить полную информацию о мастерах салона.
    Используй когда клиент спрашивает "какие у вас мастера?", "расскажите про мастеров", "кто работает в салоне" или подобные вопросы о мастерах.
    
    Returns:
        Полное содержимое файла masters.json в читаемом формате
    """
    try:
        data = _masters_data_loader.load_data()
        
        if not data:
            return "Информация о мастерах не найдена"
        
        # Возвращаем полное содержимое JSON в читаемом формате
        return json.dumps(data, ensure_ascii=False, indent=2)
        
    except FileNotFoundError as e:
        logger.error(f"Файл с информацией о мастерах не найден: {e}")
        return "Файл с информацией о мастерах не найден"
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON: {e}")
        return "Ошибка при чтении информации о мастерах"
    except Exception as e:
        logger.error(f"Ошибка при получении информации о мастерах: {e}")
        return f"Ошибка при получении информации о мастерах: {str(e)}"

