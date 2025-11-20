"""
Инструмент FindMasterByService для поиска мастера по имени и услуге
"""
import asyncio
import logging
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.tools.shared.yclients_service import YclientsService
from app.tools.find_master_by_service.logic import find_master_by_service_logic

logger = logging.getLogger(__name__)


class FindMasterByServiceInput(BaseModel):
    """Входные параметры для FindMasterByService"""
    master_name: str = Field(
        description="Имя мастера для поиска. Может быть неточным - поддерживается поиск по вариантам имени (например, 'Анна' найдет 'Аня', 'Аннушка')."
    )
    service_name: str = Field(
        description="Название услуги для поиска. Может быть неточным - поддерживается поиск по ключевым словам и категориям услуг (например, 'маникюр', 'массаж', 'брови')."
    )


@tool(args_schema=FindMasterByServiceInput)
def find_master_by_service_tool(master_name: str, service_name: str) -> str:
    """
    Найти мастера по имени и услуге.
    Используй когда нужно найти конкретного мастера, который оказывает определенную услугу.
    Поддерживает неточный поиск по имени (варианты имен) и по услуге (ключевые слова, категории).
    """
    try:
        # Создаем сервис (он сам возьмет переменные окружения)
        try:
            yclients_service = YclientsService()
        except ValueError as e:
            return f"Ошибка конфигурации: {str(e)}. Проверьте переменные окружения AUTH_HEADER/AuthenticationToken и COMPANY_ID/CompanyID."
        
        # Запускаем async функцию синхронно
        result = asyncio.run(
            find_master_by_service_logic(
                yclients_service=yclients_service,
                master_name=master_name,
                service_name=service_name
            )
        )
        
        # Форматируем результат
        if not result.get('success'):
            error = result.get('error', 'Неизвестная ошибка')
            return f"Ошибка: {error}"
        
        master = result.get('master', {})
        services = result.get('services', [])
        
        # Формируем отформатированный ответ
        result_lines = []
        
        # Информация о мастере
        master_name_result = master.get('name', 'Неизвестно')
        master_id = master.get('id')
        position_title = master.get('position_title', '')
        
        result_lines.append(f"Найден мастер: {master_name_result}")
        if position_title:
            result_lines.append(f"Должность: {position_title}")
        if master_id:
            result_lines.append(f"ID мастера: {master_id}")
        
        # Список услуг
        if services:
            result_lines.append(f"\nУслуги мастера:")
            for service in services:
                service_title = service.get('title', 'Неизвестно')
                service_id = service.get('id')
                duration_sec = service.get('duration', 0)
                duration_min = duration_sec // 60 if duration_sec else 0
                
                service_line = f"- {service_title}"
                if service_id:
                    service_line += f" (ID: {service_id})"
                if duration_min:
                    service_line += f" - {duration_min} мин"
                result_lines.append(service_line)
        else:
            result_lines.append("\nУслуги не найдены")
        
        return "\n".join(result_lines)
        
    except ValueError as e:
        logger.error(f"Ошибка конфигурации FindMasterByService: {e}")
        return f"Ошибка конфигурации: {str(e)}"
    except Exception as e:
        logger.error(f"Ошибка при поиске мастера: {e}", exc_info=True)
        return f"Ошибка при поиске мастера: {str(e)}"







