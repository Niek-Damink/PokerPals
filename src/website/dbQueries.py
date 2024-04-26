from .models import User, Session, User_Session, Post, Events
from . import db
from sqlalchemy import func, cast, Integer
import datetime

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
    return

def deleteSession(id):
    User_Session.query.filter(User_Session.session_ID == id).delete(synchronize_session=False)
    Session.query.filter(Session.session_ID == id).delete(synchronize_session=False)
    db.session.commit()
    return
    
def deletePost(id):
    Post.query.filter(Post.id == id).delete(synchronize_session=False)
    db.session.commit()
    return

def deleteEvent(id):
    Events.query.filter(Events.id == id).delete(synchronize_session=False)
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

def getLeaderboard():
    leaderboard = []
    users = User.query.all()
    i = 0
    for user in users:
        username = user.name
        user_sessions = User_Session.query.filter(User_Session.person_name == username)
        session_amount = user_sessions.count()
        if(session_amount < 3):
            continue
        total_session_result = 0
        total_hours = 0
        for session in user_sessions:
            total_session_result += session.end_stack - session.begin_stack - session.added_chips
            total_hours += Session.query.filter(Session.session_ID == session.session_ID).first().duration
        average_session_result = round(total_session_result / session_amount, 2)
        average_hour_result = round(total_session_result/ total_hours, 2)
        leaderboard.append([i, username, average_session_result, average_hour_result, session_amount, total_session_result])
    leaderboard.sort(key=lambda x: x[5], reverse=True)
    for person in leaderboard:
        i += 1
        person[0] = i
    return leaderboard

def getLeaderboardPerYear(year):
    leaderboard = []
    users = User.query.all()
    i = 0
    for user in users:
        username = user.name
        theFilter = "______" + year
        user_sessions = User_Session.query.filter(User_Session.person_name == username, User_Session.session_ID == Session.session_ID, Session.date.like(theFilter))
        session_amount = user_sessions.count()
        if(session_amount < 3):
            continue
        total_session_result = 0
        total_hours = 0
        for session in user_sessions:
            theSession = Session.query.filter(Session.session_ID == session.session_ID).first()
            total_session_result += session.end_stack - session.begin_stack - session.added_chips
            total_hours += theSession.duration
        average_session_result = round(total_session_result / session_amount, 2)
        average_hour_result = round(total_session_result/ total_hours, 2)
        leaderboard.append([i, username, average_session_result, average_hour_result, session_amount, total_session_result])
    leaderboard.sort(key=lambda x: x[5], reverse=True)
    for person in leaderboard:
        i += 1
        person[0] = i
    return leaderboard

def getAllDates():
    distinct_years = db.session.query(func.substr(Session.date, -4)).distinct().all()
    return distinct_years

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

def getMaxPostID():
    max_post = Post.query.order_by(Post.id.desc()).first()
    if max_post == None:
        max_session_id = 1
    else:
        max_session_id = max_post.id + 1
    return max_session_id

def getPosts():
    all_posts = Post.query.order_by(Post.id.desc()).all()
    return all_posts

def getEventsAdmin():
    all_events = Events.query.all()
    return all_events
   
def getEvents():
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')
    day = datetime.datetime.today().strftime('%d')
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(days=1)
    today = today.strftime('%d/%m/%Y')
    tomorrow = tomorrow.strftime('%d/%m/%Y')
    all_events = Events.query.filter((cast(func.substr(Events.date, 7, 10),Integer) > year) |
                                      ((cast(func.substr(Events.date, 4, 5), Integer) > month) & (cast(func.substr(Events.date, 7, 10) == year, Integer))) | 
                                      ((cast(func.substr(Events.date, 1, 2), Integer) >= day) & (cast(func.substr(Events.date, 4, 5), Integer) == month) & (cast(func.substr(Events.date, 7, 10), Integer) == year))).order_by(cast(func.substr(Events.date, 7, 10),Integer).asc(), cast(func.substr(Events.date, 4, 5),Integer).asc(), cast(func.substr(Events.date, 1, 2),Integer).asc()).all()
    for event in all_events:
        if event.date == today:
            event.date = "Today"
        elif event.date == tomorrow:
            event.date = "Tomorrow"
    return all_events

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
