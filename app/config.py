import os

# Read from the environment now so later DynamoDB work does not put names in code.
# The in-memory store does not use this value.
TABLE_NAME = os.environ.get("TABLE_NAME", "expenses")
