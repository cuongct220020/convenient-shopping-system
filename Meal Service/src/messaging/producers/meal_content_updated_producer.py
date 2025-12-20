from messaging.manager import kafka_manager

def produce_meal_content_updated(event: dict):
    producer = kafka_manager.get_producer()
    producer.send_and_wait(
        topic="meal_updated",
        value=event,
        timeout=10
    )