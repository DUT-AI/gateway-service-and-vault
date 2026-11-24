"""Architectural purity gate tests for Clean Architecture.

Verifies that all domain entity and interface modules across all feature modules
have ZERO dependencies on frameworks like Pydantic, FastAPI, or SQLAlchemy.
"""


def test_domain_layer_purity_zero_framework_imports():
    """Verify that domain modules do not import Pydantic, FastAPI, or SQLAlchemy."""
    from modules.gateway.domain import entities as gw_ent
    from modules.gateway.domain import interfaces as gw_iface
    from modules.identity.domain import entities as id_ent
    from modules.identity.domain import exceptions as id_exc
    from modules.identity.domain import interfaces as id_iface
    from modules.vault.domain import entities as vault_ent
    from modules.vault.domain import interfaces as vault_iface

    forbidden = ["pydantic", "fastapi", "sqlalchemy"]
    checked_modules = [
        id_ent,
        id_exc,
        id_iface,
        gw_ent,
        gw_iface,
        vault_ent,
        vault_iface,
    ]

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


def test_routers_thin_layer_zero_repository_injections():
    """Verify that Presentation routers never inject Repository interfaces directly (Principle I)."""
    import re
    from pathlib import Path

    routers_dir = Path(__file__).resolve().parent.parent / "apps" / "api" / "routers"
    repo_pattern = re.compile(
        r"FromDishka\[.*Repository.*\]|from .* import .*Repository"
    )

    violations = []
    for py_file in routers_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        matches = repo_pattern.findall(content)
        if matches:
            violations.append(f"{py_file.name}: {matches}")

    assert not violations, f"Forbidden Repository injection in routers: {violations}"


def test_repositories_zero_use_case_and_commit_calls():
    """Verify that Repositories never import Use Cases or execute commit() (Principle I)."""
    from pathlib import Path

    modules_dir = Path(__file__).resolve().parent.parent / "modules"
    commit_violations = []
    use_case_violations = []

    for py_file in modules_dir.glob("*/repository/*.py"):
        if py_file.name == "__init__.py":
            continue
        content = py_file.read_text(encoding="utf-8")
        if ".commit()" in content:
            commit_violations.append(py_file.name)
        if "use_cases" in content:
            use_case_violations.append(py_file.name)

    assert not commit_violations, (
        f"Forbidden .commit() call in repositories: {commit_violations}"
    )
    assert not use_case_violations, (
        f"Forbidden use_cases import in repositories: {use_case_violations}"
    )
