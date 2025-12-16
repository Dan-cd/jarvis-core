from Jarvis.core.errors import JarvisError
from datetime import datetime

def log_error(error: JarvisError):
    with open("data/logs/error.log", "a") as f:
        f.write(
        f"\n\n"
        f"[{datetime.now()}] "
        f"origin={error.origin} "
        f"source={error.source} "
        f"module={error.module} "
        f"function={error.function} "
        f"sensitive={error.sensitive} "
        f"msg={error.message}\n\n"
        )