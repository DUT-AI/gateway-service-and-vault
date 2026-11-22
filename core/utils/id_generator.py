from ulid import ULID


def generate_ulid() -> str:
    """Generate a standard 26-character sortable ULID string."""
    return str(ULID())


def generate_id(prefix: str) -> str:
    """Generate prefixed identifier (e.g. usr_01H..., prj_01H...)."""
    return f"{prefix}_{generate_ulid()}"
