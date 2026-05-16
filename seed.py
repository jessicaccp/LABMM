"""
Seed script: creates the first super-admin account.
Run once after `flask db upgrade`:

    python seed.py
"""

import os

from dotenv import load_dotenv

load_dotenv()

from labmm import create_app
from labmm.extensions import db
from labmm.models.member import Member


def seed():
    app = create_app()
    with app.app_context():
        if Member.query.count() > 0:
            print("Database already seeded — skipping.")
            return

        email = os.environ.get("ADMIN_EMAIL", "admin@labmm.local")
        password = os.environ.get("ADMIN_PASSWORD", "changeme")
        first_name = os.environ.get("ADMIN_FIRST_NAME", "Admin")
        last_name = os.environ.get("ADMIN_LAST_NAME", "User")

        admin = Member(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_super_admin=True,
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Super-admin created: {email}")


if __name__ == "__main__":
    seed()
