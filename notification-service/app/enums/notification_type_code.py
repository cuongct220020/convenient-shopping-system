from enum import Enum

class NotificationTypeCode(str, Enum):
    """Enum for notification type codes"""
    GROUP_USER_ADDED = "group_user_added"
    REGISTRATION_OTP = "registration_otp"