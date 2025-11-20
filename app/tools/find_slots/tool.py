"""
Инструмент FindSlots для поиска слотов по временным признакам
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.tools.shared.yclients_service import YclientsService
from app.tools.find_slots.logic import find_slots_by_period, _format_time_period_display

logger = logging.getLogger(__name__)


class FindSlotsInput(BaseModel):
    """Входные параметры для FindSlots"""
    service_id: int = Field(
        description="ID услуги (число, обязательное поле). Получи из GetServices - каждая услуга имеет формат 'Название (ID: число)'."
    )
    time_period: str = Field(
        description="Период времени (обязательное поле). Поддерживаемые форматы: 'morning' (9:00-11:00), 'day' (11:00-17:00), 'evening' (17:00-22:00); конкретное время '16:00' или '16.00' (окно 30 минут); интервал '16:00-19:00' или '16.00-19.00'; 'before 11:00' (до 11:00); 'after 16:00' (после 16:00). Используй когда клиент просит время в определенный период или интервал."
    )
    master_name: Optional[str] = Field(
        default=None,
        description="Имя мастера (необязательное поле). Заполняй только если клиент хочет записаться к конкретному мастеру. Инструмент найдет мастера по вариациям имени (например, 'Анна' найдет 'Аня', 'Аннушка')."
    )
    master_id: Optional[int] = Field(
        default=None,
        description="ID мастера (необязательное поле). Заполняй только если знаешь точный ID мастера. Если указан master_id, то master_name игнорируется."
    )
    date_range: Optional[str] = Field(
        default=None,
        description="Интервал дат (необязательное поле). Формат: 'YYYY-MM-DD:YYYY-MM-DD' (например, '2025-01-11:2025-01-16'). Заполняй только если клиент указал конкретный интервал дат. Если не указан, инструмент будет искать с текущей даты до 10 дней вперед, пока не найдет 3 дня с доступными слотами."
    )


@tool(args_schema=FindSlotsInput)
def find_slots_tool(
    service_id: int,
    time_period: str,
    master_name: Optional[str] = None,
    master_id: Optional[int] = None,
    date_range: Optional[str] = None
) -> str:
    """
    Найти доступные временные слоты для услуги с фильтрацией по периоду времени.
    Используй когда клиент хочет найти время в определенный период (утром, днем, вечером) 
    или в определенном интервале дат. Этот инструмент более гибкий чем BookTimes - он может 
    искать слоты на несколько дней вперед и фильтровать по времени суток.
    """
    try:
        # Создаем сервис (он сам возьмет переменные окружения)
        try:
            yclients_service = YclientsService()
        except ValueError as e:
            return f"Ошибка конфигурации: {str(e)}. Проверьте переменные окружения AUTH_HEADER/AuthenticationToken и COMPANY_ID/CompanyID."
        
        # Запускаем async функцию синхронно
        result = asyncio.run(
            find_slots_by_period(
                yclients_service=yclients_service,
                service_id=service_id,
                time_period=time_period,
                master_name=master_name,
                master_id=master_id,
                date_range=date_range
            )
        )
        
        # Форматируем результат
        if result.get('error'):
            return f"Ошибка: {result['error']}"
        
        service_title = result.get('service_title', 'Услуга')
        time_period_result = result.get('time_period', '')
        master_name_result = result.get('master_name')
        results = result.get('results', [])
        
        if not results:
            period_display = _format_time_period_display(time_period_result)
            
            if master_name_result:
                if date_range:
                    return f"К сожалению, у мастера {master_name_result} нет свободных слотов {period_display} для услуги '{service_title}' в указанный период."
                else:
                    return f"К сожалению, у мастера {master_name_result} нет свободных слотов {period_display} для услуги '{service_title}' в ближайшие дни."
            else:
                if date_range:
                    return f"К сожалению, нет свободных слотов {period_display} для услуги '{service_title}' в указанный период."
                else:
                    return f"К сожалению, нет свободных слотов {period_display} для услуги '{service_title}' в ближайшие дни."
        
        # Форматируем список результатов по датам
        period_display = _format_time_period_display(time_period_result)
        
        result_lines = []
        if master_name_result:
            result_lines.append(f"Доступные слоты {period_display} у мастера {master_name_result} для услуги '{service_title}':\n")
        else:
            result_lines.append(f"Доступные слоты {period_display} для услуги '{service_title}':\n")
        
        for day_result in results:
            date = day_result['date']
            slots = day_result['slots']
            
            # Форматируем дату для вывода
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d.%m.%Y")
            except:
                formatted_date = date
            
            slots_text = ", ".join(slots)
            result_lines.append(f"  {formatted_date}: {slots_text}")
        
        return "\n".join(result_lines)
        
    except ValueError as e:
        logger.error(f"Ошибка конфигурации FindSlots: {e}")
        return f"Ошибка конфигурации: {str(e)}"
    except Exception as e:
        logger.error(f"Ошибка при поиске слотов: {e}", exc_info=True)
        return f"Ошибка при поиске доступных слотов: {str(e)}"

