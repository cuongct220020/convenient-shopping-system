# user-service/app/views/users/me_tag_view.py
from sanic import Request
from sanic_ext import openapi

from app.decorators import validate_request
from app.views.base_view import BaseAPIView

from app.schemas.user_tag_schema import (
    UserTagBulkAddSchema,
    UserTagDeleteSchema,
    UserTagUpdateByCategorySchema
)
from app.services.user_tag_service import UserTagService
from app.repositories.user_tag_repository import UserTagRepository

from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Me Tag View")


class MeTagsView(BaseAPIView):
    """
    GET /users/me/tags - Get all user's tags grouped by category
    POST /users/me/tags - Add tags to user
    """
    @openapi.summary("Get current user's tags")
    @openapi.description("Retrieves all tags for the authenticated user, grouped by category.")
    @openapi.tag("Profile - Tags")
    async def get(self, request: Request):
        """Get all tags for current user, grouped by category."""
        user_id = request.ctx.auth_payload["sub"]

        # Initialize dependencies
        user_tag_repo = UserTagRepository(session=request.ctx.db_session)
        user_tag_service = UserTagService(user_tag_repo)

        try:
            # Get tags
            tags_response = await user_tag_service.get_user_tags_grouped(user_id)

            # Use helper method from base class
            return self.success_response(
                data=tags_response,
                message="Successfully fetched user tags",
                status_code=200
            )
        except Exception as e:
            logger.error("Failed to fetch user tags", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to fetch user tags",
                status_code=500
            )

    @openapi.summary("Add tags to user")
    @openapi.description("Adds one or more tags to the authenticated user's profile.")
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
            logger.error("Failed to add tags", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to add tags",
                status_code=500
            )


class MeTagsCategoryView(BaseAPIView):
    """
    PUT /users/me/tags/category/{category} - Update tags in specific category
    """
    @openapi.summary("Update tags in specific category")
    @openapi.description("Replaces all tags in a specific category with new ones.")
    @openapi.tag("Profile - Tags")
    @validate_request(UserTagUpdateByCategorySchema)
    async def put(self, request: Request, category: str):
        """Update all tags in a specific category."""
        user_id = request.ctx.auth_payload["sub"]
        data = request.ctx.validated_data

        # Initialize dependencies
        user_tag_repo = UserTagRepository(session=request.ctx.db_session)
        user_tag_service = UserTagService(user_tag_repo)

        try:
            # Update category tags
            result = await user_tag_service.update_category_tags(
                user_id, 
                category, 
                data.tag_values
            )

            # Use helper method from base class
            return self.success_response(
                data=result,
                message=f"Category '{category}' tags updated successfully",
                status_code=200
            )
        except Exception as e:
            logger.error(f"Failed to update category '{category}' tags", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message=f"Failed to update category '{category}' tags",
                status_code=500
            )


class MeTagsDeleteView(BaseAPIView):
    """
    POST /users/me/tags/delete - Remove tags from user
    (Using POST instead of DELETE to accept request body)
    """
    @openapi.summary("Delete user's tags")
    @openapi.description("Deletes one or more tags from the authenticated user's profile.")
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
            logger.error("Failed to remove tags", exc_info=e)
            # Use helper method from base class
            return self.error_response(
                message="Failed to delete tags",
                status_code=500
            )