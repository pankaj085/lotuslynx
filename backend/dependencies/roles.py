from fastapi import HTTPException, Depends, status
from models.user import UserRole, User
from .auth import get_current_user

async def require_admin(
    user: User = Depends(get_current_user)
) -> User:
    """Dependency to restrict access to admins"""
    if str(user.role) != UserRole.admin.value:  # Convert to string and compare values
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user

async def require_editor(
    user: User = Depends(get_current_user)
) -> User:
    """Dependency for editors or admins"""
    if str(user.role) not in [role.value for role in (UserRole.admin, UserRole.editor)]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor privileges required"
        )
    return user