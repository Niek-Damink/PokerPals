from .models import User, User_Session, Session
from .. import db
from sqlalchemy import func

#returns a list of lists containing attributes for a leaderboard
#does this for all the users that have played a minimum of three sessions
#of form: [[i, username, average_session_result, average_hour_result, session_amount, total_session_result]]
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


#returns a list of lists containing attributes for a leaderboard
#does this for all the users that have played a minimum of three sessions in the specified year
#of form: [[i, username, average_session_result, average_hour_result, session_amount, total_session_result]]
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

#returns all the distinct years where sessions have been played
def getAllDates():
    distinct_years = db.session.query(func.substr(Session.date, -4)).distinct().all()
    return distinct_years