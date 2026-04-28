from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Any

RequestContext = dict[str, Any]

_request_context: ContextVar[RequestContext] = ContextVar("request_context", default={})


def get_request_context() -> RequestContext:
    return dict(_request_context.get())


def bind_request_context(**values: Any) -> Token[RequestContext]:
    context = get_request_context()
    context.update({key: value for key, value in values.items() if value is not None})
    return _request_context.set(context)


def clear_request_context(token: Token[RequestContext] | None = None) -> None:
    if token is not None:
        _request_context.reset(token)
        return
    _request_context.set({})
