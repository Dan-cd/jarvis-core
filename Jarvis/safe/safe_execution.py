from functools import wraps
from Jarvis.core.errors import JarvisError


def safe_execute(*, origin: str | None = None, sensitive= False):
    def decorator(func):
        real_origin = origin or f"{func.__module__}.{func.__qualname__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                return JarvisError(
                    message=str(exc),
                    source=real_origin,
                    origin=origin,
                    module=func.__module__,
                    function=func.__name__,
                    sensitive=sensitive,
                    original_exception=exc,
                )
        return wrapper
    return decorator