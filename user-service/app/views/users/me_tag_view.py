# user-service/app/views/users/me_tag_view.py
from uuid import UUID
from sanic import Request
from sanic.views import HTTPMethodView
from sanic.response import json

from app.decorators import validate_request
from shopping_shared.exceptions import BadRequest

from app.schemas.user_tag_schema import (
    UserTagBulkAddSchema,
    UserTagDeleteSchema
)
from app.services.user_tag_service import UserTagService
from app.repositories.user_tag_repository import UserTagRepository

from shopping_shared.schemas.response_schema import GenericResponse


class MeTagsView(HTTPMethodView):
    """
    GET /users/me/tags - Get all user's tags grouped by category
    POST /users/me/tags - Add tags to user
    """
    @staticmethod
    async def get(request: Request):
        """Get all tags for current user, grouped by category."""
        user_id  = request.ctx.auth_payload["sub"]

        # Initialize dependencies
        user_tag_repo = UserTagRepository(session=request.ctx.db_session)
        user_tag_service = UserTagService(user_tag_repo)

        # Get tags
        tags_grouped = await user_tag_service.get_user_tags_grouped(user_id)

        response = GenericResponse(
            status="success",
            message="Successfully fetched user tags",
            data=tags_grouped
        )

        return json(response.model_dump(exclude_none=True), status=200)

    @validate_request(UserTagBulkAddSchema)
    async def post(self, request: Request):
        """Add tags to current user."""
        user_id = request.ctx.auth_payload["sub"]
        data = request.ctx.validated_data

        # Initialize dependencies
        user_tag_repo = UserTagRepository(session=request.ctx.db_session)
        user_tag_service = UserTagService(user_tag_repo)

        # Add tags
        result = await user_tag_service.add_tags(user_id, data)

        response = GenericResponse(
            status="success",
            message="Tags added successfully",
            data=result
        )

        return json(response.model_dump(exclude_none=True), status=201)


class MeTagsDeleteView(HTTPMethodView):
    """
    POST /users/me/tags/delete - Remove tags from user
    (Using POST instead of DELETE to accept request body)
    """
    @validate_request(UserTagDeleteSchema)
    async def post(self, request: Request):
        """Remove tags from current user."""
        user_id = request.ctx.auth_payload["sub"]

        data = request.ctx.validated_data

        user_tag_repo = UserTagRepository(session=request.ctx.db_session)
        user_tag_service = UserTagService(user_tag_repo)

        result = await user_tag_service.remove_tags(user_id, data)

        response = GenericResponse(
            status="success",
            message="Tags deleted successfully",
            data=result
        )

        return json(response.model_dump(exclude_none=True), status=200)

