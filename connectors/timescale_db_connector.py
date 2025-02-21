import psycopg
import psycopg.sql
import json
import timescaledb_queries

class TimescaleDBConnector:
    def __init__(self, connection_str):
        self.connection_str = connection_str
        self.conn = None
    
    def connect(self):
        self.conn = psycopg.connect(conninfo=self.connection_str)
        return self.conn
    
    def create_table_if_not_present(self,type):
        config = timescaledb_queries.table_configs.get(type)
        if not config:
            raise ValueError(f"Unsupported table type: {type}")
        
        with self.conn.cursor() as cur:
            cur.execute(config['query'])
            cur.execute(f"SELECT create_hypertable('{type}', '{config['primary_key']}', if_not_exists => TRUE);")

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