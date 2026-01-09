# user-service/app/views/groups/group_access_view.py
from uuid import UUID

from sanic import Request
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request
from app.views.groups.base_group_view import BaseGroupView
from app.schemas.family_group_schema import GroupAccessCheckSchema
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.openapi_utils import get_openapi_body


class GroupAccessCheckView(BaseGroupView):

    @openapi.definition(
        summary="[INTERNAL] Check group access and Head Chef role",
        description="Internal endpoint to validate group existence, user membership, and optionally verify Head Chef role",
        tag=["Internal Group Authorization"],
        body=get_openapi_body(GroupAccessCheckSchema),
        response = [
            Response(content=get_openapi_body(GenericResponse), status=200, description="User has valid access (and is Head Chef if required)"),
            Response(content=get_openapi_body(GenericResponse), status=403, description="User is not Head Chef when required"),
            Response(content=get_openapi_body(GenericResponse), status=404, description="Group or membership not found.")
        ]
    )
    @validate_request(GroupAccessCheckSchema)
    async def post(
        self,
        request: Request,
        group_id: UUID,
        user_id: UUID
    ):
        check_head_chef = request.ctx.validated_data.check_head_chef
        service = self._get_service(request)

        is_member, is_head_chef = await service.check_group_access(
            user_id=user_id,
            group_id=group_id,
            check_head_chef=check_head_chef
        )

        # If checking head chef, user must be both a member and head chef
        if check_head_chef:
            if is_member and is_head_chef:
                return self.success_response(
                    data={"authorized": True, "is_head_chef": True, "is_member": True},
                    message="User is the head chef of this group"
                )
            elif is_member and not is_head_chef:
                return self.fail_response(
                    data={"authorized": False, "is_head_chef": False, "is_member": True},
                    message="User is a member but not the head chef of this group",
                    status_code=403
                )
            else:
                return self.fail_response(
                    data={"authorized": False, "is_head_chef": False, "is_member": False},
                    message="User is not a member of this group",
                    status_code=404
                )
        else:
            # If not checking head chef, just check if user is a member
            if is_member:
                return self.success_response(
                    data={"authorized": True, "is_head_chef": is_head_chef, "is_member": True},
                    message="User is a member of this group"
                )
            else:
                return self.fail_response(
                    data={"authorized": False, "is_head_chef": False, "is_member": False},
                    message="User is not a member of this group",
                    status_code=404
                )