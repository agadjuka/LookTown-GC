"""
Инструмент ViewService для получения детальной информации об услуге
"""
import asyncio
import logging
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.tools.shared.yclients_service import YclientsService
from app.tools.view_service.logic import view_service_logic

logger = logging.getLogger(__name__)


class ViewServiceInput(BaseModel):
    """Входные параметры для ViewService"""
    service_id: int = Field(
        description="ID услуги (число). Получи из GetServices - каждая услуга имеет формат 'Название (ID: число)'."
    )


@tool(args_schema=ViewServiceInput)
def view_service_tool(service_id: int) -> str:
    """
    Получить детальную информацию об услуге по её ID.
    Используй когда нужно узнать подробности об услуге: название, цену, продолжительность, список мастеров.
    service_id получай из GetServices (каждая услуга имеет ID: число).
    """
    try:
        # Создаем сервис (он сам возьмет переменные окружения)
        try:
            yclients_service = YclientsService()
        except ValueError as e:
            return f"Ошибка конфигурации: {str(e)}. Проверьте переменные окружения AUTH_HEADER/AuthenticationToken и COMPANY_ID/CompanyID."
        
        # Запускаем async функцию синхронно
        result = asyncio.run(
            view_service_logic(
                yclients_service=yclients_service,
                service_id=service_id
            )
        )
        
        # Форматируем результат
        if not result.get('success'):
            error = result.get('error', 'Неизвестная ошибка')
            message = result.get('message', '')
            status = result.get('status')
            
            if error == 'bad_service_id':
                return f"Ошибка: {message}"
            elif error == 'yclients_http_error':
                return f"Ошибка при обращении к API Yclients (HTTP {status}): {message}"
            else:
                if message:
                    return f"Ошибка: {error}. {message}"
                return f"Ошибка: {error}"
        
        service = result.get('service', {})
        
        # Формируем отформатированный ответ
        result_lines = []
        
        # Название услуги
        title = service.get('title', 'Неизвестно')
        result_lines.append(f"Услуга: {title}")
        
        # Продолжительность
        duration_sec = service.get('duration_sec')
        if duration_sec:
            duration_min = duration_sec // 60
            result_lines.append(f"Продолжительность: {duration_min} минут")
        
        # Цена
        price_min = service.get('price_min')
        price_max = service.get('price_max')
        if price_min or price_max:
            if price_min == price_max:
                result_lines.append(f"Цена: {price_min} руб.")
            else:
                result_lines.append(f"Цена: {price_min or 'от'} - {price_max or 'до'} руб.")
        
        # Комментарий
        comment = service.get('comment')
        if comment:
            result_lines.append(f"\nОписание:\n{comment}")
        
        # Мастера
        staff = service.get('staff', [])
        if staff:
            result_lines.append(f"\nУслугу оказывают мастера:")
            for master in staff:
                master_name = master.get('name', 'Неизвестно')
                result_lines.append(f"- {master_name}")
        else:
            result_lines.append("\nМастера не найдены")
        
        return "\n".join(result_lines)
        
    except ValueError as e:
        logger.error(f"Ошибка конфигурации ViewService: {e}")
        return f"Ошибка конфигурации: {str(e)}"
    except Exception as e:
        logger.error(f"Ошибка при получении информации об услуге: {e}", exc_info=True)
        return f"Ошибка при получении информации об услуге: {str(e)}"

