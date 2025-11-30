from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.admin_permission import AdminPermission
from app.schemas.admin import UserAdminResponse, UserUpdate, AdminPermissionUpdate, AdminPermissionResponse
from app.utils.dependencies import get_current_admin, check_permission
from app.utils.auth import get_password_hash
import secrets

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


@router.get("/", response_model=List[UserAdminResponse])
def get_users(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_blocked: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(check_permission("can_manage_users")),
    db: Session = Depends(get_db)
):
    """Получить список всех пользователей с фильтрами"""
    query = db.query(User)

    # Фильтры
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_blocked is not None:
        query = query.filter(User.is_blocked == is_blocked)
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) | (User.full_name.ilike(f"%{search}%"))
        )

    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserAdminResponse)
def get_user(
    user_id: UUID,
    current_user: User = Depends(check_permission("can_manage_users")),
    db: Session = Depends(get_db)
):
    """Получить детали пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserAdminResponse)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(check_permission("can_manage_users")),
    db: Session = Depends(get_db)
):
    """Обновить пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Обновляем поля
    if user_data.full_name:
        user.full_name = user_data.full_name
    if user_data.role:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.is_blocked is not None:
        user.is_blocked = user_data.is_blocked

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    hard_delete: bool = Query(False),
    current_user: User = Depends(check_permission("can_manage_users")),
    db: Session = Depends(get_db)
):
    """Удалить пользователя (мягкое или жёсткое)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Нельзя удалить себя
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    if hard_delete:
        db.delete(user)
    else:
        user.is_active = False

    db.commit()
    return {"message": "User deleted"}


@router.post("/{user_id}/block")
def block_user(
    user_id: UUID,
    current_user: User = Depends(check_permission("can_manage_users")),
    db: Session = Depends(get_db)
):
    """Заблокировать пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot block yourself")

    user.is_blocked = True
    db.commit()
    return {"message": "User blocked"}


@router.post("/{user_id}/unblock")
def unblock_user(
    user_id: UUID,
    current_user: User = Depends(check_permission("can_manage_users")),
    db: Session = Depends(get_db)
):
    """Разблокировать пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_blocked = False
    db.commit()
    return {"message": "User unblocked"}


@router.put("/{user_id}/permissions", response_model=AdminPermissionResponse)
def update_permissions(
    user_id: UUID,
    permissions_data: AdminPermissionUpdate,
    current_user: User = Depends(check_permission("can_manage_permissions")),
    db: Session = Depends(get_db)
):
    """Обновить права админа"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role != "admin":
        raise HTTPException(status_code=400, detail="User is not an admin")

    # Проверяем существующие права
    perms = db.query(AdminPermission).filter(AdminPermission.user_id == user_id).first()

    if perms:
        # Обновляем
        perms.can_manage_users = permissions_data.can_manage_users
        perms.can_manage_courses = permissions_data.can_manage_courses
        perms.can_manage_tests = permissions_data.can_manage_tests
        perms.can_view_analytics = permissions_data.can_view_analytics
        perms.can_manage_permissions = permissions_data.can_manage_permissions
        db.commit()
        db.refresh(perms)
    else:
        # Создаём новые
        perms = AdminPermission(
            user_id=user_id,
            can_manage_users=permissions_data.can_manage_users,
            can_manage_courses=permissions_data.can_manage_courses,
            can_manage_tests=permissions_data.can_manage_tests,
            can_view_analytics=permissions_data.can_view_analytics,
            can_manage_permissions=permissions_data.can_manage_permissions
        )
        db.add(perms)
        db.commit()
        db.refresh(perms)

    return perms


@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: UUID,
    current_user: User = Depends(check_permission("can_manage_users")),
    db: Session = Depends(get_db)
):
    """Сбросить пароль пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Генерируем временный пароль
    temp_password = secrets.token_urlsafe(12)
    user.hashed_password = get_password_hash(temp_password)

    db.commit()

    return {
        "message": "Password reset successfully",
        "temporary_password": temp_password
    }
