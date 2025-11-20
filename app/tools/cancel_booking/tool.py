"""
Инструмент CancelBooking для отмены записи клиента
"""
import asyncio
import logging
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.tools.shared.yclients_service import YclientsService
from app.tools.cancel_booking.logic import cancel_booking_logic

logger = logging.getLogger(__name__)


class CancelBookingInput(BaseModel):
    """Входные параметры для CancelBooking"""
    record_id: int = Field(
        description="ID записи (число). Получи из GetClientRecords - каждая запись имеет ID записи."
    )


@tool(args_schema=CancelBookingInput)
def cancel_booking_tool(record_id: int) -> str:
    """
    Отменить запись клиента по ID записи.
    Используй когда клиент просит отменить запись или перенести её.
    record_id получай из GetClientRecords - каждая запись имеет ID записи.
    """
    try:
        # Создаем сервис (он сам возьмет переменные окружения)
        try:
            yclients_service = YclientsService()
        except ValueError as e:
            return f"Ошибка конфигурации: {str(e)}. Проверьте переменные окружения AUTH_HEADER/AuthenticationToken и COMPANY_ID/CompanyID."
        
        # Запускаем async функцию синхронно
        result = asyncio.run(
            cancel_booking_logic(
                yclients_service=yclients_service,
                record_id=record_id
            )
        )
        
        # Проверяем результат
        if result.get('success'):
            # Возвращаем мягкое сообщение об успешной отмене
            return result.get('message', 'Запись успешно отменена')
        else:
            error = result.get('error', 'Неизвестная ошибка')
            return f"Ошибка: {error}"
        
    except ValueError as e:
        logger.error(f"Ошибка конфигурации CancelBooking: {e}")
        return f"Ошибка конфигурации: {str(e)}"
    except Exception as e:
        logger.error(f"Ошибка при отмене записи: {e}", exc_info=True)
        return f"Ошибка при отмене записи: {str(e)}"







