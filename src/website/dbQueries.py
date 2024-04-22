from .models import User, Session
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
    max_session = Session.query.order_by(Session.session_ID.desc()).first().session_ID + 1
    if (max_session == None):
        max_session = 1
    print(max_session)
    return max_session

    