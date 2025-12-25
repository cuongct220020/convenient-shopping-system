# user-service/app/views/users/me_change_email_view.py
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView


from app.decorators.validate_request import validate_request
from app.repositories.user_repository import UserRepository
from app.schemas import RequestEmailChangeSchema, ConfirmEmailChangeSchema, UserInfoUpdateSchema
from app.services.otp_service import otp_service
from app.enums import OtpAction
from app.services.kafka_service import kafka_service

from shopping_shared.schemas.response_schema import GenericResponse
from shopping_shared.exceptions import BadRequest



class MeRequestChangeEmailView(HTTPMethodView):

    @validate_request(RequestEmailChangeSchema)
    async def post(self, request: Request):
        """Step 1: Request an OTP to change email."""
        new_email = request.ctx.validated_data.new_email

        # We can reuse OTP service
        otp_code = await otp_service.generate_and_store_otp(
            email=str(new_email),
            action=str(OtpAction.CHANGE_EMAIL.value),
            data=None
        )

        await kafka_service.publish_message(
            new_email=str(new_email),
            otp_code=str(otp_code),
            action=str(OtpAction.CHANGE_EMAIL.value)
        )

        response = GenericResponse(
            status="success",
            message="OTP sent to your new email address.",
            data=None
        )

        return json(response.model_dump(mode='json'), status=200)




class MeConfirmChangeEmailView(HTTPMethodView):

    @validate_request(ConfirmEmailChangeSchema)
    async def post(self, request: Request):
        """Step 2: Confirm email change with OTP."""
        user_id = request.ctx.auth_payload["sub"]
        new_email = request.ctx.validated_data.new_email
        summited_otp_code = request.ctx.validated_data.otp_code
        
        # Verify OTP
        is_valid = await otp_service.verify_otp(
            email=str(new_email),
            action=OtpAction.CHANGE_EMAIL.value,
            submitted_code=summited_otp_code
        )
        
        if not is_valid:
            raise BadRequest("Invalid or expired OTP code.")

        # Update User Email
        user_repo = UserRepository(request.ctx.db_session)
        await user_repo.update(user_id, UserInfoUpdateSchema(email=new_email))

        response = GenericResponse(
            status="success",
            message="Email updated successfully.",
            data=None
        )

        return json(response.model_dump(mode='json'), status=200)