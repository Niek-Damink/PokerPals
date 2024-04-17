from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    text = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())

class Session(db.Model):
    sessionID = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True))
    duration = db.Column(db.Integer)
    straddle = db.Column(db.Boolean)
    seven_Deuce = db.Column(db.Boolean)
    small_blind = db.Column(db.Float)
    big_blind = db.Column(db.Float)
    usersessions = db.relationship('Usersession')

class Usersession(db.Model):
    noneID = db.Column(db.Integer, primary_key=True)
    sessionID = db.Column(db.Integer, db.ForeignKey('session.sessionID'))
    personID = db.Column(db.Integer, db.ForeignKey('user.id'))
    beginStack = db.Column(db.Float)
    addedChips = db.Column(db.Float)
    endStack = db.Column(db.Float)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    sessions = db.relationship('Usersession')
