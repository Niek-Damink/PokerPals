from .models import User, Session, User_Session
from . import db
from sqlalchemy import func

def getUserAndImage():
    users = User.query.all()
    user_list = []
    for user in users:
        if user.name != "Admin":
            user_list.append([user.name, user.imgURL])
    return user_list
    
def deleteUserName(name):
    User.query.filter(User.name == name).delete(synchronize_session=False)
    db.session.commit()
    return

def getMaxSessionID():
    max_session = Session.query.order_by(Session.session_ID.desc()).first()
    if max_session == None:
        max_session_id = 1
    else:
        max_session_id = max_session.session_ID + 1
    return max_session_id

def getSessionsWithPeopleAndPot(filter, value, order):
    if filter == "1" and value != "":
        sessions = Session.query.filter(Session.host == value).all()
    elif filter == "2" and value != "":
        theFilter = "%" + value + "%"
        sessions = Session.query.filter(Session.date.like(theFilter)).all()
    elif filter == "3" and value != "":
        theFilter = "%" + value
        sessions = Session.query.filter(Session.date.like(theFilter)).all()
    else:
        sessions = Session.query.all()
    for session in sessions:
        total = 0
        userSessions = User_Session.query.filter(User_Session.session_ID == session.session_ID)
        players = userSessions.count()
        for userSession in userSessions:
            total += userSession.end_stack
        session.players = players
        session.pot = total
    if order == "0":
        sessions.sort(key=lambda x: x.session_ID, reverse=True)
    elif order == "1":
        sessions.sort(key=lambda x: x.duration, reverse=True)
    elif order == "2":
        sessions.sort(key=lambda x: x.pot, reverse=True)
    else:
        sessions.sort(key=lambda x: x.players, reverse=True)
    return sessions

def getTotalStatistics():
    sessions = Session.query.all()
    total_statistics_dict = {}
    session_count = len(sessions)
    total_statistics_dict["Sessions"] = session_count

    total_in = 0
    total_added = 0
    for session in sessions:
        userSessions = User_Session.query.filter(User_Session.session_ID == session.session_ID)
        for userSession in userSessions:
            total_in += userSession.begin_stack
            total_added += userSession.added_chips
    total_statistics_dict["Total in"] = total_in
    total_statistics_dict["Average in"] = round(total_in/session_count,2)
    total_statistics_dict["Total added"] = total_added
    total_statistics_dict["Average added"] = round(total_added/session_count,2)
    return total_statistics_dict
    
def getSessionInformation(id):
    user_sessions = User_Session.query.filter(User_Session.session_ID == id)
    enters = {}
    i = 0
    for user in user_sessions:
        if i%2 == 0 and i != 0:
            enters[user.person_name] = True
        else:
            enters[user.person_name] = False
        i += 1
    return user_sessions, enters