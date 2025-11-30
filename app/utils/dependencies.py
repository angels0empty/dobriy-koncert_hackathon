from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.admin_permission import AdminPermission
from app.utils.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    if not user.is_active or user.is_blocked:
        raise HTTPException(status_code=403, detail="User is inactive or blocked")

    return user


async def get_current_teacher(current_user: User = Depends(get_current_user)) -> User:
    """Проверка что пользователь - преподаватель"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Only teachers can access this")
    return current_user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Проверка что пользователь - админ"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def check_permission(permission: str):
    """Проверка конкретного права админа"""
    async def _check(
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
    ):
        perms = db.query(AdminPermission).filter(
            AdminPermission.user_id == current_user.id
        ).first()

        if not perms:
            raise HTTPException(status_code=403, detail=f"Permission {permission} required")

        if not getattr(perms, permission, False):
            raise HTTPException(status_code=403, detail=f"Permission {permission} required")

        return current_user
    return _check
