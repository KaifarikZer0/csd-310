import mysql.connector
from mysql.connector import errorcode

import dotenv
from dotenv import dotenv_values

# Load environment variables
secrets = dotenv_values(r"C:\csd\csd-310\module-6\.env") 

# Database configuration
config = {
    "user": secrets["USER"],
    "password": secrets["PASSWORD"],
    "host": secrets["HOST"],
    "database": secrets["DATABASE"],
    "raise_on_warnings": True
}

try:
    # Connect to the MySQL database
    db = mysql.connector.connect(**config)
    print(f"Connected to MySQL database: {db.database}")

    # Create a cursor object to execute queries
    cursor = db.cursor()

    # Query 1: Select all fields from the studio table
    query1 = "SELECT * FROM studio"
    cursor.execute(query1)
    print("\nOutput of Query 1: All fields from the studio table")
    for row in cursor:
        print(row)

    # Query 2: Select all fields from the genre table
    query2 = "SELECT * FROM genre"
    cursor.execute(query2)
    print("\nOutput of Query 2: All fields from the genre table")
    for row in cursor:
        print(row)

    # Query 3: Select movie names with runtime less than 120 minutes
    query3 = "SELECT film_name FROM film WHERE film_runtime < 120"
    cursor.execute(query3)
    print("\nOutput of Query 3: Movie names with runtime less than 120 minutes")
    for row in cursor:
        print(row[0])

    # Query 4: Select film names and directors grouped by director
    query4 = "SELECT film_name, director FROM film GROUP BY director"
    cursor.execute(query4)
    print("\nOutput of Query 4: Film names and directors grouped by director")
    for row in cursor:
        print(f"Director: {row[1]}, Film: {row[0]}")

except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    db = None

finally:
    if db:
        db.close()