import sqlite3


DATABASE = "database.db"


def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


def create_tables():

    connection = get_db_connection()


    # ==========================================
    # 1. TIMETABLE TABLE
    # ==========================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS timetable (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            subject TEXT NOT NULL,

            day TEXT NOT NULL,

            start_time TEXT NOT NULL,

            end_time TEXT NOT NULL,

            room TEXT

        )
    """)


    # ==========================================
    # 2. ASSIGNMENTS TABLE
    # ==========================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS assignments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            subject TEXT NOT NULL,

            deadline TEXT NOT NULL,

            estimated_hours INTEGER NOT NULL,

            importance TEXT NOT NULL,

            status TEXT DEFAULT 'Pending'

        )
    """)


    # ==========================================
    # 3. PRESENTATIONS TABLE
    # ==========================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS presentations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic TEXT NOT NULL,

            subject TEXT NOT NULL,

            presentation_date TEXT NOT NULL,

            preparation_hours INTEGER NOT NULL,

            importance TEXT NOT NULL,

            status TEXT DEFAULT 'Planned'

        )
    """)


    # Save changes

    connection.commit()


    # Close database connection

    connection.close()