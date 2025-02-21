import psutil
import os
import json
import subprocess
import time
import socket
import datetime
from kafka_producer import KafkaStreamProducer


class SystemMonitor:
    def __init__(self):
        self.hostname = socket.gethostname()
        # self.producer_conf = {
        #     "bootstrap.servers": bootstrap_servers,
        #     "message.send.max.retries": 5,
        #     "retry.backoff.ms": 1000,
        #     "queue.buffering.max.messages": 100000,
        #     "default.topic.config": {"acks": "all"},
        # }
        self.producer = KafkaStreamProducer()

    def get_system_metrics(self):
        metrics = {
            "timestamp": datetime.datetime.now(tz=datetime.UTC).isoformat(),
            "hostname": self.hostname,
            "type": "system_metrics",
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(logical=False),
                "logical_count": psutil.cpu_count(logical=True),
                "times": psutil.cpu_times_percent()._asdict(),
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "used": psutil.virtual_memory().used,
                "percent": psutil.virtual_memory().percent,
                "swap": psutil.swap_memory()._asdict(),
            },
            "disk": [
                {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "usage": psutil.disk_usage(part.mountpoint)._asdict(),
                }
                for part in psutil.disk_partitions()
                if part.mountpoint
            ],
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv,
                "packets_sent": psutil.net_io_counters().packets_sent,
                "packets_recv": psutil.net_io_counters().packets_recv,
            },
        }
        return metrics

    def send_metrics(self, interval=10):
        try:
            kafka_topic = "system_metrics"
            self.producer.create_topic(kafka_topic)
            while True:
                metrics = self.get_system_metrics()
                self.producer.send_log_data(
                    kafka_topic,
                    data=json.dumps(metrics),
                )
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nFlushing remaining metrics...")
            self.producer.interrupt_flush()
            print("Producer shutdown complete")
        except Exception as e:
            print(f'⚠️ Error occurred: {e}')

if __name__ == '__main__':
    SystemMonitor().send_metrics()