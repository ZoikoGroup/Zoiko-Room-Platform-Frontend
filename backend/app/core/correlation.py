import uuid

from fastapi import Request

CORRELATION_HEADER = "X-Correlation-Id"


async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get(CORRELATION_HEADER) or uuid.uuid4().hex
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers[CORRELATION_HEADER] = correlation_id
    return response


def get_correlation_id(request: Request) -> str:
    return getattr(request.state, "correlation_id", "")
