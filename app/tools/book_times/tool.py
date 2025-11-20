"""
Инструмент BookTimes для поиска доступных временных слотов
"""
import asyncio
import logging
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.tools.shared.yclients_service import YclientsService
from app.tools.book_times.logic import find_best_slots

logger = logging.getLogger(__name__)


class BookTimesInput(BaseModel):
    """Входные параметры для BookTimes"""
    service_id: int = Field(
        description="ID услуги (число, ОБЯЗАТЕЛЬНО). Получи ID через инструмент GetServices - сначала вызови GetServices с category_id, чтобы получить список услуг. Каждая услуга в ответе GetServices имеет формат 'Название (ID: число)' - извлеки это число и используй как service_id. НЕ придумывай ID, НЕ используй случайные значения или строки. ID можно получить ТОЛЬКО через GetServices."
    )
    date: str = Field(
        description="Дата в формате YYYY-MM-DD (например '2025-11-12'). Преобразуй относительные даты ('сегодня', 'завтра') в этот формат."
    )
    master_name: Optional[str] = Field(
        default=None,
        description="Имя мастера (опционально). Если указано - слоты только у этого мастера. Игнорируется если указан staff_id."
    )
    staff_id: Optional[int] = Field(
        default=None,
        description="ID мастера (опционально). Если указан - слоты только у этого мастера. Имеет приоритет над master_name."
    )


@tool(args_schema=BookTimesInput)
def book_times_tool(
    service_id: int,
    date: str,
    master_name: Optional[str] = None,
    staff_id: Optional[int] = None
) -> str:
    """
    Найти доступные временные слоты для записи на услугу.
    Используй когда клиент выбрал услугу и дату - нужно найти свободное время.
    
    ВАЖНО: Перед использованием этого инструмента ОБЯЗАТЕЛЬНО используй GetServices, чтобы получить service_id. 
    service_id - это число, которое указано в формате 'Название услуги (ID: число)' в ответе GetServices.
    НЕ придумывай service_id, НЕ используй случайные значения или строки.
    
    date в формате YYYY-MM-DD (например "2025-11-12").
    """
    try:
        # Создаем сервис (он сам возьмет переменные окружения)
        try:
            yclients_service = YclientsService()
        except ValueError as e:
            return f"Ошибка конфигурации: {str(e)}. Проверьте переменные окружения AUTH_HEADER/AuthenticationToken и COMPANY_ID/CompanyID."
        
        # Запускаем async функцию синхронно
        result = asyncio.run(
            find_best_slots(
                yclients_service=yclients_service,
                service_id=service_id,
                date=date,
                master_name=master_name,
                staff_id=staff_id
            )
        )
        
        # Форматируем результат
        if result.get('error'):
            return f"Ошибка: {result['error']}"
        
        service_title = result.get('service_title', 'Услуга')
        master_name_result = result.get('master_name')
        slots = result.get('slots', [])
        
        if not slots:
            if master_name_result:
                return f"К сожалению, на {date} у мастера {master_name_result} нет свободных слотов для услуги '{service_title}'."
            else:
                return f"К сожалению, на {date} нет свободных слотов для услуги '{service_title}'."
        
        # Форматируем список слотов
        slots_text = "\n".join([f"  • {slot}" for slot in slots])
        
        result_text = f"Доступные временные слоты для услуги '{service_title}' на {date}:\n\n{slots_text}"
        
        if master_name_result:
            result_text = f"Доступные временные слоты у мастера {master_name_result} для услуги '{service_title}' на {date}:\n\n{slots_text}"
        
        return result_text
        
    except ValueError as e:
        logger.error(f"Ошибка конфигурации BookTimes: {e}")
        return f"Ошибка конфигурации: {str(e)}"
    except Exception as e:
        logger.error(f"Ошибка при поиске слотов: {e}", exc_info=True)
        return f"Ошибка при поиске доступных слотов: {str(e)}"

