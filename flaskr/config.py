import os
import credentials

# Database Variables
HOST = "localhost"
PORT = 3306
DB_FILE = "riders"
# DATABASE_URI = f"mariadb+pymysql://{credentials.db_username}:{credentials.db_password}@{HOST}:{PORT}/{DB_FILE}?charset=utf8mb4"  # will be created in datadir of mariadb, in my case /var/lib/mysql
DATABASE_URI = os.environ["DATABASE_URL"]

# Regex
REGEX = {
        "username": r"^[A-Za-z0-9]+$",
        "phone": r"^01\d{9}",
        "email": r"^[^\.\s\n\\][^\n\s\\]*@[^\.\s\n\\]+\.[^\.\s\n\\]+",
        "password": r"^.{8,52}$",
        "speed": r"^\d{2}$",
        "distance": r"^\d{1,3}$",
        "arabic" : r"[\u0600-\u06FF\s]+"
        }
