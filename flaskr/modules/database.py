import time
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """User Base Class"""
    __tablename__ = "users"

    id =  db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    arabic_username = db.Column(db.String(255), nullable=False)
    hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    phone = db.Column(db.String(13), unique=True, nullable=False)
    rides = db.Column(db.Integer, default=0)
    created_datetime = db.Column(db.BIGINT, default=time.time())
    is_admin = db.Column(db.Boolean, default=False)

    created_rides = db.relationship("Ride", back_populates="creator")
    leaded_rides = db.relationship("Lead", back_populates="leader")
    participations = db.relationship("Participation", order_by="Participation.ride_id", back_populates="user")

    def __repr__(self) -> str:
        """
        String representation of the object
        """
        return super().__repr__()[:-1] + f" id={self.id} username={self.username} phone={self.phone} admin={self.is_admin}>"


class Ride(db.Model):
    """Ride Base Class"""
    __tablename__ = "rides"

    id =  db.Column(db.Integer, primary_key=True, autoincrement=True)
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ride_notes = db.Column(db.String(255))
    assembly_datetime = db.Column(db.BIGINT, nullable=False)
    moving_datetime = db.Column(db.BIGINT, nullable=False)
    course = db.Column(db.String(255), nullable=False)
    distance = db.Column(db.Integer, nullable=False)
    max_speed = db.Column(db.Integer, nullable=False)
    min_speed = db.Column(db.Integer, nullable=False)
    ride_type = db.Column(db.String(255))
    edited = db.Column(db.Boolean, default=False)

    creator = db.relationship("User", back_populates="created_rides")
    lead = db.relationship("Lead", back_populates="ride")
    participants = db.relationship("Participation", back_populates="ride")

    def __repr__(self) -> str:
        """
        String representation of the object
        """
        return super().__repr__()[:-1] + f" id={self.id}>"


class Participation(db.Model):
    """Participations Base Class"""
    __tablename__ = "participations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey("rides.id"), nullable=False)

    user = db.relationship("User", back_populates="participations")
    ride = db.relationship("Ride", back_populates="participants")

    unique_index = db.Index("participations_unique_index", user_id, ride_id, unique=True)  # Creating unique index to avoid row duplication


class Lead(db.Model):
    """Ride Leaders 'Association' Base Class"""
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    leader_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey("rides.id"), nullable=False, unique=True)

    leader = db.relationship("User", back_populates="leaded_rides")
    ride = db.relationship("Ride", back_populates="lead")

    unique_index = db.Index("leads_unique_index", leader_id, ride_id, unique=True)


if __name__ == "__main__":
    """
    Before running execute the following command in MySQL/MariaDB shell:
        CREATE DATABASE riders;
        # or your database name
    """
    from app import app
    with app.app_context():
        db.create_all()  # Should be run once to create the table once
