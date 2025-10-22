import time
from typing import Optional, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from backend.app.core.logging_config import get_logger

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        skip_paths: Optional[List[str]] = None,
        log_body: bool = False,
        log_response: bool = False,
        max_body_length: int = 2000,  # 限制日志体长度防止过长
    ):
        super().__init__(app)
        self.skip_paths = skip_paths or []
        self.log_body = log_body
        self.log_response = log_response
        self.max_body_length = max_body_length

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if any(path.startswith(skip) for skip in self.skip_paths):
            return await call_next(request)

        start_time = time.perf_counter()
        method = request.method

        # 读取请求体（并重新包装可重读）
        body_str = ""
        body_bytes = b""
        if self.log_body:
            try:
                body_bytes = await request.body()
                body_str = body_bytes.decode("utf-8", errors="replace")
                request = Request(request.scope, receive=lambda: {"type": "http.request", "body": body_bytes})
            except Exception as e:
                body_str = f"<Failed to read body: {e}>"

        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"[ERROR] {method} {path} | {process_time:.2f}ms | "
                f"Exception={exc!r} | Body={body_str if self.log_body else '[Not Logged]'}",
                exc_info=True,
            )
            raise

        process_time = (time.perf_counter() - start_time) * 1000

        # 尝试读取响应体
        response_body_str = ""
        if self.log_response:
            try:
                # 如果是 StreamingResponse，就要收集内容后再重建
                if isinstance(response, StreamingResponse):
                    content = b""
                    async for chunk in response.body_iterator:
                        content += chunk
                    response_body_str = content.decode("utf-8", errors="replace")[: self.max_body_length]
                    response = Response(
                        content,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type,
                    )
                else:
                    response_body_str = (response.body or b"").decode("utf-8", errors="replace")[: self.max_body_length]
            except Exception as e:
                response_body_str = f"<Failed to read response body: {e}>"

        logger.info(
            f"[SUCCESS] {method} {path} | Status={response.status_code} | "
            f"Time={process_time:.2f}ms"
            + (f" | RequestBody={body_str[:self.max_body_length]}" if self.log_body else "")
            + (f" | ResponseBody={response_body_str}" if self.log_response else "")
        )

        return response
