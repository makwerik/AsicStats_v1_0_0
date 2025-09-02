import os
from typing import ClassVar, Literal, Dict, List, Optional

import httpx
import asyncio

from dotenv import load_dotenv

from S19.model import HashRate, StatsFan, StatsBoard
from debugging.logger import repair_s19

load_dotenv()

LOGIN = os.getenv("login")
PASSWORD = os.getenv("password")
URL = os.getenv("url")

class S19Async:
    """Класс для работы с S19"""

    ERROR_MESSAGE: ClassVar[Optional[str]] = None
    NETWORK: ClassVar[bool] = True
    FANS: ClassVar[bool] = True
    # Общая блокировка для исключения гонки установки состояний флагов
    _CLASS_LOCK: ClassVar[asyncio.Lock] = asyncio.Lock()

    VERSION = "1.0.0"

    def __init__(self):
        # Асинхронный клиент для http-запросов с поддержкой DigestAuth аутентификации
        self.client: httpx.AsyncClient = httpx.AsyncClient(verify=False, timeout=httpx.Timeout(60.0))
        self.url: str = URL
        self.login: str = LOGIN
        self.password: str = PASSWORD
        # Словарь с данными о состоянии S19
        self.data: Dict = {}
        # Блокировка экземпляра класса, для предотвращения гонок данных
        self.lock: asyncio.Lock = asyncio.Lock()

    @classmethod
    async def set_flag(cls, name: Literal["NETWORK", "FANS"], flag: bool) -> None:
        """
        Метод для установки boolean значений для флагов.
        :param name: Имя флага.
        :param flag: Boolean значение
        """
        async with cls._CLASS_LOCK:
            setattr(cls, name, flag)

    @classmethod
    async def set_message(cls, message: Optional[str]) -> None:
        """
        Метод для установки сообщений об исключениях.
        :param message: Сообщение.
        """
        async with cls._CLASS_LOCK:
            setattr(cls, "ERROR_MESSAGE", message)


    async def _make_requests(self) -> None:
        """
        Метод для асинхронных запросов к http-серверу.
         Наполняет словарь с данными data{}.
        """
        response = await self.client.get(url=self.url, auth=httpx.DigestAuth(self.login, self.password))
        response.raise_for_status()

        async with self.lock:
            self.data = response.json().get("STATS")[0]

        # Повторная установка флага в True, чтобы избежать залипания, если до этого была ошибка
        await self.set_flag("NETWORK", True)
        await self.set_message(None)

    @repair_s19
    async def get_stats_hash_rate(self) -> HashRate:
        """
        Метод полает хэшрейт за последние 5 секунд, 30 минут и средний хэшрейт.
        :return: Возвращает актуальную информацию о хэше через pydantic схему.
        """
        await self._make_requests()

        hash_rate_5_second: float = self.data.get("rate_5s")
        hash_rate_30_minutes: float = self.data.get("rate_30m")
        hash_rate_avg: float = self.data.get("rate_avg")

        all_hash_rate = {"hash_rate_5_second": hash_rate_5_second,
                         "hash_rate_30_minutes": hash_rate_30_minutes,
                         "hash_rate_avg": hash_rate_avg}

        return HashRate(**all_hash_rate)

    @repair_s19
    async def get_stats_fan(self) -> StatsFan:
        """
        Метод получает состояние вентиляторов, а именно скорость вращения.
        :return: Возвращает актуальную информацию о вентиляторах через pydantic схему.
        """
        await self._make_requests()

        first_fan: int = self.data.get("fan")[0]
        second_fan: int = self.data.get("fan")[1]
        third_fan: int = self.data.get("fan")[2]
        fourth_fan: int = self.data.get("fan")[3]


        all_stats_fan = {"first_fan": first_fan,
                         "second_fan": second_fan,
                         "third_fan": third_fan,
                         "fourth_fan": fourth_fan}

        return StatsFan(**all_stats_fan)

    @repair_s19
    async def get_stats_board(self) -> List[StatsBoard]:
        """
        Метод получает актуальную информацию о состоянии плат, в том числе температуру чипов, входящего воздуха
         и выходящего.
        :return: Возвращает список с актуальной информацией о вентиляторах через pydantic схему.
        """
        await self._make_requests()

        board_stats: list = self.data.get("chain")

        results: List[Dict] = []

        for index, board in enumerate(board_stats):
            results.append(
                {
                    "board_number": index,
                    "incoming_air": board.get("temp_pic"),
                    "temperature_of_the_board": board.get("temp_pcb"),
                    "chip_temperature": board.get("temp_chip")
                }
            )

        return [StatsBoard(**board) for board in results]
