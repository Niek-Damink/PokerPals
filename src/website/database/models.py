from .. import db 
from flask_login import UserMixin
from sqlalchemy.sql import func

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    text = db.Column(db.String(10000))
    imgURL = db.Column(db.String(10000))
    date = db.Column(db.String(100))

class Session(db.Model):
    session_ID = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(100))
    date = db.Column(db.String(100))
    duration = db.Column(db.Integer)
    straddle = db.Column(db.Boolean)
    seven_deuce = db.Column(db.Boolean)
    small_blind = db.Column(db.Float)
    big_blind = db.Column(db.Float)

class User_Session(db.Model):
    noneID = db.Column(db.Integer, primary_key=True)
    session_ID = db.Column(db.Integer, db.ForeignKey('session.session_ID'))
    person_name = db.Column(db.String(150), db.ForeignKey('user.name'))
    begin_stack = db.Column(db.Float)
    added_chips = db.Column(db.Float)
    end_stack = db.Column(db.Float)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    imgURL = db.Column(db.String(10000))

class Events(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    date = db.Column(db.String(150))


