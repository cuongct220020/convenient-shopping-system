

from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreateSchema
from app.utils.password_utils import hash_password
from shopping_shared.exceptions import Conflict, NotFound
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Admin Service")

class AdminService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository


    async def get_user_by_admin(self, user_id):
        """Fetch a user by ID for admin."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFound(f"User with id {user_id} not found")
        return user

    async def create_user_by_admin(self, user_data: UserCreateSchema):
        """Creates a new user by an admin."""
        existing_user = await self.user_repository.get_by_username(user_data.username)
        if existing_user:
            raise Conflict(f"User with username {user_data.username} already exists.")

        # Hash password (handle SecretStr properly)
        password_str = user_data.password.get_secret_value() if hasattr(user_data.password, 'get_secret_value') else str(user_data.password)
        hashed_password = hash_password(password_str)

        # Convert schema to dict and inject hashed password
        new_user_data = user_data.model_dump(exclude={'password'})
        new_user_data['password_hash'] = hashed_password

        # Create user via direct session (association table pattern)
        from app.models.user import User as UserModel

        user = UserModel(**new_user_data)
        self.user_repository.session.add(user)
        await self.user_repository.session.flush()
        await self.user_repository.session.refresh(user)

        logger.info(f"Admin created user: {user.username}")
        return user

    async def update_user_by_admin(self, user_id: UUID, update_data: UserUpdateSchema) -> User:
        """Updates a user's information by an admin."""
        user = await self.repository.update(user_id, update_data)
        if not user:
            raise NotFound(f"User with id {user_id} not found")

        logger.info(f"Admin updated user: {user_id}")
        return user
