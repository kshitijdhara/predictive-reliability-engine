import json
from time import sleep
import pandas as pd
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

class KafkaStreamProducer:
    def __init__(self, kafka_server_url="localhost", kafka_server_port="9092"):
        self.bootstrap_servers = f"{kafka_server_url}:{kafka_server_port}"
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")  # Serialize data to JSON
        )
        
        self.admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)

    def create_topic(self, topic, num_partitions=1, replication_factor=1):
        """Creates a Kafka topic if it doesn't already exist."""
        existing_topics = self.admin_client.list_topics()
        if topic not in existing_topics:
            topic_config = NewTopic(
                name=topic,
                num_partitions=num_partitions,
                replication_factor=replication_factor
            )
            self.admin_client.create_topics([topic_config])
            print(f"✅ Created topic: {topic}")
        else:
            print(f"⚡ Topic {topic} already exists.")

    def send_metrics_from_csv(self, topic, csv_file):
        """Reads metrics from a CSV file and sends them to Kafka."""
        df = pd.read_csv(csv_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])  # Ensure timestamp format

        for _, row in df.iterrows():
            message = {
                "timestamp": row["timestamp"].isoformat(),
                "cpu_usage": row["cpu_usage"],
                "memory_usage": row["memory_usage"],
                "disk_io": row["disk_io"],
                "network_latency": row["network_latency"],
                "error_rate": row["error_rate"]
            }
            self.producer.send(topic, value=message)
            print(f"📤 Sent: {message}")
            sleep(1)

        self.producer.flush()  # Ensure all messages are sent
        print("✅ All metrics have been sent.")
    
    def send_log_data(self, topic, data):
        self.producer.send(topic=topic, value=data)
        print("data sent to topic")

# Example Usage
if __name__ == "__main__":
    producer = KafkaStreamProducer()
    topic_name = "metrics_topic"

    # Create Kafka topic if not exists
    producer.create_topic(topic_name)

    # Send metrics from CSV
    producer.send_metrics_from_csv(topic_name, "/Users/kshitijdhara/Public/predictive-reliability-engine/metrics_data.csv")
