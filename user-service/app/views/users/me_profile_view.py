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
    UserHealthProfileUpdateSchema
)


class MeIdentityProfileView(HTTPMethodView):

    async def get(self, request: Request):
        """Retrieves the identity profile of the authenticated user."""
        user_id = request.ctx.auth_payload["sub"]
        
        repo = UserIdentityProfileRepository(request.ctx.db_session)
        service = UserIdentityProfileService(repo)

        try:
            profile = await service.get(user_id)
            data = UserIdentityProfileSchema.model_validate(profile)
        except NotFound:
            # If profile doesn't exist, we might return empty or default defaults
            # depending on business rule. Returning empty for now or 404.
            # Assuming 404 is appropriate if not created yet, or create default.
            # Let's return 404 to be explicit.
            raise NotFound("Identity profile not found.")

        response = GenericResponse(
            status="success",
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
            # Create if not exists (Upsert)
            # Note: validated_data is UpdateSchema, Create usually needs UserID
            # We need to inject user_id manually or use a create method
            # For strict typing, we might need to convert UpdateSchema to CreateSchema or dict
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

    async def get(self, request: Request):
        """Retrieves the health profile of the authenticated user."""
        user_id = request.ctx.auth_payload["sub"]

        repo = UserHealthProfileRepository(request.ctx.db_session)
        service = UserHealthProfileService(repo)

        try:
            profile = await service.get(user_id)
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

        repo = UserHealthProfileRepository(request.ctx.db_session)
        service = UserHealthProfileService(repo)

        try:
            updated_profile = await service.update(user_id, validated_data)
        except NotFound:
            # Upsert logic
            create_data = validated_data.model_dump()
            create_data['user_id'] = user_id
            updated_profile = await repo.create(create_data)

        response = GenericResponse(
            status="success",
            message="Health profile updated.",
            data=UserHealthProfileSchema.model_validate(updated_profile)
        )
        return json(response.model_dump(exclude_none=True), status=200)