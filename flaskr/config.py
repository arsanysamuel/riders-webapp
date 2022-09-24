import credentials

# Database Variables
HOST = "localhost"
PORT = 3306
DB_FILE = "riders"
DATABASE_URI = f"mariadb+pymysql://{credentials.db_username}:{credentials.db_password}@{HOST}:{PORT}/{DB_FILE}?charset=utf8mb4"  # will be created in datadir of mariadb, in my case /var/lib/mysql

