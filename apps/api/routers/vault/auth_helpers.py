from typing import Any


def resolve_caller_identity(
    user_payload: dict[str, Any] | None = None,
    x_identity_id: str | None = None,
    x_user_role: str | None = None,
    identity_query_param: str | None = None,
) -> str:
    """Resolve caller identity prioritising explicit headers/query, then authenticated SSO JWT."""
    if x_identity_id:
        return x_identity_id
    if identity_query_param:
        return identity_query_param
    if x_user_role:
        return x_user_role

    if user_payload:
        roles = [str(r).lower() for r in (user_payload.get("role_names") or [])]
        if user_payload.get("role"):
            roles.append(str(user_payload["role"]).lower())
        permissions = user_payload.get("permissions") or []

        # Privileged roles or wildcard permissions map to admin
        if (
            any(r in ["admin", "system", "superuser"] for r in roles)
            or "*" in permissions
        ):
            return "admin"

        return str(
            user_payload.get("user_id") or user_payload.get("sub") or "anonymous"
        )

    return "anonymous"
