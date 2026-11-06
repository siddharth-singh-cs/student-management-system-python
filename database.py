"""
Database module for Student Management System.
Handles connection management and raw parameterized SQL queries using mysql-connector-python.
"""

import mysql.connector
from mysql.connector import Error
from config import Config


def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database.
    Catches connection errors and provides clear troubleshooting messages.
    """
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        return connection
    except Error as err:
        print(f"[DATABASE ERROR] Failed to connect to MySQL: {err}")
        print("Troubleshooting tips:")
        print("  1. Is MySQL Server running on your computer?")
        print("  2. Did you create the database 'student_management' using schema.sql?")
        print("  3. Check DB_USER, DB_PASSWORD, and DB_PORT in your .env file.")
        raise err


def execute_query(query, params=None, fetch_one=False):
    """
    Executes a SELECT query using a dictionary cursor and returns results.

    :param query: SQL SELECT string with %s placeholders
    :param params: Tuple or list of parameter values
    :param fetch_one: Boolean; if True, returns a single dictionary or None.
                      If False, returns a list of dictionaries.
    :return: Dict or List[Dict]
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        # dictionary=True ensures rows are returned as dicts {'col_name': value}
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def execute_commit(query, params=None):
    """
    Executes an INSERT, UPDATE, or DELETE query and commits changes.

    :param query: SQL statement with %s placeholders
    :param params: Tuple or list of parameter values
    :return: dict with 'lastrowid' (for INSERTs) and 'rowcount' (affected rows)
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        connection.commit()
        return {
            'lastrowid': cursor.lastrowid,
            'rowcount': cursor.rowcount
        }
    except Error as err:
        if connection:
            connection.rollback()
        raise err
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def test_connection():
    """
    Quick helper function to verify MySQL connectivity.
    Can be run directly via: python database.py
    """
    try:
        conn = get_db_connection()
        if conn.is_connected():
            db_info = conn.get_server_info()
            print(f"SUCCESS: Connected to MySQL Server version {db_info}")
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"Active database: {record[0]}")
            cursor.close()
            conn.close()
            return True
    except Error as e:
        print(f"Connection test failed: {e}")
        return False


if __name__ == '__main__':
    print("Testing MySQL connection from database.py...")
    test_connection()

