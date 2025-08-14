import sqlite3
from typing import Protocol

from loguru import logger

from ..core.config import DATABASE_NAME


class DatabaseInterface(Protocol):
    """Protocol defining database operations."""

    def check_offer_exists(self, offer_id: int) -> bool:
        """Check if an offer ID exists in storage."""
        ...

    def add_offer_id(self, offer_id: int) -> None:
        """Add a new offer ID to storage."""
        ...

    def close(self) -> None:
        """Close database connection."""
        ...


class SQLiteDatabase:

    def __init__(self, database_path: str = DATABASE_NAME) -> None:
        """Initialize database connection and create tables if needed."""
        self._connection = sqlite3.connect(database_path, check_same_thread=False)
        self._cursor = self._connection.cursor()
        self._create_tables()
        logger.info("Database initialized: %s" % database_path)

    def _create_tables(self) -> None:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_id INTEGER UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        with self._connection:
            self._cursor.execute(create_table_query)
        logger.debug("Database tables ensured")

    def check_offer_exists(self, offer_id: int) -> bool:
        try:
            with self._connection:
                query = "SELECT 1 FROM offers WHERE offer_id = ?"
                exists = self._cursor.execute(query, (offer_id,)).fetchone() is not None
                logger.debug("Offer ID %d exists: %s" % (offer_id, exists))
                return exists
        except sqlite3.Error as e:
            logger.error(
                "Database error while checking offer ID %d: %s" % (offer_id, e)
            )
            return False

    def add_offer_id(self, offer_id: int) -> None:
        try:
            with self._connection:
                query = "INSERT INTO offers (offer_id) VALUES (?)"
                self._cursor.execute(query, (offer_id,))
                logger.debug("Added offer ID %d to database" % offer_id)
        except sqlite3.IntegrityError:
            logger.warning("Offer ID %d already exists in database" % offer_id)
        except sqlite3.Error as e:
            logger.error("Database error while adding offer ID %d: %s" % (offer_id, e))

    def close(self) -> None:
        self._connection.close()
        logger.info("Database connection closed")
