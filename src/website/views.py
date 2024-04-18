from flask import Blueprint, render_template
from flask_login import login_user, login_required, logout_user, current_user
from .models import User

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append([user.name, user.imgURL])
    return render_template("home.html", user = current_user, user_list = user_list)

@views.route('/account')
@login_required
def account():
    return render_template("account.html", user = current_user)

@views.route('/sessions')
@login_required
def sessions():
    return render_template("sessions.html", user = current_user)

@views.route('/leaderboard')
@login_required
def leaderboard():
    return render_template("leaderboard.html", user = current_user)


