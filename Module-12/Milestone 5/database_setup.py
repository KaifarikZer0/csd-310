#   Title: database_setup.py
#   Authors: Casey Rose, Darreon Tolen and Jennifer Hoitenga
#   Date: 03/02/2025
#   Description: Bacchus Winery database initialization script.
#   Source: Find Business Days - https://stackoverflow.com/questions/2224742/most-recent-previous-business-day-in-python
#   Source: Print formatted table: https://stackoverflow.com/questions/48138015/printing-table-in-format-without-using-a-library-sqlite-3-python


# Import Statements
import mysql.connector  # to connect
from mysql.connector import errorcode
from db_config import connect_db  # Import shared db_config file
import logging
from log_config import logger  # Import shared logging configuration
import traceback  # for detailed error diagnostics
import dotenv  # to use .env file
from dotenv import dotenv_values
from datetime import datetime, date, timedelta  # Import date for date formatting
from decimal import Decimal  # Import for decimal formatting


# Drop and recreate the database
def setup_database():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DROP DATABASE IF EXISTS winery")
    cursor.execute("CREATE DATABASE winery")

    conn.commit()  # Commit changes to the database
    conn.close()  # Close the connection
    print("Database 'winery' has been created.")


try:
    # Try/catch block for handling potential MySQL database errors

    # Connect to the winery database
    db = connect_db(database="winery")  # Connect to database

    # Output the connection status
    print("\n Successfully connected to the Winery MySQL database.")

    # Open a new cursor for executing database queries.
    cursor = db.cursor()

    # Create the tables
    def create_tables():
        conn = connect_db(database="winery")  # Connect to database
        cursor = conn.cursor()

        tables = {
            # Stores winery information
            "winery": """
                CREATE TABLE winery (
                    winery_id INT AUTO_INCREMENT PRIMARY KEY,
                    winery_name VARCHAR(75) NOT NULL,
                    winery_phone VARCHAR(20) NOT NULL,
                    winery_email VARCHAR(100) NOT NULL UNIQUE
                )
            """,
            # Stores supplier details
            "supplier": """
                CREATE TABLE supplier (
                    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
                    supplier_name VARCHAR(75) NOT NULL,
                    supplier_phone VARCHAR(20) NOT NULL,
                    supplier_email VARCHAR(100) NOT NULL UNIQUE
                )
            """,
            # Stores distributor details
            "distributor": """
                CREATE TABLE distributor (
                    distributor_id INT AUTO_INCREMENT PRIMARY KEY,
                    distributor_name VARCHAR(75) NOT NULL,
                    distributor_phone VARCHAR(20) NOT NULL,
                    distributor_email VARCHAR(100) NOT NULL UNIQUE
                )
            """,
            # Stores job positions
            "job_position": """
                CREATE TABLE job_position (
                    position_id INT AUTO_INCREMENT PRIMARY KEY,
                    position_name VARCHAR(75) UNIQUE NOT NULL,
                    salary_min DECIMAL(10,2) NOT NULL,
                    salary_max DECIMAL(10,2) NOT NULL
                )
            """,
            # Stores employees first so department can reference it
            "employee": """
                CREATE TABLE employee (
                    employee_id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(75) NOT NULL,
                    last_name VARCHAR(75) NOT NULL,
                    department_id INT NULL,
                    winery_id INT NOT NULL,
                    position_id INT NOT NULL,
                    CONSTRAINT fk_employee_winery FOREIGN KEY (winery_id) 
                        REFERENCES winery(winery_id),
                    CONSTRAINT fk_employee_job_position FOREIGN KEY (position_id) 
                        REFERENCES job_position(position_id)
                )
            """,
            # Stores department details and allows manager id to be null initially
            "department": """
                CREATE TABLE department (
                    department_id INT AUTO_INCREMENT PRIMARY KEY,
                    department_name VARCHAR(75) UNIQUE NOT NULL,
                    manager_id INT NULL,
                    CONSTRAINT fk_department_employee FOREIGN KEY (manager_id) 
                        REFERENCES employee(employee_id) ON DELETE SET NULL
                )
            """,
            # Stores different types of wine
            "wine_type": """
                CREATE TABLE wine_type (
                    wine_type_id INT AUTO_INCREMENT PRIMARY KEY,
                    wine_type_name VARCHAR(75) UNIQUE NOT NULL
                )
            """,
            # Stores different grape varieties
            "grape_variety": """
                CREATE TABLE grape_variety (
                    grape_variety_id INT AUTO_INCREMENT PRIMARY KEY,
                    grape_variety_name VARCHAR(75) UNIQUE NOT NULL
                )
            """,
            # Links wine types to grape varieties
            "wine_grape_variety": """
                CREATE TABLE wine_grape_variety (
                    wine_type_id INT NOT NULL,
                    grape_variety_id INT NOT NULL,
                    PRIMARY KEY (wine_type_id, grape_variety_id),
                    CONSTRAINT fk_wine_grape_variety_wine_type FOREIGN KEY (wine_type_id) 
                        REFERENCES wine_type(wine_type_id),
                    CONSTRAINT fk_wine_grape_variety_grape_variety FOREIGN KEY (grape_variety_id) 
                        REFERENCES grape_variety(grape_variety_id)
                )
            """,
            # Stores information about different wines
            "wines": """
                CREATE TABLE wines (
                    wine_id INT AUTO_INCREMENT PRIMARY KEY,
                    inventory_quantity INT NOT NULL,
                    price_per_bottle DECIMAL(10,2) NOT NULL,
                    vintage_year YEAR NOT NULL,
                    winery_id INT NOT NULL,
                    wine_type_id INT NOT NULL,
                    CONSTRAINT fk_wines_winery FOREIGN KEY(winery_id) 
                        REFERENCES winery(winery_id),
                    CONSTRAINT fk_wines_wine_type FOREIGN KEY(wine_type_id) 
                        REFERENCES wine_type(wine_type_id)
                )
            """,
            # Stores supply orders
            "supply_type": """
                CREATE TABLE supply_type (
                supply_type_id INT AUTO_INCREMENT PRIMARY KEY,
                type_name VARCHAR(75) NOT NULL UNIQUE
                )
            """,
            # Stores supply orders
            "supply": """
                CREATE TABLE supply (
                    supply_id INT AUTO_INCREMENT PRIMARY KEY,
                    order_date DATE NOT NULL,
                    expected_date DATE NOT NULL,
                    delivery_date DATE NOT NULL,
                    supplier_id INT NOT NULL,
                    winery_id INT NOT NULL,
                    CONSTRAINT fk_supply_winery FOREIGN KEY(winery_id) 
                        REFERENCES winery(winery_id),
                    CONSTRAINT fk_supply_supplier FOREIGN KEY(supplier_id) 
                        REFERENCES supplier(supplier_id)
                )
            """,
            # Stores details of each supply order
            "supply_details": """
                CREATE TABLE supply_details (
                    supply_id INT NOT NULL,
                    supply_type_id INT NOT NULL,
                    quantity INT NOT NULL,
                    PRIMARY KEY (supply_id, supply_type_id),
                    CONSTRAINT fk_supply_details_supply FOREIGN KEY (supply_id) 
                        REFERENCES supply(supply_id),
                    CONSTRAINT fk_supply_details_supply_type FOREIGN KEY (supply_type_id) 
                        REFERENCES supply_type(supply_type_id)
                )
            """,
            # Stores different order statuses (Ordered, Delivered, Canceled)
            "order_status": """
                CREATE TABLE order_status (
                order_status_id INT AUTO_INCREMENT PRIMARY KEY,
                status_name VARCHAR(50) UNIQUE NOT NULL
                )
            """,
            # Stores sales transactions
            "sales": """
                CREATE TABLE sales (
                    sale_id INT AUTO_INCREMENT PRIMARY KEY,
                    quantity INT NOT NULL,
                    sale_date DATE NOT NULL,
                    wine_id INT NOT NULL,
                    distributor_id INT NOT NULL,
                    order_status_id INT NOT NULL,
                    CONSTRAINT fk_sales_wines FOREIGN KEY(wine_id) 
                        REFERENCES wines(wine_id),
                    CONSTRAINT fk_sales_distributor FOREIGN KEY(distributor_id) 
                        REFERENCES distributor(distributor_id),
                    CONSTRAINT fk_sales_order_status FOREIGN KEY(order_status_id) 
                        REFERENCES order_status(order_status_id)
                )
            """,
            # Stores employee work hours
            "work_hours": """
                CREATE TABLE work_hours (
                    work_id INT AUTO_INCREMENT PRIMARY KEY,
                    work_date DATE NOT NULL,
                    hours_worked INT NOT NULL,
                    employee_id INT NOT NULL,
                    CONSTRAINT fk_work_hours_employee FOREIGN KEY(employee_id) 
                        REFERENCES employee(employee_id)
                )
            """
        }

        # Iterate through the table and execute each query
        for table_name, query in tables.items():
            cursor.execute(query)
            print(f"Table '{table_name}' created.")

        conn.commit()  # Commit changes to the database
        conn.close()  # Close the connection

    def insert_data():
        conn = connect_db(database="winery")  # Connect to database
        cursor = conn.cursor()

        # Define total employees
        employee_ids = list(range(1, 28))  # Employee IDs from 1 to 27

        # Define work hour exceptions per employee per month
        employee_exceptions = {
            "2024-01-31": {
                1: 192, 5: 192, 9: 200, 13: 192, 20: 200, 26: 192
            },
            "2024-02-29": {
                2: 184, 9: 184, 27: 184
            },
            "2024-03-31": {
                1: 184, 5: 184, 7: 184, 9: 184, 12: 176, 18: 160, 27: 184
            },
            "2024-04-30": {
                1: 184, 5: 184, 9: 184, 13: 184, 27: 184
            },
            "2024-05-31": {
                2: 200, 7: 192, 7: 192, 27: 184
            },
            "2024-06-30": {
                1: 168, 5: 168, 9: 168, 18: 160, 27: 176
            },
            "2024-07-31": {
                27: 192
            },
            "2024-08-31": {
                1: 168, 11: 184, 13: 168, 20: 160, 26: 184
            },
            "2024-09-30": {
                3: 176, 4: 176, 5: 176, 6: 176, 27: 176
            },
            "2024-10-31": {
                1: 192, 5: 192, 9: 192, 13: 192, 15: 192, 26: 192
            },
            "2024-11-30": {
                1: 184, 5: 184, 9: 184, 12: 184, 13: 184, 26: 184, 27: 184
            },
            "2024-12-31": {
                1: 192, 2: 192, 4: 192, 8: 192, 15: 192, 21: 192, 25: 192, 27: 192
            },
            "2025-01-31": {
                1: 168, 2: 168, 3: 168, 4: 168, 5: 168, 6: 160, 27: 160
            }
        }

        # Function to count business days for each month
        def count_business_days(year, month):
            first_day = date(year, month, 1)
            last_day = date(year, month, 28)  # Start with 28th
            while last_day.month == month:  # Find the last day of the month
                last_day += timedelta(days=1)
            last_day -= timedelta(days=1)  # Adjust to last valid date

            business_days = sum(1 for day in range((last_day - first_day).days + 1)
                                if (first_day + timedelta(days=day)).weekday() < 5)  # Monday-Friday only
            return business_days * 8  # Convert to work hours

        # Generate SQL statements
        sql_statements = []
        for date_str in employee_exceptions:
            year, month, _ = map(int, date_str.split('-'))
            default_hours = count_business_days(
                year, month)  # Business days * 8 hours

            for emp_id in employee_ids:
                hours = employee_exceptions[date_str].get(
                    emp_id, default_hours)  # Use exceptions or default hours
                sql_statements.append(f"({emp_id}, '{date_str}', {hours})")

        data = {
            # Insert winery
            "winery": """INSERT INTO winery (winery_name, winery_phone, winery_email) VALUES
                ('Bacchus Winery', '555-867-5309', 'bacchuswinery@gmail.com')""",
            # Insert Suppliers
            "supplier": """INSERT INTO supplier (supplier_name, supplier_phone, supplier_email) VALUES
                ('Prestige Bottling Co.', '555-983-6789', 'prestigebottlingco@gmail.com'),
                ('Label and Crate', '555-487-1254', 'labelcrate@yahoo.com'),
                ('Titan Barrel Works', '555-677-4617', 'titanbarrel@gmail.com')""",
            # Insert Distributors
            "distributor": """INSERT INTO distributor (distributor_name, distributor_phone, distributor_email) VALUES
                ('Lumon Vineworks', '555-358-6479', 'lumonvineworks@gmail.com'),
                ('Macrodata Vintners', '555-942-1724', 'macrodatavintners@gmail.com'),
                ('Severed Cellars', '555-867-2463', 'severedcellars@gmail.com'),
                ('Harmony Wines & Spirits', '555-252-4119', 'harmonywines@yahoo.com')""",
            # Insert Job Positions
            "job_position": """INSERT INTO job_position (position_name, salary_min, salary_max) VALUES
                ('Owner', '80000.00', '250000.00'),
                ('Manager', '50000.00', '100000.00'),
                ('Assistant', '35000.00', '55000.00'),
                ('Production Line Worker', '30000.00', '45000.00')""",
            # Insert Departments
            "department": """INSERT INTO department (department_name) VALUES
                ('Operations'),
                ('Finance'),
                ('Marketing'),
                ('Production'),
                ('Distribution')""",
            # Insert Employees
            "employee": """INSERT INTO employee (first_name, last_name, position_id, department_id, winery_id) VALUES
                ('Stan', 'Bacchus', 1, 1, 1),
                ('Davis', 'Bacchus', 1, 1, 1),
                ('Janet', 'Collins', 2, 2, 1),
                ('Roz', 'Murphy', 2, 3, 1),
                ('Bob', 'Ulrich', 3, 3, 1),
                ('Henry', 'Doyle', 2, 4, 1),
                ('Seth', 'Milchick', 4, 4, 1),
                ('Mark', 'Scout', 4, 4, 1),
                ('Helly', 'Riggs', 4, 4, 1),
                ('Dylan', 'George', 4, 4, 1),
                ('Irving', 'Bailiff', 4, 4, 1),
                ('Harmony', 'Cobel', 4, 4, 1),
                ('Devon', 'Scout-Hale', 4, 4, 1),
                ('Gemma', 'Scout', 4, 4, 1),
                ('Burt', 'Goodman', 4, 4, 1),
                ('Kier', 'Eagan', 4, 4, 1),
                ('Doug', 'Graner', 4, 4, 1),
                ('Ricken', 'Hale', 4, 4, 1),
                ('Natalie', 'Kalen', 4, 4, 1),
                ('Petey', 'Kilmer', 4, 4, 1),
                ('Jame', 'Eagan', 4, 4, 1),
                ('Gretchen', 'George', 4, 4, 1),
                ('Dario', 'Rossi', 4, 4, 1),
                ('Asal', 'Reghabi', 4, 4, 1),
                ('Mark', 'Wilkins', 4, 4, 1),
                ('Gabby', 'Arteta', 4, 4, 1),
                ('Maria', 'Costanza', 2, 5, 1)""",
            # Update Dept Managers
            "update_department_managers": """UPDATE department
                SET manager_id = CASE
                WHEN department_name = 'Finance' THEN 3  -- Janet is Finance Manager
                WHEN department_name = 'Marketing' THEN 4  -- Roz is Marketing Manager
                WHEN department_name = 'Production' THEN 6  -- Henry is Production Manager
                WHEN department_name = 'Distribution' THEN 27  -- Maria is Distribution Manager
                END
            """,
            # Insert Wine Types
            "wine_type": """INSERT INTO wine_type (wine_type_name) VALUES
                ('Merlot'), ('Cabernet'), ('Chablis'), ('Chardonnay')""",
            # Insert Grape Varieties
            "grape_variety": """INSERT INTO grape_variety (grape_variety_name) VALUES
                ('Cabernet Franc'), ('Sauvignon Blanc'), ('Chardonnay'), ('Pinot Noir')""",
            # Insert relationship between wine type and grape variety
            "wine_grape_variety": """INSERT INTO wine_grape_variety (wine_type_id, grape_variety_id) VALUES
                (1, 1),  -- Merlot and Cabernet Franc
                (2, 2),  -- Cabernet and Sauvignon Blanc
                (3, 3),  -- Chablis and Chardonnay
                (4, 4)  -- Chardonnay and Pinot Noir   """,
            # Insert Wines
            "wines": """INSERT INTO wines(wine_type_id, inventory_quantity, price_per_bottle, vintage_year, winery_id) VALUES
                ('1', '9500', '18.00', '2025', 1),
                ('2', '9850', '20.00', '2025', 1),
                ('3', '9640', '25.00', '2025', 1),
                ('4', '9900', '24.00', '2025', 1)""",
            # Insert Supply Types
            "supply_type": """INSERT INTO supply_type (type_name) VALUES
                ('Bottles'),
                ('Corks'),
                ('Labels'),
                ('Boxes'),
                ('Vats'),
                ('Tubing')""",
            # Insert Supply Orders
            "supply": """INSERT INTO supply(order_date, expected_date, delivery_date, supplier_id, winery_id) VALUES
                ('2024-11-07', '2024-11-11', '2024-11-18', 1, 1), -- Order 1 (Bottles and Corks)
                ('2024-11-07', '2024-11-11', '2024-11-11', 2, 1), -- Order 2 (Labels and Boxes)
                ('2024-11-07', '2024-11-11', '2024-11-11', 3, 1), -- Order 3 (Vats and Tubing)
                ('2024-12-16', '2024-12-20', '2024-12-20', 1, 1), -- Order 4 (Bottles and Corks)
                ('2024-12-16', '2024-12-20', '2024-12-25', 2, 1), -- Order 5 (Labels and Boxes)
                ('2024-12-16', '2024-12-20', '2024-12-23', 3, 1), -- Order 6 (Vats and Tubing)
                ('2025-01-27', '2025-01-31', '2025-02-10', 1, 1), -- Order 7 (Bottles and Corks)
                ('2025-01-27', '2025-01-31', '2025-02-14', 2, 1), -- Order 8 (Labels and Boxes)
                ('2025-01-27', '2025-01-31', '2025-02-05', 3, 1) -- Order 9 (Vats and Tubing) """,
            # Insert Supply Details
            "supply_details": """INSERT INTO supply_details (supply_id, supply_type_id, quantity) VALUES
                (1, 1, 100), -- 100 Bottles
                (1, 2, 200), -- 200 Corks
                (2, 3, 500), -- 500 Labels
                (2, 4, 250), -- 250 Boxes
                (3, 5, 50), -- 50 Vats
                (3, 6, 75), -- 200 Tubing
                (4, 1, 200), -- 200 Bottles
                (4, 2, 100), -- 100 Corks
                (5, 3, 1000), -- 1000 Labels
                (5, 4, 500), -- 500 Boxes
                (6, 5, 100), -- 100 Vats
                (6, 6, 150), -- 150 Tubing
                (7, 1, 200), -- 200 Bottles
                (7, 2, 100), -- 100 Corks
                (8, 3, 1000), -- 1000 Labels
                (8, 4, 500), -- 500 Boxes
                (9, 5, 100), -- 100 Vats
                (9, 6, 150) -- 150 Tubing """,
            # Insert Order Statuses
            "order_status": """INSERT INTO order_status (status_name) VALUES
                ('Ordered'), ('Delivered'), ('Canceled')""",
            # Insert Sales
            "sales": """INSERT INTO sales(quantity, sale_date, order_status_id, wine_id, distributor_id) VALUES
                ('700', '2024-10-07', 2, 1, 1),
                ('500', '2024-10-07', 2, 2, 2),
                ('400', '2024-10-07', 2, 3, 3),
                ('600', '2024-10-07', 2, 4, 4),
                ('700', '2024-10-21', 2, 1, 1),
                ('500', '2024-10-21', 2, 2, 2),
                ('200', '2024-10-21', 2, 3, 3),
                ('600', '2024-10-21', 2, 4, 4),
                ('1000', '2024-11-11', 2, 1, 1),
                ('1100', '2024-11-11', 2, 2, 2),
                ('900', '2024-11-11', 2, 3, 3),
                ('1200', '2024-11-11', 2, 4, 4),
                ('500', '2024-12-02', 2, 1, 1),
                ('500', '2024-12-02', 2, 2, 2),
                ('500', '2024-12-02', 2, 3, 3),
                ('600', '2024-12-02', 2, 4, 4),
                ('1000', '2024-12-16', 2, 1, 1),
                ('1100', '2024-12-16', 2, 2, 2),
                ('900', '2024-12-16', 2, 3, 3),
                ('1200', '2024-12-16', 2, 4, 4),
                ('1000', '2025-01-20', 2, 1, 1),
                ('1200', '2025-01-20', 2, 2, 2),
                ('800', '2025-01-20', 2, 3, 3),
                ('1200', '2025-01-20', 2, 4, 4)""",
            # Insert Work Hours
            "work_hours": "INSERT INTO work_hours (employee_id, work_date, hours_worked) VALUES " + ",\n".join(sql_statements) + ";"
        }

        for table_name, query in data.items():
            cursor.execute(query)
            print(f"Data inserted into '{table_name}'.")

        conn.commit()  # Commit changes to the database
        conn.close()  # Close the connection

    def display_data():
        conn = connect_db(database="winery")  # Connect to database
        cursor = conn.cursor()

        tables = ["winery", "department", "job_position", "work_hours", "employee", "supplier", "supply_type", "supply_details", "supply",
                  "wine_type", "wine_grape_variety", "grape_variety", "wines", "order_status", "distributor", "sales"]

        for table in tables:
            # Table header
            print(f"\n-- DISPLAYING {table.upper()} RECORDS --")

            try:
                query = f"SELECT * FROM {table}"
                cursor.execute(query)  # Execute the insert query
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]

                if rows:
                    # Determine column widths
                    col_widths = [max(len(str(col)), max(
                        len(str(row[i])) for row in rows)) for i, col in enumerate(column_names)]

                    # Print table header
                    header = " | ".join(
                        f"{col_name:<{col_widths[i]}}" for i, col_name in enumerate(column_names))
                    print("-" * len(header))
                    print(header)
                    print("-" * len(header))

                    for row in rows:
                        # Convert date fields to a readable format
                        formatted_row = [
                            f"{field.strftime('%Y-%m-%d')}" if isinstance(field, date) else
                            f"{field.strftime('%Y-%m-%d %H:%M:%S')}" if isinstance(field, datetime) else
                            f"{field:,.2f}" if isinstance(field, Decimal) else
                            "NULL" if field is None else str(field)
                            for field in row
                        ]

                        print(" | ".join(
                            f"{field:<{col_widths[i]}}" for i, field in enumerate(formatted_row)))
                    print()
                else:
                    print(f"Table '{table}' is empty.")

            except mysql.connector.Error as err:
                print(f"[ERROR] Failed to retrieve data from '{table}': {err}")

        conn.close()  # Close the connection

    # Run database setup
    if __name__ == "__main__":
        setup_database()
        create_tables()
        insert_data()

        print("\nThe Winery database setup is now complete!")

        # Call display_data()
        display_data()

  # Close the cursor.
    cursor.close()


except mysql.connector.Error as err:
    error_message = ""

    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        error_message = f"Error: The supplied username or password are invalid. MySQL Error Code: {err.errno}"

    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        error_message = f"Error: The specified database does not exist. MySQL Error Code: {err.errno}"

    else:
        error_message = f"General MySQL Error: {err}"

    print(error_message)  # Prints the error for immediate feedback.
    logging.error(error_message)  # Logs the error message.
    # Logs the full traceback for debugging.
    logging.error(traceback.format_exc())

finally:
    # Close the connection to MySQL
    if 'db' in locals() and db.is_connected():
        db.close()
        print("Connection closed safely.")
