# src/retrieval_service/db.py

import os
from flask import g
from datastore.factory import create_datastore
from datastore.providers.cloudsql_postgres import Config

_datastore = None

def get_db():
    """
    Connects to the database if not already connected.
    """
    global _datastore
    if _datastore is None:
        db_config = Config(
            kind="cloudsql-postgres",
            project=os.environ.get("DB_PROJECT"),
            region=os.environ.get("DB_REGION"),
            instance=os.environ.get("DB_INSTANCE"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
        )
        _datastore = create_datastore(db_config)
    return _datastore

def close_db(e=None):
    """Closes the database connection."""
    global _datastore
    if _datastore is not None:
        _datastore.close()
        _datastore = None