import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Use psycopg2 as specified in requirements.txt
from google.cloud.sql.connector import Connector, IPTypes
from pydantic import BaseModel

class Config(BaseModel):
    kind: str
    project: str = None
    region: str = None
    instance: str = None
    user: str
    password: str = None   # Allow password to be optional in config if set via env var
    database: str

class CloudSQLPostgresDatastore:
    def __init__(self, config: Config):
        self.config = config
        # Ensure password is set, preferring environment variable if not in config
        if not self.config.password:
            self.config.password = os.environ.get("DB_PASSWORD")
        
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _create_engine(self):
        """
        Creates a SQLAlchemy engine for connecting to Cloud SQL for PostgreSQL.
        """
        if not all([self.config.project, self.config.region, self.config.instance]):
            # Fallback for local development or migration steps
            db_host = os.environ.get("DB_HOST", "127.0.0.1")
            db_port = os.environ.get("DB_PORT", "5432")
            connection_string = (
                f"postgresql+psycopg2://{self.config.user}:{self.config.password}@"
                f"{db_host}:{db_port}/{self.config.database}"
            )
            return create_engine(connection_string)

        # Use Cloud SQL Connector for Cloud Run environment
        def getconn():
            connector = Connector()
            conn = connector.connect(
                f"{self.config.project}:{self.config.region}:{self.config.instance}",
                "psycopg2", # Use psycopg2 driver
                user=self.config.user,
                password=self.config.password,
                db=self.config.database,
                # Use PRIVATE IP if available, otherwise PUBLIC
                ip_type=IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC,
            )
            return conn

        engine = create_engine(
            "postgresql+psycopg2://", # Use psycopg2 dialect
            creator=getconn,
        )
        return engine

    def get_session(self):
        return self.SessionLocal()

    def close(self):
        """
        Closes the database engine.
        """
        if self.engine:
            self.engine.dispose()