"""
Cycling rides web app
"""
import os
import time
import datetime
import re

from flask import Flask, flash, redirect, render_template, request, session, jsonify, g, abort
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

from modules.database import db, User, Ride, Lead, Participation
from modules.helpers import login_required, route_format
from modules.regex import REGEX

try:  # just for my local tests
    from credentials import secret_key
    from config import DATABASE_URI
    SECRET_KEY = secret_key
    DATABASE_URL = DATABASE_URI
except ModuleNotFoundError:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DATABASE_URL = os.environ["DATABASE_URL"]


"""Global Variables"""
WEEKDAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

"""App init and config"""
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configuring session
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_PERMANENT"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # will emit a warning: https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/?highlight=sqlalchemy_track_modifications

# app.config["SESSION_SQLALCHEMY"] = db  # unnecessary and might cause an error
Session(app)
db.init_app(app)

# Adding custom filters
app.jinja_env.filters["route_format"] = route_format


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.errorhandler(400)
def bad_request(e):
    return render_template("errors/400.html", msg=e.description), 400


@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html", msg=e.description), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500


@app.route("/")
@login_required
def index():
    """ Index page """
    # Get current month epoch
    today = datetime.datetime.today()
    month = today.strftime("%B")
    month_epoch = datetime.datetime(today.year, today.month, 1)

    # Queries
    participations = Participation.query.filter_by(user_id=session["user_id"]).all()
    rides_ids = [p.ride_id for p in participations]
    rides_query = Ride.query.filter(Ride.id.in_(rides_ids)).filter(Ride.assembly_datetime <= int(time.time()))
    total_rides = rides_query.all()
    total_distance = sum([r.distance for r in total_rides])
    month_rides = rides_query.filter(Ride.assembly_datetime >= month_epoch).all()
    month_distance = sum([r.distance for r in month_rides])

    stats = {
            "month": month,
            "month_rides": len(month_rides),
            "total_rides": len(total_rides),
            "month_distance": month_distance,
            "total_distance": total_distance
            }

    return render_template("index.html", stats=stats)


@app.route("/register", methods=["POST", "GET"])
def register():
    """ Register a new user """
    if request.method == "POST":
        # Get use input
        username = request.form.get("username")
        phone = request.form.get("phone")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        accepted = request.form.get("accept")

        # Check username
        username_re = re.compile(REGEX["username"])
        if not username_re.fullmatch(username):
            return abort(400, "Invalid Username")
        elif len(User.query.filter_by(username=username).all()) > 0:
            return abort(400, "Username already exists")

        # Check phone number
        phone_re = re.compile(REGEX["phone"])
        if not phone_re.fullmatch(phone):
            return abort(400, "Invalid phone number format")

        # Check email
        email_re = re.compile(REGEX["email"])
        if not email_re.fullmatch(email):
            return abort(400, "Invalid email format")

        # Check password
        password_re = re.compile(REGEX["password"])
        if not password_re.fullmatch(password):
            return abort(400, "Invalid password, try again.")
        elif password != confirmation:
            return abort(400, "Password Mismatch")

        # Check rules accepted
        if not accepted:
            return abort(400, "You must read and accept the group rules")

        # Register user
        user = User(
                    username=username,
                    arabic_username=request.form.get("arabic"),
                    hash=generate_password_hash(password),
                    email=email,
                    phone="+2" + phone,  # country code prefix
                    created_datetime=time.time()
                    )
        db.session.add(user)
        db.session.commit()

        # Login user
        session["user"] = user
        session["user_id"] = user.id
        g.user = user

        # Redirect to index
        flash("Registered Successfully", "success")
        return redirect("/")

    else:
        return render_template("auth/register.html", regex=REGEX)


@app.route("/match-username")
def user_exists():
    """ AJAX: request to check for duplicates in username """
    input_user = request.args.get("input_username")
    return jsonify({"found": (len(User.query.filter_by(username=input_user).all()) > 0)})


@app.route("/match-email")
def email_exists():
    """ AJAX: request to check for duplicates in Email """
    input_user = request.args.get("input_email")
    return jsonify({"found": (len(User.query.filter_by(email=input_user).all()) > 0)})


