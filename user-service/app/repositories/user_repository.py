# user-service/app/repositories/user_repository.py
from typing import Optional, List, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload

from app.models import UserIdentityProfile
from app.models.user import User
from app.schemas.user_schema import UserCreateSchema, UserInfoUpdateSchema
from shopping_shared.databases.base_repository import BaseRepository



class UserRepository(BaseRepository[User, UserCreateSchema, UserInfoUpdateSchema]):
    """
    Repository for User model-specific database operations.
    Inherits all common CRUD, pagination, and soft-delete logic from BaseRepository.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def check_conflicts(self, username: str, email: str, phone_num: Optional[str] = None) -> List[str]:
        """
        Checks if a user with the same username, email, or phone number already exists.
        Returns a list of unique conflict messages.
        Executes a single DB query instead of multiple sequential ones.
        """
        conflicts = []
        conditions = [func.lower(User.username) == func.lower(username), func.lower(User.email) == func.lower(email)]
        
        if phone_num:
            conditions.append(func.lower(User.phone_num) == func.lower(phone_num))

        # Check for any conflicts, excluding deleted users
        stmt = select(User.username, User.email, User.phone_num).where(or_(*conditions)).where(User.is_deleted.is_(False))
        
        result = await self.session.execute(stmt)
        # Fetch all matching records (there could be multiple conflicts)
        existing_records = result.all()
        
        for record in existing_records:
            r_username, r_email, r_phone = record
            
            if r_username and r_username.lower() == username.lower():
                conflicts.append(f"User with username '{username}' already exists.")
            if r_email and r_email.lower() == email.lower():
                conflicts.append(f"User with email '{email}' already exists.")
            if phone_num and r_phone and r_phone.lower() == phone_num.lower():
                 conflicts.append(f"User with phone number '{phone_num}' already exists.")

        return list(set(conflicts))

    async def get_by_username(self, username: str) -> Optional[User]:
        """Fetches user by username."""
        return await self.get_by_field_case_insensitive("username", username)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch user record by email."""
        return await self.get_by_field_case_insensitive("email", email)

    async def activate_user(self, user_id: UUID) -> Optional[User]:
        """Activates a user account by setting is_active to True."""
        return await self.update_field(user_id, "is_active", True)

    async def update_password(self, user_id: UUID, hashed_password: str) -> Optional[User]:
        """Updates the user's password with the hashed value."""
        return await self.update_field(user_id, "password_hash", hashed_password)


    async def get_user_for_registration_check(
        self,
        username,
        email,
        phone_num: Optional[str] = None
    ) -> dict:
        conditions = [
            func.lower(User.username) == func.lower(username),
            func.lower(User.email) == func.lower(email),
        ]

        if phone_num:
            conditions.append(func.lower(User.phone_num) == func.lower(phone_num))

        stmt = select(User).where(or_(*conditions)).where(User.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        users = result.scalars().all()

        result_dict: Dict[str, Optional[User]] = {
            "username_match": None,
            "email_match": None,
            "phone_match": None,
        }

        for user in users:
            if user.username and user.username.lower() == username.lower():
                result_dict["username_match"] = user
            if user.email and user.email.lower() == email.lower():
                result_dict["email_match"] = user
            if user.phone_num and user.phone_num.lower() == phone_num.lower():
                result_dict["phone_match"] = user

        return result_dict

    async def create_user_with_dict(self, user_data: dict) -> User:
        """
        Creates a new user from a dictionary and optimizes response.
        Sets profile relations to None to prevent unnecessary lazy-load queries
        since a newly created user definitely has no profiles yet.
        """
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        
        # Optimization: Prevent extra SELECT queries when serializing
        user.identity_profile = None
        user.health_profile = None
        
        return user


    async def get_user_with_profiles(self, user_id: UUID) -> Optional[User]:
        """
        Gets user with eager-loaded identity and health profiles.
        Useful for /users/me endpoint to return complete user data.
        """
        load_options = [
            selectinload(User.identity_profile).selectinload(UserIdentityProfile.address),
            selectinload(User.health_profile)
        ]
        return await self.get_by_id(user_id, load_options=load_options)


    async def get_by_identifier(self, identifier: str) -> Optional[User]:
        """
        Fetches user by either username or email using a single optimized query.
        """
        stmt = select(User).where(
            or_(
                func.lower(User.username) == func.lower(identifier),
                func.lower(User.email) == func.lower(identifier)
            )
        )
        # Apply default soft-delete filter
        stmt = stmt.where(User.is_deleted.is_(False))
        
        result = await self.session.execute(stmt.limit(1))
        return result.scalars().first()

