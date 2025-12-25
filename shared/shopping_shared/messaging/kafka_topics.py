# Centralized definition of Kafka topic names to avoid magic strings.
# Best Practice Kakfa Topic Naming Conventions are followed: <domain>.<entity>.<action>.

REGISTRATION_EVENTS_TOPIC = "user_service.user.register_account"

RESET_PASSWORD_EVENTS_TOPIC = "user_service.user.reset_password"

EMAIL_CHANGE_EVENTS_TOPIC = "user_service.user.change_email"

USER_UPDATE_TAG_EVENTS_TOPIC = "user_service.user.update_tags"