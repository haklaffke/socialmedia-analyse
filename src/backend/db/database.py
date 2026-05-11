import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

"""
Connection settings for the Postgres database.
The connection string can be overridden via the environment variable DB_URL.
Format: postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DBNAME
"""
DB_URL = os.getenv(
    "DB_URL",
    "postgresql+psycopg2://absa:absa@localhost:5432/absa",
)

engine = create_engine(DB_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

