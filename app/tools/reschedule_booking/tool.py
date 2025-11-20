"""
Инструмент RescheduleBooking для переноса записи клиента на другое время
"""
import asyncio
import logging
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.tools.shared.yclients_service import YclientsService
from app.tools.reschedule_booking.logic import reschedule_booking_logic

logger = logging.getLogger(__name__)


class RescheduleBookingInput(BaseModel):
    """Входные параметры для RescheduleBooking"""
    record_id: int = Field(
        description="ID записи (число). Получи из GetClientRecords - каждая запись содержит эти данные."
    )
    datetime: str = Field(
        description="Новое дата и время в формате YYYY-MM-DD HH:MM (например '2025-11-12 14:30') или YYYY-MM-DDTHH:MM"
    )
    staff_id: int = Field(
        description="ID мастера (число). Получи из GetClientRecords - каждая запись содержит эти данные."
    )
    service_id: int = Field(
        description="ID услуги (число). Получи из GetClientRecords - каждая запись содержит эти данные."
    )
    client_id: int = Field(
        description="ID клиента (число). Получи из GetClientRecords - каждая запись содержит эти данные."
    )
    seance_length: int = Field(
        description="Продолжительность сеанса в секундах (число). Получи из GetClientRecords - каждая запись содержит эти данные."
    )
    save_if_busy: Optional[bool] = Field(
        default=False,
        description="Сохранить запись даже если слот занят (по умолчанию False). Обычно не используй."
    )


@tool(args_schema=RescheduleBookingInput)
def reschedule_booking_tool(
    record_id: int,
    datetime: str,
    staff_id: int,
    service_id: int,
    client_id: int,
    seance_length: int,
    save_if_busy: Optional[bool] = False
) -> str:
    """
    Перенести запись клиента на новое время.
    Используй когда клиент просит перенести запись на другое время или дату.
    record_id, staff_id, service_id, client_id и seance_length получай из GetClientRecords - каждая запись содержит эти данные.
    datetime в формате YYYY-MM-DD HH:MM (например "2025-11-12 14:30") или YYYY-MM-DDTHH:MM.
    """
    try:
        # Создаем сервис (он сам возьмет переменные окружения)
        try:
            yclients_service = YclientsService()
        except ValueError as e:
            return f"Ошибка конфигурации: {str(e)}. Проверьте переменные окружения AUTH_HEADER/AuthenticationToken и COMPANY_ID/CompanyID."
        
        # Запускаем async функцию синхронно
        result = asyncio.run(
            reschedule_booking_logic(
                yclients_service=yclients_service,
                record_id=record_id,
                datetime=datetime,
                staff_id=staff_id,
                service_id=service_id,
                client_id=client_id,
                seance_length=seance_length,
                save_if_busy=save_if_busy if save_if_busy is not None else False
            )
        )
        
        # Проверяем результат
        if result.get('success'):
            # Возвращаем мягкое сообщение об успешном переносе
            return result.get('message', 'Запись успешно перенесена')
        else:
            error = result.get('error', 'Неизвестная ошибка')
            return f"Ошибка: {error}"
        
    except ValueError as e:
        logger.error(f"Ошибка конфигурации RescheduleBooking: {e}")
        return f"Ошибка конфигурации: {str(e)}"
    except Exception as e:
        logger.error(f"Ошибка при переносе записи: {e}", exc_info=True)
        return f"Ошибка при переносе записи: {str(e)}"







