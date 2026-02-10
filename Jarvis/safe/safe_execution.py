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
                # Levanta um JarvisError usando o origin correto (real_origin)
                raise JarvisError(
                    message=str(exc),
                    origin=real_origin,
                    module=func.__module__,
                    function=func.__name__,
                    original_exception=exc,
                ) from exc
        return wrapper
    return decorator