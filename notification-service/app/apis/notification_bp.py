# notification-service/app/apis/notification_bp.py
from sanic import Blueprint

from app.views.notification_view import NotificationListView, NotificationDetailView

notification_bp = Blueprint('notification_bp', url_prefix='/api/v1/notification-service/notifications')

# GET /api/v1/notification-service/notifications/users/<user_id:uuid> - List user's notifications
notification_bp.add_route(NotificationListView.as_view(), '/users/<user_id:uuid>', name='notification_list')

# PATCH /api/v1/notification-service/notifications/<notification_id:int>/users/<user_id:uuid> - Mark as read
# DELETE /api/v1/notification-service/notifications/<notification_id:int>/users/<user_id:uuid> - Delete notification
notification_bp.add_route(NotificationDetailView.as_view(), '/<notification_id:int>/users/<user_id:uuid>', name='notification_detail')
