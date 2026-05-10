"""
Setup script for Sheep.AI / FinMitra Authentication System

Responsibilities:
- Initialize authentication database
- Ensure default admin exists
- Optionally create a test user

IMPORTANT:
- This script DOES NOT create filesystem directories.
- User data directories are created inside AuthDatabase.create_user()
"""

from auth_database import get_auth_db


def setup_database():
    print("=" * 60)
    print("Sheep.AI Authentication System - Setup")
    print("=" * 60)

    # --------------------------------------------------
    # Initialize database (tables + default admin)
    # --------------------------------------------------
    db = get_auth_db()
    print("\n✓ Authentication database initialized")
    print(f"  Location: {db.db_path}")

    # --------------------------------------------------
    # Verify default admin
    # --------------------------------------------------
    admin = db.get_user_by_username("admin")

    if admin:
        print("\n✓ Default admin user verified")
    else:
        # This should normally never happen because
        # create_default_admin() is called during init
        print("\n⚠ Admin user not found – something is wrong")

    print("  Username : admin")
    print("  Password : sheep123")
    print("  Role     : Admin")
    print("  ⚠ CHANGE THIS PASSWORD AFTER FIRST LOGIN")

    # --------------------------------------------------
    # Create sample test user (safe / idempotent)
    # --------------------------------------------------
    print("\nCreating sample test user (if not exists)...")

    success, message = db.create_user(
        username="testuser",
        password="test123",
        email="testuser@sheepai.info",
        role="User"
    )

    if success:
        print("✓ Sample test user created")
        print("  Username : testuser")
        print("  Password : test123")
        print("  Role     : User")
        print("  Data dir : /var/Data/testuser/data")
    else:
        if "exists" in message.lower():
            print("✓ Sample test user already exists")
        else:
            print(f"✗ Failed to create test user: {message}")

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------
    users = db.get_all_users()

    print("\n" + "=" * 60)
    print("Setup Complete")
    print("=" * 60)
    print(f"Total users in system : {len(users)}")

    print("\nYou can now run the application:")
    print("  python app_fin_mitra.py")

    print("\nDefault login credentials:")
    print("  Admin : admin / sheep123")
    print("  User  : testuser / test123")

    print("=" * 60)


if __name__ == "__main__":
    setup_database()
