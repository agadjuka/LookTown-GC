"""
Инструмент GetCategories для получения списка категорий услуг
"""
import json
import logging
from pathlib import Path
from langchain_core.tools import tool
from app.tools.shared.services_data_loader import _data_loader

logger = logging.getLogger(__name__)


@tool
def get_categories_tool() -> str:
    """
    Получить список всех категорий услуг с их ID.
    Используй когда клиент спрашивает "какие у вас есть услуги?" или "что вы предлагаете?"
    
    Returns:
        Отформатированный список категорий с ID
    """
    try:
        data = _data_loader.load_data()
        
        if not data:
            return "Категории услуг не найдены"
        
        categories = []
        for cat_id, cat_data in sorted(data.items(), key=lambda x: int(x[0])):
            category_name = cat_data.get('category_name', 'Неизвестно')
            categories.append(f"{cat_id}. {category_name}")
        
        result = "Доступные категории услуг:\n\n" + "\n".join(categories)
        result += "\n\nДля получения услуг категории используйте GetServices с указанием ID категории."
        
        return result
        
    except FileNotFoundError as e:
        logger.error(f"Файл с услугами не найден: {e}")
        return "Файл с данными об услугах не найден"
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON: {e}")
        return "Ошибка при чтении данных об услугах"
    except Exception as e:
        logger.error(f"Ошибка при получении категорий: {e}")
        return f"Ошибка при получении категорий: {str(e)}"

