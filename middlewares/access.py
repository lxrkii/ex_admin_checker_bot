from aiogram import BaseMiddleware
from config import ALLOWED_USERS

class AccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if user and user.id not in ALLOWED_USERS:
            return 
        return await handler(event, data)