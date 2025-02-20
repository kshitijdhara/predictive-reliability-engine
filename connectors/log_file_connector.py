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
        """Improved syslog parser with better pattern matching"""
        line = line.strip()
        if not line:  # Skip empty lines
            return None
            
        # More robust regex pattern
        pattern = r'''
            ^
            (?P<timestamp>\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2})  # Mmm DD HH:MM:SS
            \s+
            (?P<hostname>\S+)                                # Hostname
            \s+
            (?P<service>[\w\-\.]+)                           # Service (allows hyphens/dots)
            (?:\[(?P<pid>\d+)\])?                            # Optional PID
            :\s+
            (?P<message>.*)                                  # Message content
            $
        '''
        match = re.match(pattern, line, re.VERBOSE)
        
        if match:
            return {
                'timestamp': match.group('timestamp'),
                'hostname': match.group('hostname'),
                'service': match.group('service'),
                'pid': match.group('pid'),
                'message': match.group('message').strip(),
                'raw': line
            }
        return {'raw': line}  # Fallback with original content

    def monitor(self):
        kafka_topic = 'log_files'
        self.kafka_producer.create_topic(kafka_topic)
        for line in self._follow():
            if not line.strip():  # Skip empty lines
                continue
                
            json_line = self.to_json(line)
            print("Sending:", json_line)  # Debug output
            self.kafka_producer.send_log_data(topic=kafka_topic, data=json_line)

    def to_json(self, line):
        log_entry = self.parse_log_line(line)
        return json.dumps({
            **log_entry,
            'received_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'source_file': str(self.log_file),
            'type': 'log_files'
        })

            

if __name__ == '__main__':
    # Usage: monitor /var/log/syslog
    import sys
    try:
        LogMonitor(sys.argv[1]).monitor()
    except IndexError:
        print("Usage: python log_monitor.py </path/to/logfile>")
