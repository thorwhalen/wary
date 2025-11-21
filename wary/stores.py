"""Alternative storage backends for wary.

This module provides PostgreSQL-based storage for production use.
The default file-based storage is fine for local/personal use, but
PostgreSQL is recommended for shared/production deployments.
"""

from typing import Optional
from datetime import datetime
import json


class PostgresDependencyGraph:
    """Dependency graph backed by PostgreSQL.

    Uses the same interface as DependencyGraph but stores data in PostgreSQL.
    """

    def __init__(self, connection_string: str):
        try:
            import psycopg2
        except ImportError:
            raise ImportError("psycopg2 is required for PostgreSQL storage. Install with: pip install psycopg2-binary")

        self.conn = psycopg2.connect(connection_string)
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist."""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dependency_edges (
                    id SERIAL PRIMARY KEY,
                    upstream VARCHAR(255) NOT NULL,
                    downstream VARCHAR(255) NOT NULL,
                    constraint_spec VARCHAR(255),
                    registered_at TIMESTAMP,
                    risk_score FLOAT,
                    metadata JSONB,
                    UNIQUE(upstream, downstream)
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_upstream
                ON dependency_edges(upstream)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_downstream
                ON dependency_edges(downstream)
            """)
            self.conn.commit()

    def register_dependent(
        self, upstream: str, downstream: str, constraint: str = "", **metadata
    ):
        """Register a new dependent package."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dependency_edges
                (upstream, downstream, constraint_spec, registered_at, risk_score, metadata)
                VALUES (%s, %s, %s, NOW(), %s, %s)
                ON CONFLICT (upstream, downstream)
                DO UPDATE SET
                    constraint_spec = EXCLUDED.constraint_spec,
                    metadata = EXCLUDED.metadata,
                    registered_at = EXCLUDED.registered_at
            """,
                (
                    upstream,
                    downstream,
                    constraint,
                    metadata.get('risk_score', 0.5),
                    json.dumps(metadata),
                ),
            )
            self.conn.commit()

    def get_dependents(self, upstream: str) -> list[dict]:
        """Get all packages that depend on upstream."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT downstream, constraint_spec, risk_score, metadata, registered_at
                FROM dependency_edges
                WHERE upstream = %s
            """,
                (upstream,),
            )

            return [
                {
                    'upstream': upstream,
                    'downstream': row[0],
                    'constraint': row[1],
                    'risk_score': row[2],
                    'metadata': row[3],
                    'registered_at': row[4],
                }
                for row in cur.fetchall()
            ]

    def get_all_edges(self) -> list[dict]:
        """Get all dependency edges."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT upstream, downstream, constraint_spec, risk_score, metadata, registered_at
                FROM dependency_edges
            """)

            return [
                {
                    'upstream': row[0],
                    'downstream': row[1],
                    'constraint': row[2],
                    'risk_score': row[3],
                    'metadata': row[4],
                    'registered_at': row[5],
                }
                for row in cur.fetchall()
            ]

    def __len__(self) -> int:
        """Get total number of edges."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM dependency_edges")
            return cur.fetchone()[0]


class PostgresResultsLedger:
    """Test results backed by PostgreSQL."""

    def __init__(self, connection_string: str):
        try:
            import psycopg2
        except ImportError:
            raise ImportError("psycopg2 is required for PostgreSQL storage. Install with: pip install psycopg2-binary")

        self.conn = psycopg2.connect(connection_string)
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist."""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    test_id VARCHAR(36) PRIMARY KEY,
                    upstream_package VARCHAR(255),
                    upstream_version VARCHAR(100),
                    downstream_package VARCHAR(255),
                    downstream_version VARCHAR(100),
                    test_command TEXT,
                    commit_hash VARCHAR(40),
                    status VARCHAR(20),
                    started_at TIMESTAMP,
                    finished_at TIMESTAMP,
                    output TEXT,
                    exit_code INTEGER,
                    environment JSONB
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_upstream
                ON test_results(upstream_package)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_downstream
                ON test_results(downstream_package)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_status
                ON test_results(status)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_started_at
                ON test_results(started_at DESC)
            """)
            self.conn.commit()

    def add_result(self, result: dict):
        """Add a test result."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO test_results
                (test_id, upstream_package, upstream_version, downstream_package,
                 downstream_version, test_command, commit_hash, status,
                 started_at, finished_at, output, exit_code, environment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    result['test_id'],
                    result['upstream_package'],
                    result['upstream_version'],
                    result['downstream_package'],
                    result['downstream_version'],
                    result['test_command'],
                    result['commit_hash'],
                    result['status'],
                    result['started_at'],
                    result['finished_at'],
                    result['output'],
                    result['exit_code'],
                    json.dumps(result.get('environment', {})),
                ),
            )
            self.conn.commit()

    def __getitem__(self, test_id: str) -> dict:
        """Get a specific test result."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT test_id, upstream_package, upstream_version, downstream_package,
                       downstream_version, test_command, commit_hash, status,
                       started_at, finished_at, output, exit_code, environment
                FROM test_results
                WHERE test_id = %s
            """,
                (test_id,),
            )

            row = cur.fetchone()
            if not row:
                raise KeyError(test_id)

            return {
                'test_id': row[0],
                'upstream_package': row[1],
                'upstream_version': row[2],
                'downstream_package': row[3],
                'downstream_version': row[4],
                'test_command': row[5],
                'commit_hash': row[6],
                'status': row[7],
                'started_at': row[8].isoformat() if row[8] else None,
                'finished_at': row[9].isoformat() if row[9] else None,
                'output': row[10],
                'exit_code': row[11],
                'environment': row[12],
            }

    def query_results(
        self,
        upstream_package: Optional[str] = None,
        downstream_package: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 1000,
    ) -> list[dict]:
        """Query results with filters."""
        conditions = []
        params = []

        if upstream_package:
            conditions.append("upstream_package = %s")
            params.append(upstream_package)
        if downstream_package:
            conditions.append("downstream_package = %s")
            params.append(downstream_package)
        if status:
            conditions.append("status = %s")
            params.append(status)

        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        params.append(limit)

        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT test_id, upstream_package, upstream_version, downstream_package,
                       downstream_version, test_command, commit_hash, status,
                       started_at, finished_at, output, exit_code, environment
                FROM test_results
                WHERE {where_clause}
                ORDER BY started_at DESC
                LIMIT %s
            """,
                params,
            )

            return [
                {
                    'test_id': row[0],
                    'upstream_package': row[1],
                    'upstream_version': row[2],
                    'downstream_package': row[3],
                    'downstream_version': row[4],
                    'test_command': row[5],
                    'commit_hash': row[6],
                    'status': row[7],
                    'started_at': row[8].isoformat() if row[8] else None,
                    'finished_at': row[9].isoformat() if row[9] else None,
                    'output': row[10],
                    'exit_code': row[11],
                    'environment': row[12],
                }
                for row in cur.fetchall()
            ]

    def __len__(self) -> int:
        """Get total number of test results."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM test_results")
            return cur.fetchone()[0]
