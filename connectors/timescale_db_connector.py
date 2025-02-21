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

    def table_exists(self, table_str):
        exists = False
        try:
            cur = self.conn.cursor()
            cur.execute(
                "select exists(select relname from pg_class where relname='"
                + table_str
                + "');"
            )
            exists = cur.fetchone()[0]
            cur.close()
        except Exception as e:
            print(f"Error : {e}")
        return exists

    def create_table_if_not_present(self, type):
        config = timescaledb_queries.table_configs.get(type)
        if not config:
            raise ValueError(f"Unsupported table type: {type}")

        if not self.table_exists(type):
            with self.conn.cursor() as cur:
                cur.execute(config["query"])
                # cur.execute(f"SELECT create_hypertable('{type}', '{config['primary_key']}', if_not_exists => TRUE);")

            self.conn.commit()

    def insert_metric(self, table, columns, values, returning=None):
        query = psycopg.sql.SQL(
            """
            INSERT INTO {table} ({cols})
            VALUES ({vals})
            {returning}
        """
        ).format(
            table=psycopg.sql.Identifier(table),
            cols=psycopg.sql.SQL(", ").join(map(psycopg.sql.Identifier, columns)),
            vals=psycopg.sql.SQL(", ").join(psycopg.sql.Placeholder() for _ in values),
            returning=(
                psycopg.sql.SQL("RETURNING {}").format(
                    psycopg.sql.SQL(", ").join(map(psycopg.sql.Identifier, returning))
                )
                if returning
                else psycopg.sql.SQL("")
            ),
        )

        with self.conn.cursor() as cur:
            cur.execute(query, values)
            if returning:
                result = cur.fetchone()
            else:
                result = None
        self.conn.commit()
        return result

    def close(self):
        if self.conn:
            self.conn.close()
