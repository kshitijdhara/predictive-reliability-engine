table_configs = {
        'log_files': {
            'query': """
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
            'primary_key': 'received_at'
        },
        'system_metrics': {
            'query': """
                CREATE TABLE system_metrics (
                    metric_id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    hostname TEXT NOT NULL,
                    CONSTRAINT unique_snapshot UNIQUE (timestamp, hostname)
                    );""",
            'primary_key': 'metric_id'
        },
        'cpu_metrics':{
            'query': """
                CREATE TABLE cpu_metrics (
                    metric_id INTEGER PRIMARY KEY,
                    cpu_percent NUMERIC NOT NULL,
                    cpu_count INTEGER NOT NULL,
                    cpu_logical_count INTEGER NOT NULL,
                    cpu_time_user NUMERIC,
                    cpu_time_system NUMERIC,
                    cpu_time_idle NUMERIC,
                    cpu_time_nice NUMERIC,
                    FOREIGN KEY(metric_id) REFERENCES system_metrics(metric_id)
                    );""",
            'primary_key': 'metric_id'
        },
        'memory_metrics':{
            'query': """
                CREATE TABLE memory_metrics (
                    metric_id INTEGER PRIMARY KEY,
                    total_memory BIGINT NOT NULL,
                    available_memory BIGINT NOT NULL,
                    used_memory BIGINT NOT NULL,
                    memory_percent NUMERIC NOT NULL,
                    FOREIGN KEY(metric_id) REFERENCES system_metrics(metric_id)
                    );""",
            'primary_key': 'metric_id'
        },
        'swap_metrics':{
            'query': """
                CREATE TABLE swap_metrics (
                    metric_id INTEGER PRIMARY KEY,
                    total_swap BIGINT,
                    used_swap BIGINT,
                    free_swap BIGINT,
                    swap_percent NUMERIC,
                    swap_in BIGINT,
                    swap_out BIGINT,
                    FOREIGN KEY(metric_id) REFERENCES system_metrics(metric_id)
                    );""",
            'primary_key': 'metric_id'
        },
        'disk_metrics':{
            'query': """
                CREATE TABLE disk_metrics (
                    disk_id SERIAL PRIMARY KEY,
                    metric_id INTEGER NOT NULL,
                    device TEXT NOT NULL,
                    mountpoint TEXT NOT NULL,
                    total_disk BIGINT,
                    used_disk BIGINT,
                    free_disk BIGINT,
                    disk_percent NUMERIC,
                    FOREIGN KEY(metric_id) REFERENCES system_metrics(metric_id)
                    );""",
            'primary_key': 'disk_id'
        },
        'memory_metrics':{
            'query': """
                CREATE TABLE network_metrics (
                    metric_id INTEGER PRIMARY KEY,
                    bytes_sent BIGINT,
                    bytes_recv BIGINT,
                    packets_sent BIGINT,
                    packets_recv BIGINT,
                    FOREIGN KEY(metric_id) REFERENCES system_metrics(metric_id)
                    );""",
            'primary_key': 'metric_id'
        },
    }