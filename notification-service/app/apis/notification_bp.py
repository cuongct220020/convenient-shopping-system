# notification-service/app/apis/notification_bp.py
from sanic import Blueprint

from app.views.notification_view import NotificationListView, NotificationReadView, NotificationDeleteView

notification_bp = Blueprint('notification_bp', url_prefix='/api/v2/notification-service/notifications')

# GET /api/v2/notification-service/notifications/users/<user_id:uuid> - List user's notifications
notification_bp.add_route(NotificationListView.as_view(), '/users/<user_id:uuid>', name='notification_list')

# PATCH /api/v2/notification-service/notifications/<notification_id:int>/users/<user_id:uuid>/read - Mark as read
notification_bp.add_route(NotificationReadView.as_view(), '/<notification_id:int>/users/<user_id:uuid>/read', name='notification_mark_read')

# DELETE /api/v2/notification-service/notifications/<notification_id:int>/users/<user_id:uuid> - Delete notification
notification_bp.add_route(NotificationDeleteView.as_view(), '/<notification_id:int>/users/<user_id:uuid>', name='notification_delete')
