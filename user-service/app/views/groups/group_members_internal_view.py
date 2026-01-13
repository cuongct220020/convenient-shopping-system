from uuid import UUID
from sanic import Request
from sanic_ext.extensions.openapi.definitions import Response
from sanic_ext import openapi

from app.views.groups.base_group_view import BaseGroupView
from app.schemas.family_group_schema import FamilyGroupDetailedSchema
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.openapi_utils import get_openapi_body
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.exceptions import NotFound


logger = get_logger("Internal Group Members View")


class InternalGroupMembersView(BaseGroupView):
    """
    INTERNAL endpoint for service-to-service calls.
    Bypasses JWT middleware via user-service IGNORE_PREFIXES on /groups/internal.
    """

    @openapi.definition(
        summary="[INTERNAL] List all members in a family group",
        description="Internal endpoint to retrieve group_name and members list for a specific group.",
        tag=["Internal Group Authorization"],
        response=[
            Response(
                content=get_openapi_body(GenericResponse[FamilyGroupDetailedSchema]),
                status=200,
                description="Successfully retrieved group members.",
            ),
            Response(
                content=get_openapi_body(GenericResponse),
                status=404,
                description="Group not found.",
            )
        ]
    )
    async def get(self, request: Request, group_id: UUID):
        service = self._get_service(request)

        try:
            group = await service.get_group_with_members(group_id)
            group_detailed = FamilyGroupDetailedSchema.model_validate(group)

            return self.success_response(
                data=group_detailed,
                message="Group members retrieved successfully.",
                status_code=200
            )
        except NotFound:
            return self.error_response(
                message="Group not found.",
                status_code=404
            )
        except Exception as e:
            logger.error("Error retrieving internal group members.", exc_info=e)
            return self.error_response(
                message="Failed to retrieve group members.",
                status_code=500
            )


