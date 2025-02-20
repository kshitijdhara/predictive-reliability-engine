import re
import json
import time
import os
from pathlib import Path

from kafka_producer import KafkaStreamProducer

class LogMonitor:
    def __init__(self, log_file):
        if os.path.isfile(log_file):
            self.log_file = Path(log_file)
            self.last_inode = self._get_inode()
            self.last_position = self._get_file_size()
            self.kafka_producer = KafkaStreamProducer()
        else:
            exit(1)

    def _get_inode(self):
        return os.stat(self.log_file).st_ino

    def _get_file_size(self):
        return self.log_file.stat().st_size

    def _has_rotated(self):
        return self._get_inode() != self.last_inode

    def _follow(self):
        while True:
            if self._has_rotated():
                self.last_inode = self._get_inode()
                self.last_position = 0

            with open(self.log_file, 'r') as f:
                f.seek(self.last_position)
                lines = f.readlines()
                if lines:
                    self.last_position = f.tell()
                    yield from lines
            time.sleep(0.1)

    def parse_log_line(self, line):
        """Parse common syslog format lines into structured data"""
        pattern = r'^(\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2})\s(\S+)\s(\S+?)(\[\d+\])?:\s(.*)$'
        match = re.match(pattern, line)
        if match:
            return {
                'timestamp': match.group(1),
                'hostname': match.group(2),
                'service': match.group(3),
                'pid': match.group(4)[1:-1] if match.group(4) else None,
                'message': match.group(5),
                'raw': line.strip()
            }
        return {'raw': line.strip()}

    def to_json(self, line):
        log_entry = self.parse_log_line(line)
        return json.dumps({
            **log_entry,
            'received_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'source_file': str(self.log_file)
        })

    def monitor(self):
        kafka_topic = 'log_files'
        self.kafka_producer.create_topic(kafka_topic)
        for line in self._follow():
            json_line = self.to_json(line)
            print(json_line)
            self.kafka_producer.send_log_data(topic=kafka_topic,data=json_line)
            
            
    

if __name__ == '__main__':
    # Usage: monitor /var/log/syslog
    import sys
    try:
        LogMonitor(sys.argv[1]).monitor()
    except IndexError:
        print("Usage: python log_monitor.py </path/to/logfile>")
