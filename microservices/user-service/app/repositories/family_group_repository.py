from app.models import FamilyGroup
from app.schemas import FamilyGroupCreateSchema, FamilyGroupUpdateSchema
from app.schemas.family_group import FamilyGroupUpdateSchema
from shopping_shared.databases.base_repository import BaseRepository


class FamilyGroupRepository(BaseRepository[FamilyGroup, FamilyGroupCreateSchema, FamilyGroupUpdateSchema]):
    pass
