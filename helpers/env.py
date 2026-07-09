import os


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [
        item.strip()
        for item in os.getenv(name, default).split(",")
        if item.strip()
    ]

def env_str(name: str, default: str = "") -> str:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip() or default

def env_int(name: str, default: int = 0) -> int:
    value = os.getenv(name)

    if value is None:
        return default

    try:
        return int(value.strip())
    except ValueError:
        return default