@app.route("/match-phone")
def phone_exists():
    """ AJAX: request to check for duplicates in Phone Number """
    input_user = request.args.get("input_phone")
    input_user = "+2" + input_user
    return jsonify({"found": (len(User.query.filter_by(phone=input_user).all()) > 0)})


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Login route """
    if request.method == "POST":
        # Check username
        user = User.query.filter_by(username=request.form.get("username")).first()
        if not user:
            flash("Username doesn't exist", "danger")
            return redirect("/login")

        # Check password
        if not check_password_hash(user.hash, request.form.get("password")):
            flash("Incorrect password", "danger")
            return redirect("/login")

        # Login user
        session["user"] = user
        session["user_id"] = user.id
        g.user = user

        # Redirect to index
        flash("Logged in", "success")
        return redirect("/")

    else:
        return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():
    """ Logout user """
    session.clear()
    g.user = None
    flash("Logged out", "info")
    return redirect("/login")


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """ Create Ride Route"""
    if request.method == "POST":
        # Check rules accepted
        if not request.form.get("accept"):
            return abort(400, "You must read and accept the group rules")

        # Format route segments
        route_list = request.form.getlist("route[]")
        if len(route_list) == 0:
            return abort(400, "Route list is empty")
        route = "|".join(route_list)

        # Convert ride times to unix epochs
        (year, month, day) = [int(v) for v in request.form.get("date").split('-')]
        (assembly_h, assembly_m) = [int(v) for v in request.form.get("assembly_time").split(':')]
        (moving_h, moving_m) = [int(v) for v in request.form.get("moving_time").split(':')]
        assembly_time = datetime.datetime(year, month, day, assembly_h, assembly_m).timetuple()
        moving_time = datetime.datetime(year, month, day, moving_h, moving_m).timetuple()
        assembly_time = int(time.mktime(assembly_time))
        moving_time = int(time.mktime(moving_time))

        # Add the new ride
        ride = Ride(
                    creator_id=session["user_id"],
                    assembly_datetime=assembly_time,
                    moving_datetime=moving_time,
                    course=route,
                    distance=request.form.get("distance"),
                    max_speed=request.form.get("max-speed"),
                    min_speed=request.form.get("min-speed"),
                    ride_type=request.form.get("ride-type"),
                    ride_notes=request.form.get("ride-header")
                    )
        db.session.add(ride)
        db.session.commit()

        # Add new lead
        lead = Lead(
                leader_id=session["user_id"],
                ride_id=ride.id
                )
        db.session.add(lead)
        db.session.commit()

        # Add participation
        participation = Participation(
                user_id=session["user_id"],
                ride_id=ride.id
                )
        db.session.add(participation)
        db.session.commit()

        # Redirect
        flash("Ride created", "success")
        return redirect("/")

    else:
        today = datetime.timedelta(days=1) + datetime.date.today()
        return render_template("create_ride.html", today=today, regex=REGEX)


@app.route("/rides")
@login_required
def rides():
    """ Join Ride Route"""
    # Get upcoming rides
    time_now = time.time()
    ride_objs = Ride.query.filter(Ride.assembly_datetime >= time_now).order_by(Ride.assembly_datetime).all()

    # Get user participations in rides
    rides_ids = [ride.id for ride in ride_objs]
    participations = Participation.query.filter(Participation.user_id == session["user_id"] and Participation.ride_id in rides_ids).all()

    # Arrange rides data into dictionaries
    rides = []
    for obj in ride_objs:
        # Format date and time from epochs
        assembly_datetime = datetime.datetime.fromtimestamp(obj.assembly_datetime)
        moving_datetime = datetime.datetime.fromtimestamp(obj.moving_datetime)

        # Get leader and participants
        leader = obj.lead[0].leader  # every ride has one leader only
        participations = obj.participants
        participants = [o.user.arabic_username for o in participations]
        participants.remove(leader.arabic_username)

        rides.append({
                "id": obj.id,
                "notes": obj.ride_notes,
                "type": obj.ride_type,
                "weekday": WEEKDAYS_EN[assembly_datetime.weekday()],  # won't use strftime for arabic support later
                "date": assembly_datetime.strftime("%d/%m/%Y"),
                "assembly_time": assembly_datetime.strftime("%I:%M %p"),
                "moving_time": moving_datetime.strftime("%I:%M %p"),
                "route": obj.course,
                "distance": obj.distance,
                "max_speed": obj.max_speed,
                "min_speed": obj.min_speed,
                "leader": leader,
                "leading": session["user_id"] == leader.id,
                "participants": participants,
                "joined": session["user_id"] in [o.user.id for o in participations]
                })

    return render_template("rides.html", rides=rides)


@app.route("/rides/join", methods=["POST"])
@login_required
def join_ride():
    """AJAX: join ride request"""
    ride_id = request.form.get("ride_id")

    # Add the user to participants
    p = Participation(
            user_id=session["user_id"],
            ride_id=ride_id
            )
    db.session.add(p)
    db.session.commit()

    # Return resopnse
    return jsonify({"participant": session["user"].arabic_username})


@app.route("/rides/leave", methods=["POST"])
@login_required
def leave_ride():
    """AJAX: leave ride request"""
    ride_id = request.form.get("ride_id")
    response = {"participant": session["user"].arabic_username, "new_lead": False}

    # Queries
    ride = Ride.query.filter_by(id=ride_id).first()
    participation = Participation.query.filter_by(user_id=session["user_id"], ride_id=ride_id).first()
    lead = Lead.query.filter_by(leader_id=session["user_id"], ride_id=ride_id).first()

    # Delete participation
    db.session.delete(participation)
    db.session.commit()

    # Delete lead if any
    if lead:
        response["new_lead"] = True

        # Delete old lead
        db.session.delete(lead)
        db.session.commit()

        if len(ride.participants) > 0:
            # Add new lead
            lead = Lead(
                    leader_id=ride.participants[0].user_id,
                    ride_id=ride_id
                    )
            db.session.add(lead)
            db.session.commit()

            # Add leader name to response
            response["leader"] = lead.leader.arabic_username

        else:
            # if no other participants send an empty string
            response["leader"] = ""

    # Return user arabic name
    return jsonify(response)


@app.route("/rides/cancel", methods=["POST"])
@login_required
def cancel_ride():
    """AJAX: cancel ride request"""
    ride_id = request.form.get("ride_id")

    # Queries
    ride = Ride.query.filter_by(id=ride_id).first()
    lead = Lead.query.filter_by(ride_id=ride_id).first()
    participations = Participation.query.filter_by(ride_id=ride_id).all()

    # Validations
    if session["user_id"] != lead.leader_id or not session["user"].is_admin:
        abort(403, "Must be the ride leader or an admin in order to cancel the ride.")

    # Delete all
    if lead:
        db.session.delete(lead)
        db.session.commit()
    if participations:
        if len(participations) > 0:
            for p in participations:
                db.session.delete(p)
                db.session.commit()
    db.session.delete(ride)
    db.session.commit()

    # Return empty resopnse
    return {}


@app.route("/history")
@login_required
def history():
    """ History route """
    # Get participations
    participations = Participation.query.filter_by(user_id=session["user_id"]).all()
    rides_ids = [p.ride_id for p in participations]

    # Get rides
    time_now = int(time.time())
    rides = Ride.query.filter(Ride.id.in_(rides_ids)).filter(Ride.assembly_datetime < time_now).order_by(Ride.assembly_datetime.desc()).all()

    # Arrange rides data into dictionaries
    rides_data = []
    for ride in rides:
        # Format date and time from epochs
        assembly_datetime = datetime.datetime.fromtimestamp(ride.assembly_datetime)
        moving_datetime = datetime.datetime.fromtimestamp(ride.moving_datetime)

        # Get leader and participants
        leader = ride.lead[0].leader  # every ride has one leader only
        participations = ride.participants
        participants = [o.user.arabic_username for o in participations]
        participants.remove(leader.arabic_username)

        rides_data.append({
                "id": ride.id,
                "notes": ride.ride_notes,
                "type": ride.ride_type,
                "weekday": WEEKDAYS_EN[assembly_datetime.weekday()],  # won't use strftime for arabic support later
                "date": assembly_datetime.strftime("%d/%m/%Y"),
                "assembly_time": assembly_datetime.strftime("%I:%M %p"),
                "moving_time": moving_datetime.strftime("%I:%M %p"),
                "route": ride.course,
                "distance": ride.distance,
                "max_speed": ride.max_speed,
                "min_speed": ride.min_speed,
                "leader": leader,
                "participants": participants
                })

    return render_template("history.html", rides=rides_data)

