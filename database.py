from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlite3
from pathlib import Path
import os

# Check if we're running in Docker by looking for the environment variable
is_docker = os.environ.get('DOCKER_ENV', False)

# Set database path - if in Docker, use the data directory, otherwise use the current directory
if is_docker:
    # Ensure data directory exists
    data_dir = Path('/app/data')
    data_dir.mkdir(exist_ok=True)
    DATABASE_FILE = data_dir / 'db.sqlite3'
else:
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