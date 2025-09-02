import logging
from functools import wraps

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def repair_s19(func):
    """
    Метод для логирования действий и ошибок
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            logger.info(msg=f"{func.__name__} ")
            return await func(self, *args, **kwargs)
        except (httpx.RequestError, httpx.InvalidURL):
            logger.error(msg="Нет сети")
            await self.set_flag("NETWORK", False)
        except (KeyError, IndexError, ValueError, TypeError):
            if func.__name__ == "get_stats_fan":
                await self.set_flag("FANS", False)
            else:
                logger.exception("Ошибка валидации: ")
                await self.set_message("Данные недоступны")


    return wrapper