"""Обработчики сообщений для Telegram бота."""

import logging
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes

from app.telegram.service import AgentService

logger = logging.getLogger(__name__)


class MessageHandlers:
    """Класс для обработки сообщений Telegram."""

    def __init__(self, agent_service: AgentService) -> None:
        """Инициализирует обработчики.

        Args:
            agent_service: Сервис для взаимодействия с агентом
        """
        self.agent_service = agent_service

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает текстовое сообщение от пользователя.

        Args:
            update: Обновление от Telegram
            context: Контекст бота
        """
        if not update.message or not update.message.text:
            return

        user_id = update.effective_user.id
        message_text = update.message.text
        chat_id = update.effective_chat.id

        logger.info("Получено сообщение от пользователя %s в чате %s", user_id, chat_id)

        # Отправляем индикатор печати
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        try:
            # Обрабатываем сообщение через агента
            response = await self.agent_service.process_message(
                user_message=message_text,
                user_id=str(user_id),
                bot=context.bot,
                chat_id=chat_id,
                session_id=str(chat_id),
            )

            # Отправляем ответ пользователю только если response не None
            # (если был вызван CallManager, сообщения уже отправлены)
            if response is not None:
                await update.message.reply_text(response)

        except Exception as e:
            logger.error("Ошибка при обработке сообщения: %s", str(e), exc_info=True)
            error_message = "Произошла ошибка при обработке вашего сообщения. Попробуйте позже."
            await update.message.reply_text(error_message)

    async def handle_error(self, update: Update | None, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает ошибки бота.

        Args:
            update: Обновление от Telegram (может быть None)
            context: Контекст бота
        """
        logger.error("Ошибка в обработчике: %s", context.error, exc_info=True)

        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "Произошла ошибка при обработке вашего сообщения. Попробуйте позже."
                )
            except Exception as e:
                logger.error("Не удалось отправить сообщение об ошибке: %s", str(e))

