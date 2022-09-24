# Rider's WebApp

A Flask web application for managing cycling team rides and users, built with:
- HTML
- CSS
- Javascript
- JQuery
- Bootstrap
- Flask
- SQLAlchemy
- MariaDB


### Getting Started

- Install the requirements:
```
$ pip install -r requirements.txt
```

- Insatll and configure your database system of choice, the app is configured to use **MariaDB** By default.


- Create a database user, login with your user then create the database, for MariaDB/MySQL:
```
CREATE DATABASE riders;
```
You can change riders to any other name.

- Edit `flaskr/config.py` file.

- Generate a secret key token for flask session by opening Python shell and running the following commands:
```
>>> import secrets
>>> secrets.token_hex()
```
Then copy the generated hex.

- Create `flaskr/credentials.py` file in `flaskr` adding the following variables:
```
# Database Credentials
db_username = "root"  # or the username you have set
db_password = "password"

# Flask session secret key
secret_key = ""  # paste the generated hex into the string

# Admin app user password
admin_password = "password"
```

OR set credentials as environment variables:
```
$ export SECRET_KEY=  # paste the generated hex
$ export DATABASE_URL=  # your database URL
$ export ADMIN_PASSWORD=  # your admin user password
```

- Run the database module to create the database tables, make sure that your database server is running:
```
$ cd flaskr/modules/
$ python database.py
```

- Run main.py for development or testing or deploy the application.


## Deployment

Will be added soon


## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE) - see the [LICENSE](LICENSE) file for details
