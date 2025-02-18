from connectors.timescale_db_connector import TimescaleDBConnector
import creds
import pandas as pd


def ingest_data():
    # Example: Read data from a CSV file
    df = pd.read_csv("metrics_data.csv")
    # Normalize data: convert 'timestamp' column to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def main():
    # Compose your connection string; ensure sensitive credentials are managed securely
    connection_str = f"postgres://{creds.username}:{creds.password}@{creds.connection_url}:{creds.connnection_port}/{creds.db_name}"
    connector = TimescaleDBConnector(connection_str)
    connector.connect()
    
    df = ingest_data()
    connector.create_table_if_not_present()
    # Insert each row into the 'metrics' table; adapt columns as needed
    for _, row in df.iterrows():
        connector.insert_metric("metrics",
                                  ["timestamp","cpu_usage","memory_usage","disk_io","network_latency","error_rate"],
                                  [row["timestamp"],row["cpu_usage"],row["memory_usage"],row["disk_io"],row["network_latency"],row["error_rate"]])
    
    connector.close()

if __name__ == "__main__":
    main()
