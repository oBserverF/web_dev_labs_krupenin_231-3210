import os

# Load secrets and DB credentials from environment variables when available.
# This avoids committing passwords to the repository. On PythonAnywhere set
# these variables in your WSGI file or via other secure mechanism.

SECRET_KEY = os.environ.get(
	'LAB4_SECRET_KEY',
	"1184f940be07b6ecfcf5e05a5ef90504b8ac3e7cc30899d46858ed7eea259d85",
)

MYSQL_USER = os.environ.get('MYSQL_USER', os.environ.get('LAB4_MYSQL_USER', 'vladimirk'))
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', os.environ.get('LAB4_MYSQL_PASSWORD', None))
MYSQL_HOST = os.environ.get('MYSQL_HOST', os.environ.get('LAB4_MYSQL_HOST', 'vladimirk.mysql.pythonanywhere-services.com'))
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', os.environ.get('LAB4_MYSQL_DATABASE', 'vladimirk$default'))

# Local fallback examples (commented out):
# MYSQL_USER = 'root'
# MYSQL_PASSWORD = '123'
# MYSQL_HOST = 'localhost'
# MYSQL_DATABASE = 'lab4'