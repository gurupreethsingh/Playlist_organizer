from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    email = "superadmin@gmail.com"
    username = "superadmin"
    password = "abc123ABC!@#"

    existing_user = User.query.filter(
        (User.email == email) | (User.username == username)
    ).first()

    if existing_user:
        existing_user.full_name = "Super Admin"
        existing_user.username = username
        existing_user.email = email
        existing_user.role = "superadmin"
        existing_user.is_subscription_active = True
        existing_user.is_active_user = True
        existing_user.set_password(password)

        db.session.commit()

        print("Existing superadmin updated successfully.")
        print("Email:", email)
        print("Password:", password)
    else:
        admin = User(
            full_name="Super Admin",
            username=username,
            email=email,
            role="superadmin",
            is_subscription_active=True,
            is_active_user=True,
        )
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("Superadmin created successfully.")
        print("Email:", email)
        print("Password:", password)