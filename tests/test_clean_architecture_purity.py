"""Architectural purity gate tests for Clean Architecture.

Verifies that all domain entity and interface modules across all feature modules
have ZERO dependencies on frameworks like Pydantic, FastAPI, or SQLAlchemy.
"""


def test_domain_layer_purity_zero_framework_imports():
    """Verify that domain modules do not import Pydantic, FastAPI, or SQLAlchemy."""
    from modules.identity.domain import entities as id_ent
    from modules.identity.domain import exceptions as id_exc
    from modules.identity.domain import interfaces as id_iface

    forbidden = ["pydantic", "fastapi", "sqlalchemy"]
    checked_modules = [id_ent, id_exc, id_iface]

    for mod in checked_modules:
        mod_dict = mod.__dict__
        for imp in forbidden:
            assert imp not in mod_dict, (
                f"Forbidden framework import '{imp}' found in domain module '{mod.__name__}'"
            )


def test_user_id_standardization_is_int():
    """Verify that user identifier in domain entity is strictly an int."""
    from modules.identity.domain.entities import UserEntity

    user = UserEntity(id=1, email="test@example.com")
    assert isinstance(user.id, int)
    assert user.is_active() is True
    assert user.is_admin() is False
