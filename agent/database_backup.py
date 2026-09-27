import os
import sqlite3


DATABASE_URL = os.environ.get("DATABASE_URL")


class DBConnection:

    def __init__(self):

        self.postgres = bool(DATABASE_URL)

        if self.postgres:

            import psycopg
            from psycopg.rows import dict_row

            url = DATABASE_URL

            if url.startswith("postgres://"):
                url = url.replace(
                    "postgres://",
                    "postgresql://",
                    1
                )

            self.connection = psycopg.connect(
                url,
                row_factory=dict_row
            )

        else:

            self.connection = sqlite3.connect(
                "database.db"
            )

            self.connection.row_factory = sqlite3.Row

    def execute(self, sql, params=()):

        if self.postgres:
            sql = sql.replace("?", "%s")

        return self.connection.execute(
            sql,
            params
        )

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def get_db_connection():
    return DBConnection()


def create_tables():

    db = get_db_connection()

    # ==========================================
    # USERS
    # ==========================================

    if db.postgres:

        db.execute("""
            CREATE TABLE IF NOT EXISTS users (

                id SERIAL PRIMARY KEY,

                name TEXT NOT NULL,

                email TEXT NOT NULL UNIQUE,

                password_hash TEXT NOT NULL,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP

            )
        """)

    else:

        db.execute("""
            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                email TEXT NOT NULL UNIQUE,

                password_hash TEXT NOT NULL,

                created_at TEXT
                    DEFAULT CURRENT_TIMESTAMP

            )
        """)

    # ==========================================
    # TIMETABLE
    # ==========================================

    if db.postgres:

        db.execute("""
            CREATE TABLE IF NOT EXISTS timetable (

                id SERIAL PRIMARY KEY,

                user_id INTEGER NOT NULL,

                subject TEXT NOT NULL,

                day TEXT NOT NULL,

                start_time TEXT NOT NULL,

                end_time TEXT NOT NULL,

                room TEXT,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE

            )
        """)

    else:

        db.execute("""
            CREATE TABLE IF NOT EXISTS timetable (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                subject TEXT NOT NULL,

                day TEXT NOT NULL,

                start_time TEXT NOT NULL,

                end_time TEXT NOT NULL,

                room TEXT,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE

            )
        """)

    # ==========================================
    # ASSIGNMENTS
    # ==========================================

    if db.postgres:

        db.execute("""
            CREATE TABLE IF NOT EXISTS assignments (

                id SERIAL PRIMARY KEY,

                user_id INTEGER NOT NULL,

                title TEXT NOT NULL,

                subject TEXT NOT NULL,

                deadline TEXT NOT NULL,

                estimated_hours INTEGER NOT NULL,

                importance TEXT NOT NULL,

                status TEXT DEFAULT 'Pending',

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE

            )
        """)

    else:

        db.execute("""
            CREATE TABLE IF NOT EXISTS assignments (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                title TEXT NOT NULL,

                subject TEXT NOT NULL,

                deadline TEXT NOT NULL,

                estimated_hours INTEGER NOT NULL,

                importance TEXT NOT NULL,

                status TEXT DEFAULT 'Pending',

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE

            )
        """)

    # ==========================================
    # PRESENTATIONS
    # ==========================================

    if db.postgres:

        db.execute("""
            CREATE TABLE IF NOT EXISTS presentations (

                id SERIAL PRIMARY KEY,

                user_id INTEGER NOT NULL,

                topic TEXT NOT NULL,

                subject TEXT NOT NULL,

                presentation_date TEXT NOT NULL,

                preparation_hours INTEGER NOT NULL,

                importance TEXT NOT NULL,

                status TEXT DEFAULT 'Planned',

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE

            )
        """)

    else:

        db.execute("""
            CREATE TABLE IF NOT EXISTS presentations (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                topic TEXT NOT NULL,

                subject TEXT NOT NULL,

                presentation_date TEXT NOT NULL,

                preparation_hours INTEGER NOT NULL,

                importance TEXT NOT NULL,

                status TEXT DEFAULT 'Planned',

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE

            )
        """)

    db.commit()
    db.close()


if __name__ == "__main__":

    create_tables()

    print("NEXUS database created successfully.")