from sanic import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from shopping_shared.exceptions import NotFound
from shopping_shared.schemas.response_schema import GenericResponse

from app.decorators.validate_request import validate_request
from app.repositories.user_profile_repository import (
    UserIdentityProfileRepository,
    UserHealthProfileRepository
)
from app.services.user_profile_service import (
    UserIdentityProfileService,
    UserHealthProfileService
)
from app.schemas import (
    UserIdentityProfileSchema,
    UserIdentityProfileUpdateSchema,
    UserHealthProfileSchema,
    UserHealthProfileUpdateSchema,
)

from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Me Profile View")


class MeIdentityProfileView(HTTPMethodView):

    @staticmethod
    async def get(request: Request):
        """Retrieves the identity profile of the authenticated user."""
        user_id = request.ctx.auth_payload["sub"]
        
        user_identity_profile_repo = UserIdentityProfileRepository(session=request.ctx.db_session)
        user_identity_profile_service = UserIdentityProfileService(user_identity_profile_repo)

        try:
            profile = await user_identity_profile_service.get(user_id)
            data = UserIdentityProfileSchema.model_validate(profile)
        except NotFound:
            raise NotFound("Identity profile not found.")

        response = GenericResponse(
            status="success",
            message="Identity profile found",
            data=data
        )

        return json(response.model_dump(exclude_none=True), status=200)


    @validate_request(UserIdentityProfileUpdateSchema)
    async def patch(self, request: Request):
        """Updates the identity profile of the authenticated user."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        repo = UserIdentityProfileRepository(request.ctx.db_session)
        service = UserIdentityProfileService(repo)

        # Check if exists, if not create (Upsert logic often preferred for profiles)
        try:
            # Try update first
            updated_profile = await service.update(user_id, validated_data)
        except NotFound:
            logger.warning(f"Identity profile for user_id {user_id} not found. Creating new profile.")
            create_data = validated_data.model_dump()
            create_data['user_id'] = user_id
            updated_profile = await repo.create(create_data)

        response = GenericResponse(
            status="success",
            message="Identity profile updated.",
            data=UserIdentityProfileSchema.model_validate(updated_profile)
        )
        return json(response.model_dump(exclude_none=True), status=200)


class MeHealthProfileView(HTTPMethodView):

    @staticmethod
    async def get(request: Request):
        """Retrieves the health profile of the authenticated user."""
        user_id = request.ctx.auth_payload["sub"]

        user_health_profile_repo = UserHealthProfileRepository(request.ctx.db_session)
        user_health_service = UserHealthProfileService(user_health_profile_repo)

        try:
            profile = await user_health_service.get(user_id)
            data = UserHealthProfileSchema.model_validate(profile)
        except NotFound:
            raise NotFound("Health profile not found.")

        response = GenericResponse(
            status="success",
            data=data
        )
        return json(response.model_dump(exclude_none=True), status=200)


    @validate_request(UserHealthProfileUpdateSchema)
    async def patch(self, request: Request):
        """Updates the health profile of the authenticated user."""
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        user_health_profile_repo = UserHealthProfileRepository(request.ctx.db_session)
        user_health_service = UserHealthProfileService(user_health_profile_repo)

        try:
            updated_profile = await user_health_service.update(user_id, validated_data)
        except NotFound:
            # Upsert logic
            create_data = validated_data.model_dump()
            create_data['user_id'] = user_id
            updated_profile = await user_health_profile_repo.create(create_data)

        response = GenericResponse(
            status="success",
            message="Health profile updated.",
            data=UserHealthProfileSchema.model_validate(updated_profile)
        )

        return json(response.model_dump(exclude_none=True), status=200)