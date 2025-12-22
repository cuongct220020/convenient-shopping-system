# Centralized definition of Kafka topic names to avoid magic strings.

# A general topic for triggering notifications.
# Services can produce messages here that the notification-service will consume.
# Example message: {'event_type': 'password_reset', 'user_id': 123, 'email': '...'}
NOTIFICATION_TOPIC = "service_notifications"

# Topic for events related to user activities.
# The user-service will produce events here.
# The recommendation-service can consume this to learn about user behavior.
# Example message: {'event_type': 'user_registered', 'user_id': 123, 'details': {...}}
# Example message: {'event_type': 'user_updated_preferences', 'user_id': 123, 'preferences': {...}}
USER_EVENTS_TOPIC = "user_events"

# Topic for events related to meal planning.
# The meal-service will produce events here.
# Example message: {'event_type': 'meal_plan_created', 'user_id': 123, 'plan_id': 456}
MEAL_EVENTS_TOPIC = "meal_events"

# Topic for events related to the shopping pantry.
# The shopping-pantry-service will produce events here.
# The recommendation-service can consume this to learn about pantry contents.
# Example message: {'event_type': 'item_added_to_pantry', 'user_id': 123, 'item_id': 789}
PANTRY_EVENTS_TOPIC = "pantry_events"
