import os
from pathlib import Path
from dotenv import load_dotenv

# Locate the base directory and load .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    """
    Application configuration class.
    Reads sensitive settings and credentials from environment variables.
    """
    # Flask Session & Security Key
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-dev-secret-key-replace-in-prod')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')

    # MySQL Database Connection Credentials
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'student_management')
    DB_PORT = int(os.getenv('DB_PORT', 3306))

    # Helper dictionary for passing directly to mysql.connector.connect(**Config.DB_CONFIG)
    @classmethod
    def get_db_config(cls):
        return {
            'host': cls.DB_HOST,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'port': cls.DB_PORT
        }

