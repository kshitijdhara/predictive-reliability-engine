from kafka import KafkaConsumer
import json
import timescale_db_connector
import creds

class KafkaStreamConsumer:
    def __init__(self, topic, bootstrap_servers, timescaledb_conn):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.timescaledb_connection = timescale_db_connector.TimescaleDBConnector(timescaledb_conn)
        
    def store_data(self):
        self.timescaledb_connection.connect()
        for message in self.consumer:
            data = json.loads(message.value)
            self.timescaledb_connection.create_table_if_not_present(type=data['type'])
            self.timescaledb_connection.insert_metric(table=data['type'], columns=list(data.keys()), values=list(data.values()))
    def consume(self):
        for message in self.consumer:
            # For now, print the received message; later integrate preprocessing and DB insertion
            
            print("Received message:", message.value)
            
            

if __name__ == "__main__":
    connection_str = f"postgres://{creds.username}:{creds.password}@{creds.connection_url}:{creds.connnection_port}/{creds.db_name}"
    consumer = KafkaStreamConsumer(topic="log_files",
                                   bootstrap_servers=["localhost:9092"],
                                   timescaledb_conn= connection_str)
    consumer.store_data()
    consumer.consume()