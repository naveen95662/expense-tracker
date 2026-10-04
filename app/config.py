import os

# Names and backend come from the environment; no secrets in this file.
TABLE_NAME = os.environ.get("TABLE_NAME", "expenses")
STORE_BACKEND = os.environ.get("STORE_BACKEND", "memory")
