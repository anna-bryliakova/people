import time

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from config import settings


logger.add("info.log", format="{time} {level} {message}", rotation="10 MB", level="INFO", enqueue=True)


async def log_middleware(request: Request, call_next):
    if settings.DUMP_SQL:
        start = time.perf_counter()
    try:
        response = await call_next(request)
        if response.status_code in [400, 401, 402, 403, 404, 422]:
            logger.warning(f"Ошибка запроса к {request.url.path}")
        else:
            logger.info(f"Запрос к {request.url.path} завершён успешно")
    except Exception as e:
        logger.error(f"Ошибка запроса к {request.url.path}: {str(e)}")
        response = JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
    finally:
        if settings.DUMP_SQL:
            logger.info(f"Запрос к {request.url.path} выполнялся {time.perf_counter() - start:.5f} c")
    return response
