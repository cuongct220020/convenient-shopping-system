# user-service/app/views/users/me_tag_view.py
from sanic import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request
from app.views.base_view import BaseAPIView

from app.schemas.user_tag_schema import (
    UserTagBulkAddSchema,
    UserTagDeleteSchema,
    UserTagUpdateByCategorySchema,
    UserTagsResponseSchema
)
from app.services.user_tag_service import UserTagService
from app.repositories.user_tag_repository import UserTagRepository

from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body

logger = get_logger("Me Tag View")


class MeTagsView(BaseAPIView):

    @openapi.definition(
        summary="Retrieve authenticated user's tags",
        description="Retrieves all tags associated with the authenticated user, organized and grouped by their respective categories for better organization and management.",
        tag=["User Profile Tags"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserTagsResponseSchema),
                status=200,
                description="Successfully retrieved all tags for the authenticated user, grouped by category.",
            )
        ]
    )
    async def get(self, request: Request):
        """
        Get all tags for current user, grouped by category.
        GET /api/v1/user-service/users/me/tags
        """
        user_id = request.ctx.auth_payload["sub"]

        # Initialize dependencies
        user_tag_repo = UserTagRepository(session=request.ctx.db_session)
        user_tag_service = UserTagService(user_tag_repo)

        try:
            # Get tags
            tags_response = await user_tag_service.get_user_tags_grouped(user_id)

            # Use helper method from base class
            return self.success_response(
                data=UserTagsResponseSchema.model_validate(tags_response),
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


    @openapi.definition(
        summary="Add tags to authenticated user's profile",
        description="Adds one or more tags to the authenticated user's profile. This endpoint allows users to enhance their profile with custom tags for better categorization and personalization.",
        body=get_openapi_body(UserTagBulkAddSchema),
        tag=["User Profile Tags"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserTagsResponseSchema),
                status=201,
                description="Successfully added tags to the user's profile and returned the updated tag list.",
            )
        ]
    )
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
            await user_tag_service.add_tags(user_id, data)

            # Get updated user tags to return complete information
            updated_tags = await user_tag_service.get_user_tags_grouped(user_id)

            # Use helper method from base class
            return self.success_response(
                data=UserTagsResponseSchema.model_validate(updated_tags),
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
    @openapi.definition(
        summary="Update tags in a specific category",
        description="Replaces all existing tags in a specific category with new ones for the authenticated user. This operation completely overwrites the tags in the specified category.",
        body=get_openapi_body(UserTagUpdateByCategorySchema),
        tag=["User Profile Tags"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserTagsResponseSchema),
                status=200,
                description="Successfully updated tags in the specified category and returned the updated user tag list.",
            )
        ]

    )
    @validate_request(UserTagUpdateByCategorySchema)
    async def put(self, request: Request, category: str):
        """
        Update all tags in a specific category.
        PUT /users/me/tags/category/{category} - Update tags in specific category
        """
        user_id = request.ctx.auth_payload["sub"]
        data = request.ctx.validated_data

        # Initialize dependencies
        user_tag_repo = UserTagRepository(session=request.ctx.db_session)
        user_tag_service = UserTagService(user_tag_repo)

        try:
            # Update category tags
            await user_tag_service.update_category_tags(
                user_id,
                category,
                data.tag_values
            )

            # Get updated user tags to return complete information
            updated_tags = await user_tag_service.get_user_tags_grouped(user_id)

            # Use helper method from base class
            return self.success_response(
                data=UserTagsResponseSchema.model_validate(updated_tags),
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

    @openapi.definition(
        summary="Remove tags from authenticated user's profile",
        description="Deletes one or more specified tags from the authenticated user's profile. This operation removes the selected tags and returns the updated tag list.",
        body=get_openapi_body(UserTagDeleteSchema),
        tag=["User Profile Tags"],
        secured={"bearerAuth": []},
        response=[
            Response(
                content=get_openapi_body(UserTagsResponseSchema),
                status=200,
                description="Successfully removed tags from the user's profile and returned the updated tag list.",
            )
        ]
    )
    @validate_request(UserTagDeleteSchema)
    async def post(self, request: Request):
        """
        Remove tags from current user. Using POST instead of DELETE to accept request body)
        POST /api/v1/user-service/users/me/tags/delete
        """
        user_id = request.ctx.auth_payload["sub"]
        validated_data = request.ctx.validated_data

        user_tag_repo = UserTagRepository(session=request.ctx.db_session)
        user_tag_service = UserTagService(user_tag_repo)

        try:
            # Remove tags
            await user_tag_service.remove_tags(user_id, validated_data)

            # Get updated user tags to return complete information
            updated_tags = await user_tag_service.get_user_tags_grouped(user_id)

            # Use helper method from base class
            return self.success_response(
                data=UserTagsResponseSchema.model_validate(updated_tags),
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