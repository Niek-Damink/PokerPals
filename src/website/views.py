from flask import Blueprint, render_template, request
from flask_login import login_user, login_required, logout_user, current_user
from .dbQueries import *

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user = current_user, user_list = getUserAndImage(), post_list = getPosts(), event_list = getEvents())

@views.route('/account')
@login_required
def account():
    x, y = getXYforPerson(current_user.name)
    return render_template("account.html", user = current_user, account = get_account_information(current_user.name),  session_list = getSessionsForPerson(current_user.name), x_list = x, y_list = y)

@views.route('/account/<name>')
@login_required
def accountID(name):
    x, y = getXYforPerson(name)
    return render_template("account.html", user = current_user, account = get_account_information(name), session_list = getSessionsForPerson(name), x_list = x, y_list = y)

@views.route('/sessions', methods=['GET', 'POST'])
@login_required
def sessions():
    if request.method == "POST":
        filterOn = request.form.get("filter")
        filterValue = request.form.get("inputValue")
        orderOn = request.form.get("order")
    else:
        filterOn = "0"
        filterValue = None
        orderOn = "0"
    return render_template("sessions.html", user = current_user, session_list = getSessionsWithPeopleAndPot(filterOn, filterValue, orderOn), total_statistics = getTotalStatistics(filterOn, filterValue))

@views.route('/sessions/<id>')
@login_required
def sessionOverview(id):
    session_information, enters = getSessionInformation(id)
    return render_template("sessionOverview.html", user = current_user, session_information = session_information, enters = enters)


@views.route('/leaderboard')
@login_required
def leaderboard():
    return render_template("leaderboard.html", user = current_user, leaderboard = getLeaderboard())


