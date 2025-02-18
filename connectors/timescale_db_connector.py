import psycopg
import psycopg.sql

class TimescaleDBConnector:
    def __init__(self, connection_str):
        self.connection_str = connection_str
        self.conn = None
    
    def connect(self):
        self.conn = psycopg.connect(conninfo=self.connection_str)
        return self.conn
    
    def create_table_if_not_present(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS metrics (
            timestamp TIMESTAMPTZ NOT NULL,
            cpu_usage DOUBLE PRECISION,
            memory_usage DOUBLE PRECISION,
            disk_io DOUBLE PRECISION,
            network_latency DOUBLE PRECISION,
            error_rate DOUBLE PRECISION,
            PRIMARY KEY (timestamp)
        );
        """

        with self.conn.cursor() as cur:
            cur.execute(create_table_query)
            cur.execute("SELECT create_hypertable('metrics', 'timestamp', if_not_exists => TRUE);")

        self.conn.commit()
    
    def insert_metric(self, table, columns, values):
        query = psycopg.sql.SQL("INSERT INTO {table} ({cols}) VALUES ({vals})").format(
            table=psycopg.sql.Identifier(table),
            cols=psycopg.sql.SQL(', ').join(map(psycopg.sql.Identifier, columns)),
            vals=psycopg.sql.SQL(', ').join(psycopg.sql.Placeholder() for _ in values)
            )
        with self.conn.cursor() as cur:
            cur.execute(query, values)
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()