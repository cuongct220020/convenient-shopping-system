from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from shopping_shared.schemas.response_schema import GenericResponse, SuccessResponse
from shopping_shared.exceptions import BadRequest

from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.otp_service import otp_service
from app.enums import OtpAction
# Assuming you have schemas for these or use Generic ones
from pydantic import BaseModel, EmailStr

class RequestEmailChangeSchema(BaseModel):
    new_email: EmailStr

class ConfirmEmailChangeSchema(BaseModel):
    new_email: EmailStr
    otp_code: str


class MeRequestChangeEmailView(HTTPMethodView):

    @validate_request(RequestEmailChangeSchema)
    async def post(self, request: Request):
        """Step 1: Request an OTP to change email."""
        user_id = request.ctx.auth_payload["sub"]
        new_email = request.ctx.validated_data.new_email
        
        # We can reuse OTP service
        otp_code = await otp_service.generate_and_store_otp(
            email=new_email, 
            action=OtpAction.CHANGE_EMAIL.value
        )
        
        # Publish to Kafka for notification service to send email
        from app.services.kafka_service import kafka_service
        await kafka_service.publish_user_registration_otp(new_email, otp_code) # Reusing existing method for now

        return json(SuccessResponse(message="OTP sent to your new email address.").model_dump(), status=200)


class MeConfirmChangeEmailView(HTTPMethodView):

    @validate_request(ConfirmEmailChangeSchema)
    async def post(self, request: Request):
        """Step 2: Confirm email change with OTP."""
        user_id = request.ctx.auth_payload["sub"]
        data = request.ctx.validated_data
        
        # Verify OTP
        is_valid = await otp_service.verify_otp(
            email=data.new_email,
            action=OtpAction.CHANGE_EMAIL.value,
            submitted_code=data.otp_code
        )
        
        if not is_valid:
            raise BadRequest("Invalid or expired OTP code.")
            
        # Update User Email
        repo = UserRepository(request.ctx.db_session)
        user = await repo.get_by_id(user_id)
        user.email = data.new_email
        await repo.update(user)

        return json(SuccessResponse(message="Email updated successfully.").model_dump(), status=200)