# user-service/app/views/users/me_tag_view.py
from sanic import Request
from sanic.views import HTTPMethodView
from sanic_ext import openapi

from app.decorators import validate_request, api_response
from app.views.base_view import BaseAPIView
from app.decorators.auth_decorators import auth_required

from app.schemas import (
    UserTagBulkAddSchema,
    UserTagDeleteSchema,
    UserTagsResponseSchema,
    CountResponseSchema
)
from app.services.user_tag_service import UserTagService
from app.repositories.user_tag_repository import UserTagRepository

from shopping_shared.sanic.schemas import DocGenericResponse


class MeTagsView(BaseAPIView):
    """
    GET /users/me/tags - Get all user's tags grouped by category
    POST /users/me/tags - Add tags to user
    """
    @openapi.summary("Get current user's tags")
    @openapi.description("Retrieves all tags for the authenticated user, grouped by category.")
    @auth_required()
    @api_response(
        success_schema=UserTagsResponseSchema,
        success_status=200,
        success_description="Successfully fetched user tags"
    )
    @openapi.tag("Profile - Tags")
    async def get(self, request: Request):
        """Get all tags for current user, grouped by category."""
        user_id  = request.ctx.auth_payload["sub"]

        # Initialize dependencies
        user_tag_repo = UserTagRepository(session=request.ctx.db_session)
        user_tag_service = UserTagService(user_tag_repo)

        try:
            # Get tags
            tags_grouped = await user_tag_service.get_user_tags_grouped(user_id)

            # Use helper method from base class
            return self.success_response(
                data=tags_grouped,
                message="Successfully fetched user tags",
                status_code=200
            )
        except Exception as e:
            # Use helper method from base class
            return self.error_response(
                message="Failed to fetch user tags",
                status_code=500
            )

    @openapi.summary("Add tags to user")
    @openapi.description("Adds one or more tags to the authenticated user's profile.")
    @auth_required()
    @api_response(
        success_schema=CountResponseSchema,
        success_status=201,
        success_description="Tags added successfully"
    )
    @openapi.tag("Profile - Tags")
    @validate_request(UserTagBulkAddSchema)
    async def post(self, request: Request):
        """Add tags to current user."""
        user_id = request.ctx.auth_payload["sub"]
        data = request.ctx.validated_data

        # Initialize dependencies
        user_tag_repo = UserTagRepository(session=request.ctx.db_session)
        user_tag_service = UserTagService(user_tag_repo)

        try:
            # Add tags
            result = await user_tag_service.add_tags(user_id, data)

            # Use helper method from base class
            return self.success_response(
                data=result,
                message="Tags added successfully",
                status_code=201
            )
        except Exception as e:
            # Use helper method from base class
            return self.error_response(
                message="Failed to add tags",
                status_code=500
            )


class MeTagsDeleteView(BaseAPIView):
    """
    POST /users/me/tags/delete - Remove tags from user
    (Using POST instead of DELETE to accept request body)
    """
    @openapi.summary("Delete user's tags")
    @openapi.description("Deletes one or more tags from the authenticated user's profile.")
    @auth_required()
    @api_response(
        success_schema=CountResponseSchema,
        success_status=200,
        success_description="Tags deleted successfully"
    )
    @openapi.tag("Profile - Tags")
    @validate_request(UserTagDeleteSchema)
    async def post(self, request: Request):
        """Remove tags from current user."""
        user_id = request.ctx.auth_payload["sub"]

        validated_data = request.ctx.validated_data

        user_tag_repo = UserTagRepository(session=request.ctx.db_session)
        user_tag_service = UserTagService(user_tag_repo)

        try:
            result = await user_tag_service.remove_tags(user_id, validated_data)

            # Use helper method from base class
            return self.success_response(
                data=result,
                message="Tags deleted successfully",
                status_code=200
            )
        except Exception as e:
            # Use helper method from base class
            return self.error_response(
                message="Failed to delete tags",
                status_code=500
            )