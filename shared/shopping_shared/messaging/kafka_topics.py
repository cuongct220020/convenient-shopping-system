# Centralized definition of Kafka topic names to avoid magic strings.
# Best Practice Kakfa Topic Naming Conventions are followed: <domain>.<entity>.<action>.

REGISTRATION_EVENTS_TOPIC = "user_service.user.register_account"

RESET_PASSWORD_EVENTS_TOPIC = "user_service.user.reset_password"

EMAIL_CHANGE_EVENTS_TOPIC = "user_service.user.change_email"

USER_UPDATE_TAG_EVENTS_TOPIC = "user_service.user.update_tags"

LOGOUT_EVENTS_TOPIC = "user_service.user.logout_account"

# Group-related notification topics
ADD_USERS_GROUP_EVENTS_TOPIC = "user_service.group.add_users"

LEAVE_GROUP_EVENTS_TOPIC = "user_service.group.leave_groups"

REMOVE_USERS_GROUP_EVENTS_TOPIC = "user_service.group.remove_users"

UPDATE_HEADCHEF_ROLE_EVENTS_TOPIC = "user_service.group.update_headchef_role"

# General notification topic - all non-OTP notifications go here
NOTIFICATION_TOPIC = "service_notifications"