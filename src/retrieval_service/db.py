# src/retrieval_service/db.py
import os
from flask import g
# Use relative imports for datastore
from .datastore.factory import create_datastore
from .datastore.providers.cloudsql_postgres import Config

# This variable will hold the single, shared datastore client
_datastore = None

def get_db():
    """
    Connects to the database if not already connected.
    Uses the application context (g) to store the connection for a single request.
    """
    if 'datastore' not in g:
        # If there's no connection for this request, create one.
        db_config = Config(
            kind="cloudsql-postgres",
            project=os.environ.get("DB_PROJECT"),
            region=os.environ.get("DB_REGION"),
            instance=os.environ.get("DB_INSTANCE"),
            user=os.environ.get("DB_USER"),
            # Password is automatically handled in the Datastore init
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
        )
        g.datastore = create_datastore(db_config)
    
    # Return an active session from the datastore
    if 'db_session' not in g:
        g.db_session = g.datastore.get_session()
        
    return g.db_session

def close_db(e=None):
    """Closes the database connection if it exists."""
    # Close the session used for the request
    db_session = g.pop('db_session', None)
    if db_session is not None:
        db_session.close()
    
    # Note: We don't close the entire datastore engine here, only the session.