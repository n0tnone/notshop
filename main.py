import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app import config
from app.common.middlewares import LanguageMiddleware
from app.handlers.user_handler import user_handler
from app.services.language_service import load_translations
from app.services.logger_service import setup_logging
from colorama import Fore, Style, init as colorama_init


bot = Bot(token=config.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

def init() -> None:
    colorama_init()
    print_ascii_art()
    setup_logging(console_level=logging.DEBUG)
    load_translations() # Загружаем переводы
    asyncio.run(run_telebot()) # Запускаем бота

async def run_telebot():
    dp.update.middleware(LanguageMiddleware()) # Регистрируем middleware
    dp.include_router(user_handler) # Регистрируем хэндлеры
    await dp.start_polling(bot) # Запускаем бота

def print_ascii_art():
    print(rf"{Fore.CYAN}{Style.BRIGHT} ________   ________  ______{Fore.MAGENTA}___  ________  ___  ___  ________  ________   ")
    print(rf"{Fore.CYAN}{Style.BRIGHT}|\   ___  \|\   __  \|\___   __{Fore.MAGENTA}_\\   ____\|\  \|\  \|\   __  \|\   __  \  ")
    print(rf"{Fore.CYAN}{Style.BRIGHT}\ \  \\ \  \ \  \|\  \|___ \  \_\{Fore.MAGENTA} \  \___|\ \  \\\  \ \  \|\  \ \  \|\  \ ")
    print(rf"{Fore.CYAN}{Style.BRIGHT} \ \  \\ \  \ \  \\\  \   \ \  \ \ \{Fore.MAGENTA}_____  \ \   __  \ \  \\\  \ \   ____\\ ")
    print(rf"{Fore.CYAN}{Style.BRIGHT}  \ \  \\ \  \ \  \\\  \   \ \  \ \|__{Fore.MAGENTA}__|\  \ \  \ \  \ \  \\\  \ \  \___|")
    print(rf"{Fore.CYAN}{Style.BRIGHT}   \ \__\\ \__\ \_______\   \ \__\  ____\_{Fore.MAGENTA}\  \ \__\ \__\ \_______\ \__\\   ")
    print(rf"{Fore.CYAN}{Style.BRIGHT}    \|__| \|__|\|_______|    \|__| |\_______{Fore.MAGENTA}__\|__|\|__|\|_______|\|__|   ")
    print(rf"{Fore.CYAN}{Style.BRIGHT}                \\                  \|_______{Fore.MAGENTA}__|                   {Fore.MAGENTA}\\         ")
    print(rf"{Fore.CYAN}{Style.BRIGHT}                 \\                                                   {Fore.MAGENTA}//               ")
    print(rf"{Fore.CYAN}{Style.BRIGHT}                  \\>=================>{Fore.RESET} Author: {Fore.YELLOW}{Style.BRIGHT}@notnone{Fore.RESET}            {Fore.MAGENTA} //              ")
    print(rf"{Fore.CYAN}{Style.BRIGHT}                                        {Fore.RESET}Version: {Fore.YELLOW}{Style.BRIGHT}1.0.1{Fore.RESET} {Fore.MAGENTA}<===========<//               ")
    print("\n")

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

if __name__ == "__main__":
    cls()
    init()