# Import from the current package using relative imports
from .providers.cloudsql_postgres import CloudSQLPostgresDatastore, Config

def create_datastore(config: Config):
    """
    Factory function to create a datastore instance.
    """
    if config.kind == "cloudsql-postgres":
        return CloudSQLPostgresDatastore(config)
    else:
        raise ValueError(f"Unsupported datastore kind: {config.kind}")