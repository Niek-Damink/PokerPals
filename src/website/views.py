from flask import Blueprint, render_template, request
from flask_login import login_user, login_required, logout_user, current_user
from .dbQueries import *

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user = current_user, user_list = getUserAndImage())

@views.route('/account')
@login_required
def account():
    return render_template("account.html", user = current_user)

@views.route('/sessions', methods=['GET', 'POST'])
@login_required
def sessions():
    if request.method == "POST":
        filterOn = request.form.get("filter")
        filterValue = request.form.get("inputValue")
        orderOn = request.form.get("order")
    return render_template("sessions.html", user = current_user, session_list = getSessionsWithPeopleAndPot(filterOn, filterValue, orderOn), total_statistics = getTotalStatistics())

@views.route('/sessions/<id>')
@login_required
def sessionOverview(id):
    session_information, enters = getSessionInformation(id)
    return render_template("sessionOverview.html", user = current_user, session_information = session_information, enters = enters)


@views.route('/leaderboard')
@login_required
def leaderboard():
    return render_template("leaderboard.html", user = current_user)


