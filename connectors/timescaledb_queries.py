table_configs = {
    "log_files": {
        "query": """
                CREATE TABLE IF NOT EXISTS log_files (
                    received_at TIMESTAMPTZ NOT NULL,
                    hostname TEXT NOT NULL,
                    pid INTEGER NOT NULL,
                    timestamp TEXT,
                    service TEXT,
                    message TEXT,
                    raw TEXT,
                    source_file TEXT,
                    type TEXT,
                    PRIMARY KEY (received_at, hostname, pid)
                    );""",
        "primary_key": "received_at",
    },
    'system_metrics': {
        'query': """
            CREATE TABLE system_metrics (
                metric_id SERIAL ,
                timestamp TIMESTAMPTZ NOT NULL,
                hostname TEXT NOT NULL,
                PRIMARY KEY (timestamp, metric_id),
                CONSTRAINT unique_snapshot UNIQUE (timestamp, hostname)
            );""",
        'primary_key': 'timestamp'  # Correct partitioning column
},
    "cpu_metrics": {
        "query": """
                CREATE TABLE cpu_metrics (
                    timestamp TIMESTAMPTZ NOT NULL,
                    metric_id INTEGER,
                    cpu_percent NUMERIC NOT NULL,
                    cpu_count INTEGER NOT NULL,
                    cpu_logical_count INTEGER NOT NULL,
                    cpu_time_user NUMERIC,
                    cpu_time_system NUMERIC,
                    cpu_time_idle NUMERIC,
                    cpu_time_nice NUMERIC,
                    FOREIGN KEY(timestamp, metric_id) REFERENCES system_metrics(timestamp, metric_id)
                    );""",
        "primary_key": "metric_id",
    },
    "memory_metrics": {
        "query": """
                CREATE TABLE memory_metrics (
                    timestamp TIMESTAMPTZ NOT NULL,
                    metric_id INTEGER,
                    total_memory BIGINT NOT NULL,
                    available_memory BIGINT NOT NULL,
                    used_memory BIGINT NOT NULL,
                    memory_percent NUMERIC NOT NULL,
                    FOREIGN KEY(timestamp, metric_id) REFERENCES system_metrics(timestamp, metric_id)
                    );""",
        "primary_key": "metric_id",
    },
    "swap_metrics": {
        "query": """
                CREATE TABLE swap_metrics (
                    timestamp TIMESTAMPTZ NOT NULL,
                    metric_id INTEGER,
                    total_swap BIGINT,
                    used_swap BIGINT,
                    free_swap BIGINT,
                    swap_percent NUMERIC,
                    swap_in BIGINT,
                    swap_out BIGINT,
                    FOREIGN KEY(timestamp, metric_id) REFERENCES system_metrics(timestamp, metric_id)
                    );""",
        "primary_key": "metric_id",
    },
    "disk_metrics": {
        "query": """
                CREATE TABLE disk_metrics (
                    disk_id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    metric_id INTEGER NOT NULL,
                    device TEXT NOT NULL,
                    mountpoint TEXT NOT NULL,
                    total_disk BIGINT,
                    used_disk BIGINT,
                    free_disk BIGINT,
                    disk_percent NUMERIC,
                    FOREIGN KEY(timestamp, metric_id) REFERENCES system_metrics(timestamp, metric_id)
                    );""",
        "primary_key": "disk_id",
    },
    "network_metrics": {
        "query": """
                CREATE TABLE network_metrics (
                    timestamp TIMESTAMPTZ NOT NULL,
                    metric_id INTEGER,
                    bytes_sent BIGINT,
                    bytes_recv BIGINT,
                    packets_sent BIGINT,
                    packets_recv BIGINT,
                    FOREIGN KEY(timestamp, metric_id) REFERENCES system_metrics(timestamp, metric_id)
                    );""",
        "primary_key": "metric_id",
    },
}
