from .models import Session, User_Session
from .. import db
from sqlalchemy import func, cast, Integer

def deleteSession(id):
    User_Session.query.filter(User_Session.session_ID == id).delete(synchronize_session=False)
    Session.query.filter(Session.session_ID == id).delete(synchronize_session=False)
    db.session.commit()
    return

def getMaxSessionID():
    max_session = Session.query.order_by(Session.session_ID.desc()).first()
    if max_session == None:
        max_session_id = 1
    else:
        max_session_id = max_session.session_ID + 1
    return max_session_id

def getSessionAmountForUser(name):
    amount = User_Session.query.filter(User_Session.person_name == name).count()
    return amount

def getSessionsWithPeopleAndPot(filter, value, order):
    if filter == "1" and value != "":
        sessions = Session.query.filter(Session.host == value).order_by(func.substr(Session.date, 7, 10).desc(), func.substr(Session.date, 4, 5).desc(), func.substr(Session.date, 1, 2).desc()).all()
    elif filter == "2" and value != "":
        theFilter = "___" + value + "_____"
        sessions = Session.query.filter(Session.date.like(theFilter)).order_by(func.substr(Session.date, 7, 10).desc(), func.substr(Session.date, 4, 5).desc(), func.substr(Session.date, 1, 2).desc()).all()
    elif filter == "3" and value != "":
        theFilter = "______" + value
        sessions = Session.query.filter(Session.date.like(theFilter)).order_by(func.substr(Session.date, 7, 10).desc(), func.substr(Session.date, 4, 5).desc(), func.substr(Session.date, 1, 2).desc()).all()
    else:
        sessions = Session.query.order_by(func.substr(Session.date, 7, 10).desc(), func.substr(Session.date, 4, 5).desc(), func.substr(Session.date, 1, 2).desc()).all()
    for session in sessions:
        total = 0
        userSessions = User_Session.query.filter(User_Session.session_ID == session.session_ID)
        players = userSessions.count()
        for userSession in userSessions:
            total += userSession.end_stack
        session.players = players
        session.pot = total
    for i, session in enumerate(sessions):
        session.number = len(sessions) - i
    if order == "0":
        pass
    elif order == "1":
        sessions.sort(key=lambda x: x.duration, reverse=True)
    elif order == "2":
        sessions.sort(key=lambda x: x.pot, reverse=True)
    else:
        sessions.sort(key=lambda x: x.players, reverse=True)
    return sessions

def updateSession(id, host, date, duration, small_blind, big_blind, is_straddle, is_seven_deuce):
    Session.query.filter(Session.session_ID == id).update({Session.host:host, Session.session_ID:id, Session.date:date, Session.duration:duration, Session.small_blind: small_blind, Session.big_blind: big_blind, Session.straddle: is_straddle, Session.seven_deuce: is_seven_deuce}, synchronize_session=False)
    db.session.commit()

def getTotalStatistics(filter, value):
    if filter == "1" and value != "":
        sessions = Session.query.filter(Session.host == value).all()
    elif filter == "2" and value != "":
        theFilter = "___" + value + "_____"
        sessions = Session.query.filter(Session.date.like(theFilter)).all()
    elif filter == "3" and value != "":
        theFilter = "______" + value
        sessions = Session.query.filter(Session.date.like(theFilter)).all()
    else:
        sessions = Session.query.all()
    total_statistics_dict = {}
    session_count = len(sessions)
    total_statistics_dict["Sessions"] = session_count
    if session_count != 0:
        total_in = 0
        total_added = 0
        for session in sessions:
            userSessions = User_Session.query.filter(User_Session.session_ID == session.session_ID)
            for userSession in userSessions:
                total_in += userSession.begin_stack
                total_added += userSession.added_chips
        total_statistics_dict["Total buyins"] = total_in
        total_statistics_dict["Average buyin"] = round(total_in/session_count,2)
        total_statistics_dict["Total added chips"] = total_added
        total_statistics_dict["Average added chips"] = round(total_added/session_count,2)
        total_statistics_dict["Total chips"] = total_added + total_in
        total_statistics_dict["Average chips"] = round((total_added + total_in)/session_count,2)
    else:
        total_statistics_dict["Total buyins"] = 0
        total_statistics_dict["Average buyin"] = 0
        total_statistics_dict["Total added chips"] = 0
        total_statistics_dict["Average added chips"] = 0
        total_statistics_dict["Total chips"] = 0
        total_statistics_dict["Average chips"] = 0
    return total_statistics_dict

def addSession(host, date, duration, small_blind, big_blind, is_straddle, is_seven_deuce, person_session):
    session_ID = getMaxSessionID()
    new_session = Session(host=host, session_ID = session_ID, date=date, duration = duration, small_blind = small_blind, big_blind = big_blind, straddle = is_straddle, seven_deuce = is_seven_deuce)
    db.session.add(new_session)
    for person in person_session:
        new_person_session = User_Session(session_ID = session_ID, begin_stack = person[1], added_chips = person[2], end_stack = person[3], person_name = person[0])
        db.session.add(new_person_session)
    db.session.commit()
 
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

def getSingleSession(id):
    session = Session.query.filter(Session.session_ID == id).first()
    total = 0
    userSessions = User_Session.query.filter(User_Session.session_ID == session.session_ID)
    players = userSessions.count()
    for userSession in userSessions:
            total += userSession.end_stack
    session.players = players
    session.pot = total
    all_sessions = Session.query.order_by(func.substr(Session.date, 7, 10).desc(), func.substr(Session.date, 4, 5).desc(), func.substr(Session.date, 1, 2).desc()).all()
    sessionNum = {}
    for i, the_session in enumerate(all_sessions):
        sessionNum[the_session.session_ID] = len(all_sessions)-i
    session.number = sessionNum[session.session_ID]
    return session

def getSessionsForPerson(name):
    all_sessions = User_Session.query.filter(User_Session.person_name == name).order_by(User_Session.session_ID.desc()).all()
    all_all_sessions = Session.query.order_by(cast(func.substr(Session.date, 7, 10),Integer).desc(), cast(func.substr(Session.date, 4, 5),Integer).desc(), cast(func.substr(Session.date, 1, 2),Integer).desc()).all()
    sessionDict = {}
    for i, session in enumerate(all_all_sessions):
        sessionDict[session.session_ID] = len(all_all_sessions) - i
    for session in all_sessions:
        session.date = Session.query.filter(Session.session_ID == session.session_ID).first().date
        session.number = sessionDict[session.session_ID]

    return all_sessions

def getXYforPerson(name):
    all_sessions = User_Session.query.filter(User_Session.person_name == name).order_by(User_Session.session_ID.asc()).all()
    x = []
    y = []
    total = 0
    for session in all_sessions:
        x.append(session.session_ID)
        total += round(session.end_stack - session.begin_stack - session.added_chips, 2)
        y.append(total)
    return x, y
