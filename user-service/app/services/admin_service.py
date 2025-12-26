# user-service/app/services/admin_service.py
from uuid import UUID

from pydantic import EmailStr

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.family_group_repository import GroupMembershipRepository
from app.schemas.user_admin_schema import UserAdminUpdateSchema
from app.models.family_group import GroupMembership
from app.utils.password_utils import hash_password
from app.enums import GroupRole

from shopping_shared.exceptions import Conflict, NotFound
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Admin Service")

class AdminUserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    # ===== User Management by Admin =====

    async def get_user_by_admin(self, user_id):
        """Fetch a user by ID for admin."""
        user = await self.user_repo.get_user_with_profiles(user_id)
        if not user:
            raise NotFound(f"User with id {user_id} not found")
        return user


    async def get_all_users(self, page: int = 1, page_size: int = 20):
        """Fetch all users with pagination."""
        from sqlalchemy.orm import selectinload
        load_options = [
            selectinload(User.identity_profile),
            selectinload(User.health_profile)
        ]
        return await self.user_repo.get_paginated(
            page=page,
            page_size=page_size,
            load_options=load_options
        )


    async def create_user_by_admin(self, user_data):
        """Creates a new user by an admin."""
        existing_user = await self.user_repo.get_by_username(user_data.username)
        if existing_user:
            raise Conflict(f"User with username {user_data.username} already exists.")

        # Hash password (handle SecretStr properly)
        password_str = user_data.password.get_secret_value() if hasattr(user_data.password, 'get_secret_value') else str(user_data.password)
        hashed_password = hash_password(password_str)

        # Convert schema to dict and inject hashed password
        new_user_data = user_data.model_dump(exclude={'password'})
        new_user_data['password_hash'] = hashed_password

        # Create user via repository
        user = await self.user_repo.create_user(new_user_data)

        # Refresh user with profiles to avoid lazy-load issues during serialization
        updated_user = await self.user_repo.get_user_with_profiles(user.id)

        logger.info(f"Admin created user: {user.username}")
        return updated_user

    async def update_user_by_admin(self, user_id: UUID, update_data: UserAdminUpdateSchema):
        """Updates a user's information by an admin."""
        user = await self.user_repo.update(user_id, update_data)
        if not user:
            raise NotFound(f"User with id {user_id} not found")

        # Get the updated user with profiles
        updated_user = await self.user_repo.get_user_with_profiles(user_id)
        logger.info(f"Admin updated user: {user_id}")
        return updated_user

    async def delete_user_by_admin(self, user_id: UUID):
        """Delete a user by an admin. Using soft_delete if supported, or delete"""
        deleted = await self.user_repo.soft_delete(user_id)
        if not deleted:
             user = await self.user_repo.get_by_id(user_id)
             if not user:
                 raise NotFound(f"User with id {user_id} not found")
             await self.user_repo.delete(user_id) # Hard delete fallback or actual delete

        logger.info(f"Admin deleted user: {user_id}")


    # ===== Group Membership Management by Admin =====

class AdminGroupService:
    def __init__(self, user_repository: UserRepository, member_repo: GroupMembershipRepository):
        self.user_repo = user_repository
        self.member_repo = member_repo

    async def add_member_by_admin(self, group_id: UUID, email: EmailStr) -> GroupMembership:
        """Admin adds member directly."""
        user_to_add = await self.user_repo.get_by_email(str(email))
        if not user_to_add:
            raise NotFound(f"User with email {email} not found.")

        existing = await self.member_repo.get_membership(user_to_add.id, group_id)
        if existing:
            raise Conflict("User is already a member of this group.")

        membership = await self.member_repo.add_membership(user_to_add.id, group_id, GroupRole.MEMBER)
        return membership

    async def remove_member_by_admin(self, group_id: UUID, user_id: UUID):
        """Admin removes member directly."""
        existing = await self.member_repo.get_membership(user_id, group_id)
        if not existing:
             raise NotFound("Membership not found.")
        await self.member_repo.remove_membership(user_id, group_id)

    async def update_member_role_by_admin(self, group_id: UUID, user_id: UUID, new_role: GroupRole):
        """Admin updates member role directly."""
        membership = await self.member_repo.update_role(user_id, group_id, new_role)
        if not membership:
             raise NotFound("Membership not found.")
        return membership