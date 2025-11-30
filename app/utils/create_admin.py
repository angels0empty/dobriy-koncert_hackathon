"""
Скрипт для создания первого администратора
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.admin_permission import AdminPermission
from app.utils.auth import get_password_hash


def create_admin():
    """Создать супер-админа"""
    db = SessionLocal()

    try:
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_admin:
            print("Админ уже существует!")
            return

        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Super Admin",
            role=UserRole.admin,
            is_active=True,
            is_blocked=False
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Даём все права
        permissions = AdminPermission(
            user_id=admin.id,
            can_manage_users=True,
            can_manage_courses=True,
            can_manage_tests=True,
            can_view_analytics=True,
            can_manage_permissions=True
        )

        db.add(permissions)
        db.commit()

        print("[+] admin created")
        print(f"Email: admin@example.com")
        print(f"Password: admin123")
    except Exception as e:
        print(f"[-] Ошибка при создании админа: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
