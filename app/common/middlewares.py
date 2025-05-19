from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable

from app.services.language_service import get_text


class LanguageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get('event_from_user')
        user_lang = "ru"

        if user:
            # user_lang = await get_user_language_from_db(user.id)
            user_lang = getattr(user, 'language_code', "ru")
            # state_data = await data['state'].get_data()
            # user_lang = state_data.get("user_language", "ru")

        def _(text_key: str, **kwargs) -> str:
            return get_text(text_key, lang=user_lang, **kwargs)

        data['_'] = _
        data['user_lang'] = user_lang

        return await handler(event, data)
