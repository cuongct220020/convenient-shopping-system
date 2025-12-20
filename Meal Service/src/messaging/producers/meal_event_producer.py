from messaging.manager import kafka_manager

def produce_meal_event(event: dict):
    producer = kafka_manager.get_producer()
    producer.send_and_wait(
        topic="meal_event",
        value=event,
        timeout=10
    )