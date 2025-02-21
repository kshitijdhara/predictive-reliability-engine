from kafka import KafkaConsumer
import json
import timescale_db_connector
import creds


class KafkaStreamConsumer:
    def __init__(self, topic, bootstrap_servers, timescaledb_conn):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset='earliest'
        )
        self.timescaledb_connection = timescale_db_connector.TimescaleDBConnector(
            timescaledb_conn
        )

    def store_data(self):
        self.timescaledb_connection.connect()
        for message in self.consumer:
            data = json.loads(message.value)
            if "system_metrics" in data:
                self.timescaledb_connection.create_table_if_not_present(
                    type="system_metrics"
                )
                result = self.timescaledb_connection.insert_metric(
                    table="system_metrics",
                    columns=list(data["system_metrics"].keys()),
                    values=list(data["system_metrics"].values()),
                    returning=["metric_id", "timestamp"],
                )
                metric_id, timestamp = result
                data.pop("system_metrics")
            for key, value in data.items():
                if key == "disk_metrics":
                    for data in value:
                        data.update({"metric_id": metric_id, "timestamp": timestamp})
                        self.timescaledb_connection.create_table_if_not_present(
                            type=key
                        )
                        self.timescaledb_connection.insert_metric(
                            table=key,
                            columns=list(data.keys()),
                            values=list(data.values()),
                        )
                else:
                    value.update({"metric_id": metric_id, "timestamp": timestamp})
                    self.timescaledb_connection.create_table_if_not_present(type=key)
                    self.timescaledb_connection.insert_metric(
                        table=key, columns=list(value.keys()), values=list(value.values())
                    )
            print(f'📧 Message Stored in database metric_id: {metric_id}')

    def consume(self):
        for message in self.consumer:
            # For now, print the received message; later integrate preprocessing and DB insertion

            print("Received message:", message.value)


if __name__ == "__main__":
    connection_str = f"postgres://{creds.username}:{creds.password}@{creds.connection_url}:{creds.connnection_port}/{creds.db_name}"
    consumer = KafkaStreamConsumer(
        topic="system_metrics",
        bootstrap_servers=["localhost:9092"],
        timescaledb_conn=connection_str,
    )
    consumer.store_data()
    consumer.consume()
