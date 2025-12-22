from app.models import UserIdentityProfile, UserHealthProfile
from app.schemas import UserIdentityProfileSchema, UserIdentityProfileUpdateSchema, UserHealthProfileUpdateSchema
from shopping_shared.databases.base_repository import BaseRepository


class UserIdentityProfileRepository(BaseRepository[UserIdentityProfile, UserIdentityProfileUpdateSchema, ...]):
    """
    Repository for UserIdentityProfile model.
    Uses UpdateSchema for both Create and Update since profiles are typically updated/created together with user data
    """

    pass


class UserHealthProfileRepository(BaseRepository[UserHealthProfile, UserHealthProfileUpdateSchema, ...]):
    pass
