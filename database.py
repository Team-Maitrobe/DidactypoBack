from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlite3
from pathlib import Path

DATABASE_FILE = Path(__file__).parent / 'db.sqlite3'  # Dynamically set database path

engine = create_engine(f'sqlite:///{DATABASE_FILE}', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def execute_sql_file(file_path: Path):
    """Execute the SQL commands from a file."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        with open(file_path, "r", encoding='UTF-8') as file:
            sql_script = file.read()
            conn.executescript(sql_script)
        conn.commit()

def is_initialized(db, model):
    """Check if the database is initialized."""
    cursor = db.query(model).first()
    return cursor is not None