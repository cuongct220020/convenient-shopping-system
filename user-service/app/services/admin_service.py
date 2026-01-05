# user-service/app/services/admin_service.py
from uuid import UUID
from typing import Tuple, Sequence

from sqlalchemy.exc import IntegrityError

from app.enums import GroupRole
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.family_group_repository import FamilyGroupRepository
from app.repositories.group_membership_repository import GroupMembershipRepository
from app.schemas.user_admin_schema import UserAdminUpdateSchema, UserAdminCreateSchema
from app.models.family_group import GroupMembership
from app.utils.password_utils import hash_password
from app.services.redis_service import redis_service


from shopping_shared.exceptions import Conflict, NotFound
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.caching.redis_keys import RedisKeys

logger = get_logger("Admin Service")

class AdminUserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    # ===== User Management by Admin =====

    async def get_user_by_admin(self, user_id: UUID):
        """Fetch a user by ID for admin."""
        user = await self.user_repo.get_user_with_profiles(user_id)
        if not user:
            raise NotFound(f"User with id {user_id} not found")
        return user


    async def get_all_users_paginated(self, page: int = 1, page_size: int = 20) -> Tuple[list, int]:
        """Fetch all users with pagination."""
        from sqlalchemy.orm import selectinload
        load_options = [
            selectinload(User.identity_profile),
            selectinload(User.health_profile)
        ]
        paginated_result = await self.user_repo.get_paginated(
            page=page,
            page_size=page_size,
            load_options=load_options
        )

        # get_paginated returns a PaginationResult object with items and total_items properties
        return paginated_result.items, paginated_result.total_items


    async def create_user_by_admin(self, user_data: UserAdminCreateSchema):
        """Creates a new user by an admin."""
        # 1. Consolidated Conflict Check (1 DB Query)
        conflicts = await self.user_repo.check_conflicts(
            username=user_data.username, 
            email=str(user_data.email), 
            phone_num=user_data.phone_num
        )
        
        if conflicts:
            # Join all conflict messages or just raise the first one. 
            # Returning the first one is usually cleaner for API responses.
            raise Conflict(conflicts[0])

        # Hash password (handle SecretStr properly)
        password_str = user_data.password.get_secret_value() if hasattr(user_data.password, 'get_secret_value') else str(user_data.password)
        hashed_password = hash_password(password_str)

        # Convert schema to dict and inject hashed password
        new_user_data = user_data.model_dump(exclude={'password'})
        new_user_data['password_hash'] = hashed_password
        new_user_data["is_active"] = True

        try:
            # Create user and get result optimized (1 DB Transaction)
            # create_user_with_dict includes optimization to avoid extra SELECT queries
            user = await self.user_repo.create_user_with_dict(new_user_data)
            
            # Invalidate list cache
            await redis_service.delete_pattern(RedisKeys.ADMIN_USERS_LIST_WILDCARD)
        except IntegrityError as e:
            logger.error(f"Integrity error creating user: {e}")
            # Fallback in case race condition passed the first check
            raise Conflict("User with provided unique fields already exists.")

        logger.info(f"Admin created user: {user.username}")
        return user


    async def update_user_by_admin(
        self,
        user_id: UUID,
        update_data: UserAdminUpdateSchema
    ):
        """Updates a user's information by an admin, handling nested profiles."""
        from sqlalchemy.orm import selectinload
        
        # 1. Separate nested profile data from user core data
        # We model_dump first to work with dicts
        update_dict = update_data.model_dump(exclude_unset=True)
        
        identity_data = update_dict.pop("identity_profile", None)
        health_data = update_dict.pop("health_profile", None)
        
        # 2. Update Core User Info
        
        user = await self.user_repo.get_by_id(
            user_id, 
            load_options=[
                selectinload(User.identity_profile),
                selectinload(User.health_profile)
            ]
        )
        
        if not user:
            raise NotFound(f"User with id {user_id} not found")

        # Update core fields manually or via simple assignment
        for key, value in update_dict.items():
            setattr(user, key, value)

        # 3. Handle Identity Profile Update
        if identity_data:
            # Handle Address separately
            address_data = identity_data.pop("address", None)
            
            if user.identity_profile:
                # Update existing profile fields
                for k, v in identity_data.items():
                    setattr(user.identity_profile, k, v)
                
                # Handle Address update/create
                if address_data:
                    from app.models.user_profile import Address
                    if user.identity_profile.address:
                        # Update existing address
                        for ak, av in address_data.items():
                            setattr(user.identity_profile.address, ak, av)
                    else:
                        # Create new address
                        new_address = Address(**address_data)
                        user.identity_profile.address = new_address
            else:
                # Create new profile
                from app.models.user_profile import UserIdentityProfile, Address
                
                # Prepare profile data
                identity_data['user_id'] = user.id
                
                # Create address if present
                new_address = None
                if address_data:
                    new_address = Address(**address_data)
                
                new_identity = UserIdentityProfile(**identity_data)
                if new_address:
                    new_identity.address = new_address
                    
                user.identity_profile = new_identity

        # 4. Handle Health Profile Update
        if health_data:
            if user.health_profile:
                for k, v in health_data.items():
                    setattr(user.health_profile, k, v)
            else:
                from app.models.user_profile import UserHealthProfile
                health_data['user_id'] = user.id
                new_health = UserHealthProfile(**health_data)
                user.health_profile = new_health

        # 5. Flush changes
        await self.user_repo.session.flush()
        await self.user_repo.session.refresh(user)

        logger.info(f"Admin updated user: {user_id}")

        # 6. Re-fetch with full relationship
        updated_user = await self.user_repo.get_user_with_profiles(user_id)

        # Invalidate caches
        await redis_service.delete_pattern(RedisKeys.ADMIN_USERS_LIST_WILDCARD)
        await redis_service.delete_pattern(RedisKeys.admin_user_detail_key(str(user_id)))

        return updated_user


    async def delete_user_by_admin(self, user_id: UUID):
        """Delete a user by an admin. Using soft_delete."""
        # soft_delete returns False if user doesn't exist OR is already deleted
        deleted = await self.user_repo.soft_delete(user_id)
        
        if not deleted:
             # Optimization: soft_delete failure implies user is not found or already deleted.
             # No need for an extra SELECT query to confirm.
             raise NotFound(f"User with id {user_id} not found")

        # Invalidate caches
        await redis_service.delete_pattern(RedisKeys.ADMIN_USERS_LIST_WILDCARD)
        await redis_service.delete_pattern(RedisKeys.admin_user_detail_key(str(user_id)))

        logger.info(f"Admin deleted user: {user_id}")



