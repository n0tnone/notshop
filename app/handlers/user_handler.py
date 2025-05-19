from typing import Callable
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message


user_handler = Router()


@user_handler.message(CommandStart())
async def handle_command_start(message: Message, _: Callable):
    await message.answer(_("welcome", name=message.from_user.username))
