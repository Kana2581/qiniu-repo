import time
from typing import Optional, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.logging_config import get_logger

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        skip_paths: Optional[List[str]] = None,
        log_body: bool = False
    ):
        super().__init__(app)
        self.skip_paths = skip_paths or []
        self.log_body = log_body

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if any(path.startswith(skip) for skip in self.skip_paths):
            return await call_next(request)

        start_time = time.time()
        method = request.method

        body_str = ""
        if self.log_body:
            try:
                body_bytes = await request.body()
                body_str = body_bytes.decode("utf-8")
            except Exception:
                body_str = "<Failed to read body>"

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"[ERROR] {method} {path} failed in {process_time:.2f}ms\n"
                f"Exception: {str(exc)}\n"
                f"Body: {body_str if self.log_body else '[Not Logged]'}",
                exc_info=True
            )
            raise

        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"[SUCCESS] {method} {path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.2f}ms"
            + (f" Body: {body_str}" if self.log_body else "")
        )
        return response