class AdminGroupService:
    def __init__(
        self,
        user_repository: UserRepository,
        member_repo: GroupMembershipRepository,
        group_repo: FamilyGroupRepository
    ):
        self.user_repo = user_repository
        self.member_repo = member_repo
        self.group_repo = group_repo

    # ===== Group Management by Admin =====

    async def get_all_groups_paginated(self, page: int = 1, page_size: int = 20):
        """Fetch all groups with pagination."""
        from sqlalchemy.orm import selectinload
        from app.models.family_group import FamilyGroup
        load_options = [
            selectinload(FamilyGroup.creator),
            selectinload(FamilyGroup.group_memberships).selectinload(GroupMembership.user)
        ]
        paginated_result = await self.group_repo.get_paginated(
            page=page,
            page_size=page_size,
            load_options=load_options
        )
        return paginated_result.items, paginated_result.total_items


    async def get_group_with_details(self, group_id: UUID):
        """Fetch a specific group by ID."""
        group = await self.group_repo.get_with_details(group_id)
        if not group:
            raise NotFound(f"Group with id {group_id} not found")
        return group


    async def update_group_by_admin(self, group_id: UUID, update_data):
        """Update a specific group. Optimized to single DB round-trip."""
        from sqlalchemy.orm import selectinload
        from app.models.family_group import FamilyGroup
        
        load_options = [
            selectinload(FamilyGroup.creator),
            selectinload(FamilyGroup.group_memberships).selectinload(GroupMembership.user)
        ]
        
        # Update and fetch with details in one go
        updated_group = await self.group_repo.update(group_id, update_data, load_options=load_options)
        
        if not updated_group:
            raise NotFound(f"Group with id {group_id} not found")

        # Invalidate caches
        await redis_service.delete_pattern(RedisKeys.ADMIN_GROUPS_LIST_WILDCARD)
        await redis_service.delete_pattern(RedisKeys.admin_group_detail_key(str(group_id)))

        return updated_group


    async def delete_group_by_admin(self, group_id: UUID):
        """Delete a specific group."""
        group = await self.group_repo.get_by_id(group_id)
        if not group:
            raise NotFound(f"Group with id {group_id} not found")
        await self.group_repo.delete(group_id)
        
        # Invalidate caches
        await redis_service.delete_pattern(RedisKeys.ADMIN_GROUPS_LIST_WILDCARD)
        await redis_service.delete_pattern(RedisKeys.admin_group_detail_key(str(group_id)))


    # ===== Group Membership Management by Admin =====

    async def add_member_by_admin(
        self,
        group_id: UUID,
        identifier: str,
        added_by_user_id: UUID
    ) -> GroupMembership:
        """Admin adds member directly. Optimized with fewer DB queries."""
        # 1. Fetch user (Required to get UUID)
        user_to_add = await self.user_repo.get_by_identifier(identifier)
        if not user_to_add:
            raise NotFound(f"User with identifier '{identifier}' not found.")

        # 2. Try to add membership directly
        # Optimization: We skip the "get_membership" check and rely on DB Unique Constraint.
        # We also pass the user object to avoid a redundant SELECT in the repo.
        try:
            membership = await self.member_repo.add_membership(
                user_id=user_to_add.id, 
                group_id=group_id, 
                role=GroupRole.MEMBER, 
                added_by_user_id=added_by_user_id,
                user=user_to_add
            )

            # Invalidate members list cache
            await redis_service.delete_pattern(RedisKeys.admin_group_members_list_key(str(group_id)))

            return membership
        except IntegrityError:
            # This happens if (user_id, group_id) already exists in the database
            raise Conflict("User is already a member of this group.")
        except Exception as e:
            logger.error(f"Error adding member to group {group_id} for user {user_to_add.id}: {str(e)}", exc_info=True)
            raise

    async def remove_member_by_admin(
        self,
        group_id: UUID,
        user_id: UUID
    ):
        """Admin removes member directly."""
        existing = await self.member_repo.get_membership(user_id, group_id)
        if not existing:
             raise NotFound("Membership not found.")

        await self.member_repo.remove_membership(user_id, group_id)

        # Invalidate members list cache
        await redis_service.delete_pattern(RedisKeys.admin_group_members_list_key(str(group_id)))


    async def update_member_role_by_admin(self, group_id: UUID, user_id: UUID, new_role: GroupRole):
        """Admin updates member role directly."""
        try:
            membership = await self.member_repo.update_role(user_id, group_id, new_role)
            if not membership:
                raise NotFound("Membership not found.")
            
            # Invalidate members list cache
            await redis_service.delete_pattern(RedisKeys.admin_group_members_list_key(str(group_id)))

            return membership
        except Exception as e:
            logger.error(f"Error updating member role for user {user_id} in group {group_id}: {str(e)}", exc_info=True)
            raise


    async def get_group_members(self, group_id: UUID) -> Sequence[GroupMembership]:
        """Get all members of a specific group."""
        members = await self.member_repo.get_all_members(group_id)
        return members