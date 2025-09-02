import asyncio
import os
from typing import Dict
from aiogram import Bot, Router, Dispatcher, F
from dotenv import load_dotenv
from aiogram.filters import CommandStart
from aiogram.types import Message
from Bot.middlewares.auth import AuthMiddleware
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from S19.asyncantiminer import S19Async
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

logger = logging.getLogger(__name__)

load_dotenv()

token = os.getenv("bot_token")

router = Router()

s19 = S19Async()


@router.message(CommandStart())
async def start(message: Message, is_allowed: bool) -> None:
    """
    Хендлер (обработчик) команды /start
        параметр - is_allowed: Автоматически прокинут моим мидлварой AuthMiddleware
    """
    if is_allowed:
        keyboard_list = [
            [KeyboardButton(text="Hash Rate")], [KeyboardButton(text="Fans 𖣘")],
            [KeyboardButton(text="Temperature c°")], [KeyboardButton(text="Включить мониторинг")],
            [KeyboardButton(text="Отключить мониторинг")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=keyboard_list, resize_keyboard=True)
        await message.answer("🔐🚪", reply_markup=keyboard)
    else:
        await message.answer("🔒🚪")


@router.message(F.text == "Hash Rate")
async def hash_rate(message: Message, is_allowed: bool):
    """
    Хендлер (обработчик) сообщения Hash Rate
        параметр - is_allowed: Автоматически прокинут моим мидлварой AuthMiddleware
    """
    if is_allowed:
        hash_rate_stats = await s19.get_stats_hash_rate()

        if s19.ERROR_MESSAGE:
            await message.answer(text=s19.ERROR_MESSAGE)
            return

        if s19.NETWORK:
            msg = (
                "*⚡ Хешрейт*\n\n"
                f"📊 Средний: `{hash_rate_stats.hash_rate_avg}` TH/s\n"
                f"⏱️ За 5 секунд: `{hash_rate_stats.hash_rate_5_second}` TH/s\n"
                f"🕒 За 30 минут: `{hash_rate_stats.hash_rate_30_minutes}` TH/s"
            )
            await message.answer(msg, parse_mode="MarkdownV2")
        else:
            msg = (
                "❌ *Нет сети*\n\n"
                "Проверьте подключение к интернету или доступ к ASIC"
            )
            await message.answer(msg, parse_mode="MarkdownV2")
    return


@router.message(F.text == "Fans 𖣘")
async def fan_stats(message: Message, is_allowed: bool):
    """
    Хендлер (обработчик) сообщения Fans 𖣘
        параметр - is_allowed: Автоматически прокинут моим мидлварой AuthMiddleware
    """
    if is_allowed:
        fans_stats = await s19.get_stats_fan()

        if s19.ERROR_MESSAGE:
            await message.answer(text=s19.ERROR_MESSAGE)
            return

        if s19.NETWORK:
            if s19.FANS:
                msg = (
                    "*🌀 Вентиляторы*\n\n"
                    f"1️⃣ 🌬️⬅️ Вдув воздуха: `{fans_stats.first_fan}` RPM\n"
                    f"2️⃣ 🌬️⬅️ Вдув воздуха: `{fans_stats.second_fan}` RPM\n"
                    f"3️⃣ ➡️🌬️ Выдув воздуха: `{fans_stats.third_fan}` RPM\n"
                    f"4️⃣ ➡️🌬️ Выдув воздуха: `{fans_stats.fourth_fan}` RPM"
                )
                await message.answer(msg, parse_mode="MarkdownV2")
            else:
                msg = (
                    "❌ *ВИНТАМ ПИЗДА*\n\n"
                    "СРОЧНО ОТКЛЮЧАЙ АСИК"
                )
                await message.answer(msg, parse_mode="MarkdownV2")
        else:
            msg = (
                "❌ *Нет сети*\n\n"
                "Проверьте подключение к интернету или доступ к ASIC"
            )
            await message.answer(msg, parse_mode="MarkdownV2")
    return


@router.message(F.text == "Temperature c°")
async def temperature_stats(message: Message, is_allowed: bool):
    """
    Хендлер (обработчик) сообщения Temperature c°
        параметр - is_allowed: Автоматически прокинут моим мидлварой AuthMiddleware
    """
    if is_allowed:
        temp_stats = await s19.get_stats_board()

        if s19.ERROR_MESSAGE:
            await message.answer(text=s19.ERROR_MESSAGE)
            return

        if s19.NETWORK:
            one_board = temp_stats[0]
            second_board = temp_stats[1]
            third_board = temp_stats[2]

            msg = (
                "📟 <b>Состояние плат</b>\n\n"
                f"🧩 <b>Плата {one_board.board_number + 1}</b>\n"
                f"🌬 Входящий воздух: <code>{one_board.incoming_air}°C</code>\n"
                f"📋 Плата: <code>{one_board.temperature_of_the_board}°C</code>\n"
                f"💠 Чипы: <code>{one_board.chip_temperature}°C</code>\n\n"
                f"🧩 <b>Плата {second_board.board_number + 1}</b>\n"
                f"🌬 Входящий воздух: <code>{second_board.incoming_air}°C</code>\n"
                f"📋 Плата: <code>{second_board.temperature_of_the_board}°C</code>\n"
                f"💠 Чипы: <code>{second_board.chip_temperature}°C</code>\n\n"
                f"🧩 <b>Плата {third_board.board_number + 1}</b>\n"
                f"🌬 Входящий воздух: <code>{third_board.incoming_air}°C</code>\n"
                f"📋 Плата: <code>{third_board.temperature_of_the_board}°C</code>\n"
                f"💠 Чипы: <code>{third_board.chip_temperature}°C</code>"
            )

            await message.answer(msg, parse_mode="HTML")
        else:
            msg = (
                "❌ *Нет сети*\n\n"
                "Проверьте подключение к интернету или доступ к ASIC"
            )
            await message.answer(msg, parse_mode="MarkdownV2")
    return



fan_tasks: Dict[int, asyncio.Task] = {}


async def check_fan(bot: Bot, chat_id: int, is_allowed: bool, interval: int = 10):
    """
    Метод проверяет каждые 10 секунд состояние вентиляторов.
    """
    if is_allowed:
        while True:
            fans_stat = await s19.get_stats_fan()
            # Проверяем флаг
            if not s19.NETWORK:
                msg = (
                    "❌ *ВИНТАМ ПИЗДА*\n\n"
                    "СРОЧНО ОТКЛЮЧАЙ АСИК"
                )
                await bot.send_message(chat_id=chat_id, text=msg, parse_mode="MarkdownV2")

            logger.info(msg=f"Информация о задаче: {fan_tasks} || Информация о винтах: {fans_stat}")
            await asyncio.sleep(interval)

    return



@router.message(F.text == "Включить мониторинг")
async def fan_start(message: Message, bot: Bot, is_allowed: bool):
    if is_allowed:
        chat_id = message.chat.id
        # Пытаемся получить задачу
        task = fan_tasks.get(chat_id)

        if task and not task.done():
            # Если задача есть, то не плодим их
            await message.answer("Мониторинг уже запущен")
            return

        fan_tasks[chat_id] = asyncio.create_task(check_fan(bot=bot, chat_id=chat_id, is_allowed=is_allowed))
        await message.answer("Запущен мониторинг вентиляторов каждые 10 секунд")

    return


@router.message(F.text == "Отключить мониторинг")
async def fun_disabled(message: Message, is_allowed: bool):
    """Метод остановки мониторинга"""
    if is_allowed:
        chat_id = message.chat.id
        task = fan_tasks.pop(chat_id, None)

        if not task:
            await message.answer("Мониторинг не запущен")
            return

        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        logger.info(msg=f"Задачи удалены: {fan_tasks}")
        await message.answer("Мониторинг остановлен")

    return



async def main() -> None:
    bot = Bot(token=token)
    # Диспетчер
    dp = Dispatcher()
    # Регистрирую мидлвару на обработчик сообщений, каждое событие пройдет сначала через AuthMiddleware
    # В data появится is_allowed и попадёт в хэндлеры (обработчики)
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Подключаю роутер с хэндерами (обработчиками)
    dp.include_router(router)
    await dp.start_polling(bot)
