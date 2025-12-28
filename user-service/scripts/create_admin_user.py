#!/usr/bin/env python3
"""
Script to create an initial admin user in the database.

This script can be used to create an initial admin account when setting up the system.
"""

import asyncio
import os
from datetime import datetime
import sys
from pathlib import Path

# Add the shared module to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.utils.password_utils import hash_password
from app.models.user import User
from app.enums.user import SystemRole
from shopping_shared.databases.database_manager import database_manager as postgres_db
from app.config import Config


async def create_admin_user(username: str, email: str, password: str, first_name: str, last_name: str):
    """
    Create an admin user in the database.
    
    Args:
        username: The admin username
        email: The admin email
        password: The admin password (will be hashed)
        first_name: The admin's first name
        last_name: The admin's last name
    """
    # Get database URI from config
    db_uri = Config.POSTGRESQL.DATABASE_URI
    
    # Setup database connection
    await postgres_db.setup(database_uri=db_uri, debug=Config.RUN_SETTING.get('debug', True))
    
    async with postgres_db.get_session() as session:
        # Check if admin user already exists
        existing_user = await session.execute(
            User.__table__.select().where(User.email == email)
        )
        existing_user = existing_user.fetchone()
        
        if existing_user:
            print(f"User with email {email} already exists!")
            return existing_user[0]
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Create new admin user
        admin_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            system_role=SystemRole.ADMIN,
            first_name=first_name,
            last_name=last_name,
            is_active=True,  # Set to True so admin can login immediately
            created_at=datetime.now()
        )
        
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)
        
        print(f"Admin user created successfully!")
        print(f"Username: {admin_user.username}")
        print(f"Email: {admin_user.email}")
        print(f"Role: {admin_user.system_role}")
        
        return admin_user


def main():
    # Get admin user details from environment variables or command line arguments
    username = os.getenv('ADMIN_USERNAME', 'admin')
    email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    password = os.getenv('ADMIN_PASSWORD', 'admin')
    first_name = os.getenv('ADMIN_FIRST_NAME', 'Admin')
    last_name = os.getenv('ADMIN_LAST_NAME', 'User')

    # If no environment variables are set, you can pass arguments
    if len(sys.argv) > 1:
        username = sys.argv[1]
    if len(sys.argv) > 2:
        email = sys.argv[2]
    if len(sys.argv) > 3:
        password = sys.argv[3]
    if len(sys.argv) > 4:
        first_name = sys.argv[4]
    if len(sys.argv) > 5:
        last_name = sys.argv[5]
    
    print(f"Creating admin user: {username} ({email})")
    
    # Run the async function
    admin_user = asyncio.run(create_admin_user(username, email, password, first_name, last_name))
    
    return admin_user


if __name__ == "__main__":
    main()