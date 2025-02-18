from kafka import KafkaConsumer
import json

class KafkaStreamConsumer:
    def __init__(self, topic, bootstrap_servers):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

    def consume(self):
        for message in self.consumer:
            # For now, print the received message; later integrate preprocessing and DB insertion
            print("Received message:", message.value)

if __name__ == "__main__":
    consumer = KafkaStreamConsumer(topic="system-metrics",
                                   bootstrap_servers=["localhost:9092"])
    consumer.consume()
