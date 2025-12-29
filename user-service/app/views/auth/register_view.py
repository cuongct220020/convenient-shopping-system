# user-service/app/views/auth/register_view.py
from sanic.request import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import validate_request, idempotent
from app.views.base_view import BaseAPIView
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCoreInfoSchema
from app.schemas.auth_schema import  RegisterRequestSchema
from app.services.auth_service import AuthService
from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.utils.openapi_utils import get_openapi_body


class RegisterView(BaseAPIView):


    @openapi.definition(
        summary="Create a new user account",
        description="Registers a new user account with the provided information. The account is created in an inactive state and a verification OTP is sent to the user's email address for account activation.",
        body=get_openapi_body(RegisterRequestSchema),
        tag=["Authentication"],
        response=[
            Response(content=get_openapi_body(UserCoreInfoSchema), status=201, description="User account created successfully. Verification OTP sent to the provided email address."),
            Response(content=get_openapi_body(GenericResponse), status=400, description="Invalid registration data or user already exists."),
        ]
    )
    @validate_request(RegisterRequestSchema)
    @idempotent()
    async def post(self, request: Request):
        """
        Handles new user registration.
        POST /api/v1/user-service/auth/register
        """
        validated_data = request.ctx.validated_data

        user_repo = UserRepository(session=request.ctx.db_session)

        # Service now returns the created User object
        user = await AuthService.register_account(
            reg_data=validated_data,
            user_repo=user_repo
        )

        # Use helper method from base class
        return self.success_response(
            data=UserCoreInfoSchema(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone_num=user.phone_num,
                avatar_url=user.avatar_url
            ),
            message="Registration successful. Please check your email for a verification OTP.",
            status_code=201
        )