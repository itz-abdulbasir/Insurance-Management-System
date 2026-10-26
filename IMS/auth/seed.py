"""
IMS — Admin Seeder
Pre-seeds the default admin account if it doesn't already exist.
"""

import bcrypt
from db.connection import execute_query
from config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_NAME


def seed_admin():
    """Insert default admin user if not already present."""
    existing = execute_query(
        "SELECT user_id FROM users WHERE email = %s AND role = 'admin'",
        (ADMIN_EMAIL,),
        fetch=True
    )
    if existing:
        print("[IMS] Admin account already exists.")
        return

    password_hash = bcrypt.hashpw(
        ADMIN_PASSWORD.encode("utf-8"),
        bcrypt.gensalt(rounds=12)
    ).decode("utf-8")

    execute_query(
        "INSERT INTO users (full_name, email, phone, password_hash, role) "
        "VALUES (%s, %s, %s, %s, 'admin')",
        (ADMIN_NAME, ADMIN_EMAIL, "0000000000", password_hash)
    )
    print(f"[IMS] Admin seeded: {ADMIN_EMAIL}")
