from .models import User
from . import db

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
    