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


# kafka_sender.py
import sys
import json
import argparse
from kafka import KafkaProducer
from kafka.errors import KafkaError

class KafkaLogSender:
    def __init__(self, bootstrap_servers, topic_name, ssl_enabled=False):
        self.topic = topic_name
        self.producer = self._create_producer(
            bootstrap_servers,
            ssl_enabled=ssl_enabled
        )
        
    def _create_producer(self, bootstrap_servers, ssl_enabled=False):
        """Create and configure Kafka producer with error handling"""
        config = {
            'bootstrap_servers': bootstrap_servers,
            'value_serializer': lambda v: v.encode('utf-8'),
            'retries': 3,
            'acks': 'all'
        }
        
        if ssl_enabled:
            config.update({
                'security_protocol': 'SSL',
                'ssl_cafile': '/path/to/ca.pem',
                'ssl_certfile': '/path/to/service.cert',
                'ssl_keyfile': '/path/to/service.key'
            })
        
        try:
            return KafkaProducer(**config)
        except KafkaError as e:
            print(f"Failed to create producer: {str(e)}")
            sys.exit(1)

    def send_log(self, log_json):
        """Send log record to Kafka with error callback"""
        future = self.producer.send(self.topic, value=log_json)
        future.add_callback(self._on_send_success).add_errback(self._on_send_error)

    @staticmethod
    def _on_send_success(record_metadata):
        print(f"Sent to: {record_metadata.topic}[{record_metadata.partition}]@{record_metadata.offset}")

    @staticmethod
    def _on_send_error(exc):
        print(f"Failed to send message: {str(exc)}")

    def run(self):
        """Read JSON logs from stdin and send to Kafka"""
        try:
            for line in sys.stdin:
                self.send_log(line.strip())
        except KeyboardInterrupt:
            print("\nFlushing remaining messages...")
            self.producer.flush()
            print("Clean shutdown complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send JSON logs to Kafka')
    parser.add_argument('-b', '--bootstrap-servers', required=True,
                        help='Kafka bootstrap servers (comma-separated)')
    parser.add_argument('-t', '--topic', required=True,
                        help='Target Kafka topic name')
    parser.add_argument('--ssl', action='store_true',
                        help='Enable SSL encryption')
    
    args = parser.parse_args()
    
    sender = KafkaLogSender(
        bootstrap_servers=args.bootstrap_servers.split(','),
        topic_name=args.topic,
        ssl_enabled=args.ssl
    )
    
    print(f"Starting Kafka log sender for topic: {args.topic}")
    sender.run()
