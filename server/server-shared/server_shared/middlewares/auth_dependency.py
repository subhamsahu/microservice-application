from fastapi import Request, HTTPException, status


def get_current_user(request: Request) -> dict:
    """
    Shared dependency to extract the current user object attached by the API gateway.

    The gateway is expected to set `request.state.user = token_details.get("user")`.
    This function returns that dict for route handlers, or raises 401 if missing.
    """
    user = getattr(request.state, "user", None)

    # fall back to ASGI scope value if present
    if not user:
        user = request.scope.get("user")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    return user
