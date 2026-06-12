import sys

from app.db.session import SessionLocal
from app.models.user import UserRole
from app.schemas.user import UserCreate
from app.services.user_service import create_user, get_user_by_email


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: python scripts/create_admin.py admin@example.com "Password123!"')
        return 2

    email, password = sys.argv[1], sys.argv[2]

    db = SessionLocal()
    try:
        if get_user_by_email(db, email=email):
            print(f"User already exists: {email}")
            return 1

        user = create_user(
            db,
            UserCreate(
                email=email,
                full_name="System Administrator",
                password=password,
                role=UserRole.ADMIN,
                is_active=True,
            ),
        )
        print(f"Created admin user: {user.email}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
