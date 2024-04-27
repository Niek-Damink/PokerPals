from flask import Blueprint, render_template, request
from flask_login import login_user, login_required, logout_user, current_user
from .database import userQueries, eventQueries, postQueries, sessionQueries, leaderboardQueries

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user = current_user, user_list = userQueries.getUserAndImage(), post_list = postQueries.getPosts(), event_list = eventQueries.getEvents())

@views.route('/account')
@login_required
def account():
    x, y = sessionQueries.getXYforPerson(current_user.name)
    return render_template("account.html", user = current_user, account = userQueries.get_account_information(current_user.name),  session_list = sessionQueries.getSessionsForPerson(current_user.name), x_list = x, y_list = y)

@views.route('/account/<name>')
@login_required
def accountID(name):
    x, y = sessionQueries.getXYforPerson(name)
    return render_template("account.html", user = current_user, account = userQueries.get_account_information(name), session_list = sessionQueries.getSessionsForPerson(name), x_list = x, y_list = y)

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
    return render_template("sessions.html", user = current_user, session_list = sessionQueries.getSessionsWithPeopleAndPot(filterOn, filterValue, orderOn), total_statistics = sessionQueries.getTotalStatistics(filterOn, filterValue))

@views.route('/sessions/<id>')
@login_required
def sessionOverview(id):
    session_information = sessionQueries.getSessionInformation(id)
    return render_template("sessionOverview.html", user = current_user, session_information = session_information, session = sessionQueries.getSingleSession(id))


@views.route('/leaderboard', methods=['GET', 'POST'])
@login_required
def leaderboard():
    year = request.form.get("year")
    if request.method == "POST" and year != "all":
        leaderboard = leaderboardQueries.getLeaderboardPerYear(year)
        year = "Poker Pal's " + year + " Leaderboard!" 
    else:
        leaderboard = leaderboardQueries.getLeaderboard()
        year = "Poker Pal's All-Time Leaderboard!"
    return render_template("leaderboard.html", user = current_user, leaderboard = leaderboard, dates = leaderboardQueries.getAllDates(), year=year)


