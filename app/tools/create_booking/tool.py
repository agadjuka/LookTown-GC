"""
Инструмент CreateBooking для создания записи на услугу
"""
import asyncio
import logging
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.tools.shared.yclients_service import YclientsService
from app.tools.create_booking.logic import create_booking_logic

logger = logging.getLogger(__name__)


class CreateBookingInput(BaseModel):
    """Входные параметры для CreateBooking"""
    service_id: int = Field(
        description="ID услуги (число). Получи из GetServices - каждая услуга имеет формат 'Название (ID: число)'."
    )
    client_name: str = Field(
        description="Имя клиента. Получи из сообщений клиента в диалоге, когда он предоставляет свои данные."
    )
    client_phone: str = Field(
        description="Телефон клиента в любом формате (будет автоматически нормализован). Получи из сообщений клиента в диалоге, когда он предоставляет свои данные."
    )
    datetime: str = Field(
        description="Дата и время записи в формате YYYY-MM-DD HH:MM (например '2025-11-12 14:30') или YYYY-MM-DDTHH:MM. Собери из: дата (когда клиент выбрал дату) и время (когда клиент выбрал конкретное время из доступных слотов BookTimes)."
    )
    master_name: Optional[str] = Field(
        default=None,
        description="Имя мастера (опционально). Получи из BookTimes (если клиент выбирал время у конкретного мастера) или из сообщений клиента (если клиент явно просил записаться к конкретному мастеру). НЕ УКАЗЫВАЙ если клиент не просил конкретного мастера."
    )


@tool(args_schema=CreateBookingInput)
def create_booking_tool(
    service_id: int,
    client_name: str,
    client_phone: str,
    datetime: str,
    master_name: Optional[str] = None
) -> str:
    """
    Создать запись на услугу.
    Используй когда клиент выбрал услугу, дату, время и предоставил свои данные (имя и телефон).
    """
    try:
        # Создаем сервис (он сам возьмет переменные окружения)
        try:
            yclients_service = YclientsService()
        except ValueError as e:
            return f"Ошибка конфигурации: {str(e)}. Проверьте переменные окружения AUTH_HEADER/AuthenticationToken и COMPANY_ID/CompanyID."
        
        # Запускаем async функцию синхронно
        result = asyncio.run(
            create_booking_logic(
                yclients_service=yclients_service,
                service_id=service_id,
                client_name=client_name,
                client_phone=client_phone,
                datetime=datetime,
                master_name=master_name
            )
        )
        
        # Возвращаем сообщение из результата
        return result.get('message', 'Неизвестная ошибка')
        
    except ValueError as e:
        logger.error(f"Ошибка конфигурации CreateBooking: {e}")
        return f"Ошибка конфигурации: {str(e)}"
    except Exception as e:
        logger.error(f"Ошибка при создании записи: {e}", exc_info=True)
        return f"Ошибка при создании записи: {str(e)}"

