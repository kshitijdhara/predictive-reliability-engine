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
        self.producer = KafkaStreamProducer()

    def get_cpu_metric(self):
        cpu_times = psutil.cpu_times_percent()._asdict()
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": psutil.cpu_count(logical=False),
            "cpu_logical_count": psutil.cpu_count(logical=True),
            "cpu_time_user": cpu_times["user"],
            "cpu_time_system": cpu_times["system"],
            "cpu_time_idle": cpu_times["idle"],
            "cpu_time_nice": cpu_times["nice"],
        }

    def get_memory_metric(self):
        return {
            "total_memory": psutil.virtual_memory().total,
            "available_memory": psutil.virtual_memory().available,
            "used_memory": psutil.virtual_memory().used,
            "memory_percent": psutil.virtual_memory().percent,
        }

    def get_swap_memory_metrics(self):
        swap_metrics = psutil.swap_memory()._asdict()
        return {
            "total_swap": swap_metrics["total"],
            "used_swap": swap_metrics["used"],
            "free_swap": swap_metrics["free"],
            "swap_percent": swap_metrics["percent"],
            "swap_in": swap_metrics["sin"],
            "swap_out": swap_metrics["sout"],
        }

    def get_disk_metrics(self):
        disk_metrics = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_metrics.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "total_disk": usage.total,
                        "used_disk": usage.used,
                        "free_disk": usage.free,
                        "disk_percent": usage.percent,
                    }
                )
            except Exception:
                # In case of permission errors or unavailable mountpoints, skip them.
                continue
        return disk_metrics

    def get_network_metrics(self):
        net = psutil.net_io_counters()
        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        }

    def get_system_metrics(self):
        metrics = {
            "system_metrics": {
                "timestamp": datetime.datetime.now(tz=datetime.UTC).isoformat(),
                "hostname": self.hostname,
            },
            "cpu_metrics": self.get_cpu_metric(),
            "memory_metrics": self.get_memory_metric(),
            "swap_metrics": self.get_swap_memory_metrics(),
            "disk_metrics": self.get_disk_metrics(),
            "network_metrics": self.get_network_metrics(),
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
            print(f"⚠️ Error occurred: {e}")


if __name__ == "__main__":
    SystemMonitor().send_metrics()
