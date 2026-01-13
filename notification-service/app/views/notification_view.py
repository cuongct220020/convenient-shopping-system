# notification-service/app/views/notification_view.py
from typing import List
from uuid import UUID
from sanic import Request
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.views.base_view import BaseAPIView
from app.services.notification_service import NotificationService
from app.schemas.notification_schema import NotificationResponseSchema
from shopping_shared.utils.logger_utils import get_logger
from shopping_shared.utils.openapi_utils import get_openapi_body

logger = get_logger("Notification View")


class NotificationListView(BaseAPIView):
    """View for listing user's notifications."""

    @openapi.definition(
        summary="Get user's notifications",
        description="Retrieves all notifications for a specific user, ordered by creation date (newest first).",
        tag=["Notifications"],
        response=[
            Response(
                content=get_openapi_body(List[NotificationResponseSchema]),
                status=200,
                description="Successfully retrieved notifications.",
            ),
            Response(
                content=get_openapi_body(dict),
                status=400,
                description="Invalid user_id parameter.",
            )
        ]
    )
    async def get(self, request: Request, user_id: UUID):
        """Get all notifications for a specific user."""
        try:
            requesting_user_id = getattr(request.ctx, "auth_payload", {}).get("sub")
            if requesting_user_id and str(requesting_user_id) != str(user_id):
                return self.fail_response(
                    message="Forbidden",
                    status_code=403
                )

            # Initialize dependencies
            notification_service = NotificationService(request.ctx.db_session)
            
            # Get notifications
            notifications = await notification_service.get_notifications_by_user_id(user_id)
            
            return self.success_response(
                data=notifications,
                message="Notifications retrieved successfully",
                status_code=200
            )
        except ValueError as e:
            logger.error(f"Invalid user_id parameter: {e}")
            return self.fail_response(
                message="Invalid user_id parameter",
                status_code=400
            )
        except Exception as e:
            logger.error(f"Failed to retrieve notifications for user {user_id}: {e}", exc_info=True)
            return self.error_response(
                message="Failed to retrieve notifications",
                status_code=500
            )


class NotificationReadView(BaseAPIView):
    """View for marking notifications as read."""

    @openapi.definition(
        summary="Mark notification as read",
        description="Marks a specific notification as read. Only the owner of the notification can mark it as read.",
        tag=["Notifications"],
        response=[
            Response(
                content=get_openapi_body(NotificationResponseSchema),
                status=200,
                description="Notification marked as read successfully.",
            ),
            Response(
                content=get_openapi_body(dict),
                status=404,
                description="Notification not found or not authorized.",
            ),
            Response(
                content=get_openapi_body(dict),
                status=400,
                description="Invalid parameters.",
            )
        ]
    )
    async def patch(self, request: Request, notification_id: int, user_id: UUID):
        """Mark a notification as read."""
        try:
            requesting_user_id = getattr(request.ctx, "auth_payload", {}).get("sub")
            if requesting_user_id and str(requesting_user_id) != str(user_id):
                return self.fail_response(
                    message="Forbidden",
                    status_code=403
                )

            # Initialize dependencies
            notification_service = NotificationService(request.ctx.db_session)
            
            # Mark as read
            notification = await notification_service.mark_notification_as_read(notification_id, user_id)
            
            if notification:
                return self.success_response(
                    data=notification,
                    message="Notification marked as read successfully",
                    status_code=200
                )
            else:
                return self.fail_response(
                    message="Notification not found or not authorized",
                    status_code=404
                )
        except ValueError as e:
            logger.error(f"Invalid parameters: {e}")
            return self.fail_response(
                message="Invalid parameters",
                status_code=400
            )
        except Exception as e:
            logger.error(f"Failed to mark notification {notification_id} as read: {e}", exc_info=True)
            return self.error_response(
                message="Failed to mark notification as read",
                status_code=500
            )


class NotificationDeleteView(BaseAPIView):
    """View for deleting notifications."""

    @openapi.definition(
        summary="Delete notification",
        description="Deletes a specific notification. Only the owner of the notification can delete it.",
        tag=["Notifications"],
        response=[
            Response(
                content=get_openapi_body(dict),
                status=200,
                description="Notification deleted successfully.",
            ),
            Response(
                content=get_openapi_body(dict),
                status=404,
                description="Notification not found or not authorized.",
            ),
            Response(
                content=get_openapi_body(dict),
                status=400,
                description="Invalid parameters.",
            )
        ]
    )
    async def delete(self, request: Request, notification_id: int, user_id: UUID):
        """Delete a notification."""
        try:
            requesting_user_id = getattr(request.ctx, "auth_payload", {}).get("sub")
            if requesting_user_id and str(requesting_user_id) != str(user_id):
                return self.fail_response(
                    message="Forbidden",
                    status_code=403
                )

            # Initialize dependencies
            notification_service = NotificationService(request.ctx.db_session)
            
            # Delete notification
            deleted = await notification_service.delete_notification(notification_id, user_id)
            
            if deleted:
                return self.success_response(
                    message="Notification deleted successfully",
                    status_code=200
                )
            else:
                return self.fail_response(
                    message="Notification not found or not authorized",
                    status_code=404
                )
        except ValueError as e:
            logger.error(f"Invalid parameters: {e}")
            return self.fail_response(
                message="Invalid parameters",
                status_code=400
            )
        except Exception as e:
            logger.error(f"Failed to delete notification {notification_id}: {e}", exc_info=True)
            return self.error_response(
                message="Failed to delete notification",
                status_code=500
            )
