import os

# Secret and DB config come from environment when possible.
SECRET_KEY = os.environ.get('LAB6_SECRET_KEY', 'secret-key')

# Prefer an explicit SQLALCHEMY_DATABASE_URI env var. If not provided, try to
# build from MySQL env vars. Otherwise fall back to a local sqlite for quick tests.
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
if not SQLALCHEMY_DATABASE_URI:
    mysql_user = os.environ.get('MYSQL_USER', os.environ.get('LAB6_MYSQL_USER'))
    mysql_password = os.environ.get('MYSQL_PASSWORD', os.environ.get('LAB6_MYSQL_PASSWORD'))
    mysql_host = os.environ.get('MYSQL_HOST', os.environ.get('LAB6_MYSQL_HOST'))
    mysql_db = os.environ.get('MYSQL_DATABASE', os.environ.get('LAB6_MYSQL_DATABASE'))
    if mysql_user and mysql_password and mysql_host and mysql_db:
        SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"
    else:
        # Quick local sqlite fallback for testing on servers without MySQL configured
        SQLALCHEMY_DATABASE_URI = 'sqlite:///~/lab6_local.db'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    'media',
    'images'
)
