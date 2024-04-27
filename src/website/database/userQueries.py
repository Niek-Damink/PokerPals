from .models import User, User_Session, Session
from .. import db
from werkzeug.security import generate_password_hash
from os.path import join, dirname, realpath
import os

def getUserAndImage():
    users = User.query.all()
    user_list = []
    for user in users:
        if user.name != "Admin":
            session_amount = User_Session.query.filter(User_Session.person_name == user.name).count()
            user_list.append([user.name, user.imgURL, session_amount])
            user_list.sort(key=lambda x: x[2], reverse=True)
    return user_list

def deleteUserName(name):
    User.query.filter(User.name == name).delete(synchronize_session=False)
    db.session.commit()

def editUser(oldName, newName):
    User.query.filter(User.name == oldName).update({User.name: newName}, synchronize_session=False)
    User_Session.query.filter(User_Session.person_name == oldName).update({User_Session.person_name: newName}, synchronize_session=False)
    db.session.commit()

def editPicture(name, file):
    this_user = getUser(name)
    fileName = "avatar" + str(this_user.id) + "." + file.filename.rsplit('.', 1)[1]
    UPLOADS_PATH = join(dirname(realpath(__file__)), os.pardir ,'static/pictures/', fileName)
    file.save(UPLOADS_PATH)
    User.query.filter(User.name == name).update({User.imgURL: 'pictures/' + fileName}, synchronize_session=False)
    db.session.commit()

def addUser(name, password):
    new_user= User(name = name, password = generate_password_hash(password), imgURL = "/pictures/account.png")
    db.session.add(new_user)
    db.session.commit()

def getUser(name):
    user = User.query.filter_by(name=name).first()
    return user

def get_account_information(name):
    user = User.query.filter(User.name == name).first()
    user_sessions = User_Session.query.filter(User_Session.person_name == name)
    profit = 0
    total_beginstack = 0
    total_endstack = 0
    total_added_chips = 0
    total_played_hours = 0
    session_amount = user_sessions.count()
    total_host = 0
    for user_session in user_sessions:
        profit += user_session.end_stack - user_session.begin_stack - user_session.added_chips
        total_beginstack += user_session.begin_stack
        total_endstack += user_session.end_stack
        total_added_chips += user_session.added_chips
        session = Session.query.filter(Session.session_ID == user_session.session_ID).first()
        total_played_hours += session.duration
        if session.host == name:
            total_host += 1
    account_dict = {}
    account_dict["name"] = name
    account_dict["imgURL"] = user.imgURL
    account_dict["profit"] = round(profit, 2)
    account_dict["session_amount"] = session_amount
    account_dict["total_beginstack"] = total_beginstack
    account_dict["total_endstack"] = total_endstack
    account_dict["total_added_chips"] = total_added_chips
    account_dict["total_hours"] = total_played_hours
    account_dict["host_amount"] = total_host
    if session_amount == 0:
        session_amount = 1
        total_played_hours = 1
    account_dict["average_beginstack"] = round(total_beginstack / session_amount,2)
    account_dict["average_added_chips"] = round(total_added_chips / session_amount,2)
    account_dict["average_endstack"] = round(total_endstack / session_amount,2)
    account_dict["average_profit"] = round(profit/ session_amount,2)
    account_dict["profit_hour"] = round(profit/total_played_hours, 2)
    return account_dict