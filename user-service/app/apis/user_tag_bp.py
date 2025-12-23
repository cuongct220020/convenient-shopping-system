# user-service/app/apis/user_tag_bp.py
from uuid import UUID
from sanic import Blueprint, Request, json
from sanic.log import logger

from shopping_shared.exceptions import BadRequest

from app.schemas.user_tag_schema import (
    UserTagBulkAddSchema,
    UserTagDeleteSchema,
    UserTagUpdateByCategorySchema
)
from app.services.user_tag_service import UserTagService
from app.repositories.user_tag_repository import UserTagRepository


user_tag_bp = Blueprint("user_tags", url_prefix="/users/me/tags")


@user_tag_bp.get("")
async def get_user_tags(request: Request):
    """
    GET /users/me/tags
    Get all tags for current user, grouped by category.
    """
    user_id: UUID = request.ctx.user["user_id"]

    # Initialize dependencies
    user_tag_repo = UserTagRepository(request.ctx.db_session)
    user_tag_service = UserTagService(user_tag_repo)

    # Get tags
    tags_grouped = await user_tag_service.get_user_tags_grouped(user_id)

    return json({
        "data": tags_grouped.model_dump()
    }, status=200)


@user_tag_bp.post("")
async def add_user_tags(request: Request):
    """
    POST /users/me/tags
    Add tags to current user.
    """
    user_id: UUID = request.ctx.user["user_id"]

    # Validate request body
    try:
        data = UserTagBulkAddSchema(**request.json)
    except Exception as e:
        raise BadRequest(str(e))

    # Initialize dependencies
    user_tag_repo = UserTagRepository(request.ctx.db_session)
    user_tag_service = UserTagService(user_tag_repo)

    # Add tags
    result = await user_tag_service.add_tags(user_id, data)

    return json({
        "message": "Tags added successfully",
        "data": result
    }, status=201)


@user_tag_bp.delete("")
async def delete_user_tags(request: Request):
    """
    DELETE /users/me/tags
    Remove tags from current user.
    """
    user_id: UUID = request.ctx.user["user_id"]

    # Validate request body
    try:
        data = UserTagDeleteSchema(**request.json)
    except Exception as e:
        raise BadRequest(str(e))

    # Initialize dependencies
    user_tag_repo = UserTagRepository(request.ctx.db_session)
    user_tag_service = UserTagService(user_tag_repo)

    # Delete tags
    result = await user_tag_service.remove_tags(user_id, data)

    return json({
        "message": "Tags deleted successfully",
        "data": result
    }, status=200)


@user_tag_bp.put("/category")
async def update_tags_by_category(request: Request):
    """
    PUT /users/me/tags/category
    Replace all tags in a specific category.
    """
    user_id: UUID = request.ctx.user["user_id"]

    # Validate request body
    try:
        data = UserTagUpdateByCategorySchema(**request.json)
    except Exception as e:
        raise BadRequest(str(e))

    # Initialize dependencies
    user_tag_repo = UserTagRepository(request.ctx.db_session)
    user_tag_service = UserTagService(user_tag_repo)

    # Update tags
    result = await user_tag_service.update_tags_by_category(user_id, data)

    return json({
        "message": f"Tags in category '{data.category}' updated successfully",
        "data": result
    }, status=200)

