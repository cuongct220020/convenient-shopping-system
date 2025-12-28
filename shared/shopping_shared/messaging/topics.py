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

# Topic for events related to ingredients.
# The recipe-service will produce events here when ingredients are created, updated, or deleted.
# Example message: {'event_type': 'ingredient_created', 'data': {'component_id': 123, 'component_name': '...', 'type': '...', 'unit': '...'}}
INGREDIENT_EVENTS_TOPIC = "ingredient_events"

# Topic for events related to recipes.
# The recipe-service will produce events here when recipes are created, updated, or deleted.
# Example message: {'event_type': 'recipe_created', 'data': {'component_id': 123, 'component_name': '...', 'component_list': [...]}}
RECIPE_EVENTS_TOPIC = "recipe_events"

# Topic for component existence updates.
# The shopping-storage-service will produce events here when storable units are added/removed.
# The recipe-service will consume this to update component existence cache.
# Example message: {'event_type': 'update_component_existence', 'data': {'group_id': 123, 'unit_names': ['...']}}
COMPONENT_EXISTENCE_TOPIC = "component_existence"