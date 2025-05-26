from contextlib import contextmanager
import threading
import sqlite3


class DatabaseManager:
    def __init__(self, db_path="courses.db"):
        self.db_path = db_path
        self._connection = None
        self._lock = threading.Lock()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        try:
            with self._lock:
                if self._connection is None:
                    self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
                yield self._connection
        except Exception as e:
            if self._connection:
                self._connection.rollback()
            raise e

    def execute_query(self, query, params=()):
        """Execute a query and return results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_update(self, query, params=()):
        """Execute an update query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None