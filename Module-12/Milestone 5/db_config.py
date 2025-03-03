#   Title: db_config.py
#    Authors: Casey Rose, Darreon Tolen and Jennifer Hoitenga
#    Date: 03/02/2025
#    Description: Database connection shared file.

import mysql.connector
from dotenv import dotenv_values

# Load secrets
secrets = dotenv_values("C:\\csd\\csd-310\\module-10\\.env")


# Database config object
def connect_db(database=None):
    return mysql.connector.connect(
        user=secrets["USER"],
        password=secrets["PASSWORD"],
        host=secrets["HOST"],
        database=database if database else None
    )
