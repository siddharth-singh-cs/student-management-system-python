"""
Database Setup & Initialization Utility
Reads schema.sql and initializes the MySQL database 'student_management' with starter tables and seed records.

Usage:
    python setup_db.py
    python setup_db.py <your_mysql_password>
"""

import sys
import os
from pathlib import Path
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'
SCHEMA_PATH = BASE_DIR / 'schema.sql'

load_dotenv(ENV_PATH)


def run_setup(password=None):
    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    port = int(os.getenv('DB_PORT', 3306))

    if password is None:
        # Check command line arguments first
        if len(sys.argv) > 1:
            password = sys.argv[1]
        else:
            # Check .env next
            env_pwd = os.getenv('DB_PASSWORD', '')
            if env_pwd:
                password = env_pwd
            else:
                print("=" * 60)
                print("MySQL Database Setup Wizard")
                print("=" * 60)
                print(f"Connecting to MySQL at {host}:{port} as user '{user}'...")
                password = input("Enter your MySQL root password (press Enter if blank): ").strip()

    print("\n[1/3] Connecting to MySQL Server...")
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        if not conn.is_connected():
            print("Failed to establish connection.")
            return False

        print(f"  -> Connected to MySQL Server version {conn.get_server_info()}!")

        print("\n[2/3] Reading and executing schema.sql...")
        if not SCHEMA_PATH.exists():
            print(f"Error: Could not find schema file at {SCHEMA_PATH}")
            conn.close()
            return False

        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        cursor = conn.cursor()
        # Execute script statements
        # mysql-connector-python supports executing multiple statements with multi=True
        results = cursor.execute(sql_script, multi=True)
        for res in results:
            pass  # iterate through all statement results to complete execution

        conn.commit()
        cursor.close()
        conn.close()
        print("  -> Database 'student_management' and tables created successfully!")
        print("  -> Sample courses and starter students populated.")

        print("\n[3/3] Updating .env file with verified credentials...")
        update_env_file(password)
        print("  -> .env file successfully updated!")

        print("\n" + "=" * 60)
        print("SUCCESS! Your database is fully configured and ready.")
        print("Open your browser and visit: http://127.0.0.1:5000")
        print("=" * 60)
        return True

    except Error as err:
        print(f"\n[ERROR] MySQL Connection Failed: {err}")
        print("\nTroubleshooting:")
        print("  1. Verify your MySQL root password.")
        print("  2. Ensure the MySQL service (e.g. MySQL80) is running in Windows Services.")
        return False


def update_env_file(password):
    """Safely updates or sets DB_PASSWORD in the .env file."""
    lines = []
    if ENV_PATH.exists():
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()

    updated = False
    new_lines = []
    for line in lines:
        if line.strip().startswith('DB_PASSWORD='):
            new_lines.append(f"DB_PASSWORD={password}\n")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"\nDB_PASSWORD={password}\n")

    with open(ENV_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


if __name__ == '__main__':
    run_setup()
