from .models import User

def getUserAndImage():
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append([user.name, user.imgURL])
    return user_list
    