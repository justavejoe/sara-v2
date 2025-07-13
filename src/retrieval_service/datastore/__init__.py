# Copyright 2024 Google LLC
# (license header)

from . import providers
from .datastore import Client

# The Config is now just the one from our single provider
Config = providers.cloudsql_postgres.Config

# Expose the public names.
__all__ = ["Client", "Config", "providers"]