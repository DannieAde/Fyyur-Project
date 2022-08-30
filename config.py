import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Damilola@localhost:5432/fyyur'
# DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
# DB_USER = os.getenv('DB_USER', 'postgres')
# DB_PASSWORD = os.getenv('DB_PASSWORD', 'Damilola')
# DB_NAME = os.getenv('DB_NAME', 'fyyur')


# DB_PATH = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = 'guessmykey'
