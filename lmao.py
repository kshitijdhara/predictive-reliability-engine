from kafka import KafkaAdminClient
import time

def wait_for_kafka(bootstrap_servers, retries=5, delay=5):
    for i in range(retries):
        try:
            admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
            print("✅ Kafka is ready!")
            return admin_client
        except Exception as e:
            print(f"⏳ Waiting for Kafka... Attempt {i+1}/{retries}")
            time.sleep(delay)
    raise Exception("❌ Kafka is not reachable after multiple attempts.")

# Usage
bootstrap_servers = "localhost:9092"
admin_client = wait_for_kafka(bootstrap_servers)
