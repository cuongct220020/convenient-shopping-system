# notification-service/app/core/notification_constants.py
from app.enums.notification_priority import NotificationPriority

class NotificationTemplateDefaults:
    """
    Default templates for in-app notifications.
    Used for seeding the database and as a central reference for message content.
    """
    
    # --- Group Events ---
    
    # Event: User is added to a group by someone
    GROUP_USER_ADDED = {
        "code": "GROUP_USER_ADDED",
        "name": "User Added to Group",
        "template_title": "Chào mừng bạn gia nhập nhóm {{ group_name }}!",
        "template_body": "{{ requester_username }} đã thêm bạn vào nhóm {{ group_name }}. Hãy bắt đầu lên thực đơn ngay nhé!",
        "priority": NotificationPriority.LOW
    }

    # Event: User is removed (kicked) from a group
    GROUP_USER_REMOVED = {
        "code": "GROUP_USER_REMOVED",
        "name": "User Removed from Group",
        "template_title": "Bạn đã bị xóa khỏi nhóm {{ group_name }}",
        "template_body": "Quản trị viên {{ requester_username }} đã xóa bạn khỏi nhóm {{ group_name }}. Tài khoản của bạn không còn quyền truy cập vào dữ liệu nhóm này.",
        "priority": NotificationPriority.HIGH
    }

    # Event: A member leaves the group voluntarily (Notification to other members)
    GROUP_USER_LEFT = {
        "code": "GROUP_USER_LEFT",
        "name": "User Left Group",
        "template_title": "Thành viên rời nhóm {{ group_name }}",
        "template_body": "{{ user_identifier }} đã rời khỏi nhóm.",
        "priority": NotificationPriority.LOW
    }

    # Event: Head Chef role is transferred to a new user
    GROUP_HEAD_CHEF_UPDATED = {
        "code": "GROUP_HEAD_CHEF_UPDATED",
        "name": "Group Head Chef Updated",
        "template_title": "Thông báo thay đổi Bếp trưởng nhóm {{ group_name }}",
        "template_body": "{{ requester_username }} đã chỉ định {{ new_head_chef_identifier }} làm Bếp trưởng mới của nhóm.",
        "priority": NotificationPriority.MEDIUM
    }

    @classmethod
    def get_all_templates(cls):
        """Returns a list of all defined notification templates."""
        return [
            cls.GROUP_USER_ADDED,
            cls.GROUP_USER_REMOVED,
            cls.GROUP_USER_LEFT,
            cls.GROUP_HEAD_CHEF_UPDATED
        ]
