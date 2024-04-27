from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .database import userQueries, eventQueries, postQueries, sessionQueries
from os.path import join, dirname, realpath
import os
import datetime

admin = Blueprint('admin', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg'}
do_reset = False

@admin.route('/users', methods=['GET', 'POST', 'DELETE'])
@login_required
def adminUsers():
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = userQueries.getUser(name)
        if user:
            flash('name already exists', category='error')
        elif len(name) < 1:
            flash('Pleas fill in a name', category='error')
        elif len(password1) < 5:
            flash('Password needs to be 5 characters', category='error')
        elif password1 != password2:
            flash('Passwords are not the same', category='error')
        else:
            userQueries.addUser(name, password1)
            flash('Succesfully created account for ' + name, category='success')
            return redirect(url_for('admin.adminUsers'))
    return render_template("admin/adminUsers.html", user = current_user, user_list = userQueries.getUserAndImage()) 


@admin.route('/users/delete/<name>', methods=['DELETE'])
@login_required
def deleteUser(name):
    if current_user.name != "Admin":
        return "Fail"
    user = userQueries.getUser(name)
    path = user.imgURL
    sessions = sessionQueries.getSessionAmountForUser(user.name)
    if sessions == 0:
        userQueries.deleteUserName(name)
        if path != "/pictures/account.png":
            UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/' + path)
            os.remove(UPLOADS_PATH)
            return "Success"
    else:
        flash("You cannot delete users who have participated in sessions!", "error")
        return "Fail"
    

@admin.route('/users/edit/<name>', methods=['POST'])
@login_required
def editUser(name):
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    editName = request.form.get('editName')
    user = userQueries.getUser(editName)
    if name == editName or len(editName) < 1:
        pass
    elif user:
        flash("This username is already in use", category="error")
    else:
        userQueries.editUser(name, editName)
    file = request.files['file']
    if(allowed_file(file.filename)):
        userQueries.editPicture(editName, file)
    elif len(file.filename) > 0:
        flash("File is not allowed, allowed formats are png and jpg", "error")
    return redirect(url_for('admin.adminUsers'))

@admin.route('/sessions', methods=['GET', 'POST'])
@login_required
def adminSessions():
    if request.method == "POST":
        filterOn = request.form.get("filter")
        filterValue = request.form.get("inputValue")
        orderOn = request.form.get("order")
    else:
        filterOn = "0"
        filterValue = None
        orderOn = "0"
    return render_template("admin/adminSessionOverview.html", user = current_user, session_list = sessionQueries.getSessionsWithPeopleAndPot(filterOn, filterValue, orderOn))

@admin.route('/sessions/editSession/<id>', methods=['POST'])
@login_required
def adminEditSession(id):
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    host = request.form.get('host')
    date = request.form.get('date'); date_split = date.split("/")
    duration = request.form.get('duration'); duration_split = duration.split(".")
    small_blind = request.form.get('smallblind'); small_blind_split = small_blind.split(".")
    big_blind = request.form.get('bigblind'); big_blind_split = big_blind.split(".")
    is_straddle = request.form.get('straddle') != None
    is_seven_deuce = request.form.get('sevendeuce') != None
    if not userQueries.getUser(host):
        flash("the host '" + host +"' does not exist", "error")
        return redirect(url_for('admin.adminSessions'))
    elif len(date_split) != 3 or not date_split[0].isdigit() or not date_split[1].isdigit() or not date_split[2].isdigit() or len(date_split[0]) != 2 or len(date_split[1]) != 2 or len(date_split[2]) != 4:
        flash("Please fill in a correct date (DD/MM/YYYY)", "error")
        return redirect(url_for('admin.adminSessions'))
    elif len(duration_split) > 2 or not duration_split[0].isdigit() or (len(duration_split) == 2 and not duration_split[1].isdigit()):
        flash("Please fill in a correct duration", "error")
        return redirect(url_for('admin.adminSessions'))
    elif len(small_blind_split) > 2 or not small_blind_split[0].isdigit() or (len(small_blind_split) == 2 and not small_blind_split[1].isdigit()):
        flash("Please fill in a correct small blind", "error")
        return redirect(url_for('admin.adminSessions'))
    elif len(big_blind_split) > 2 or not big_blind[0].isdigit() or (len(big_blind_split) == 2 and not big_blind_split[1].isdigit()):
        flash("Please fill in a correct big blind", "error")
        return redirect(url_for('admin.adminSessions'))
    sessionQueries.updateSession(id, host, date, duration , small_blind, big_blind, is_straddle, is_seven_deuce)
    flash("Succesfully edited session " + id, "success")
    return redirect(url_for('admin.adminSessions'))
    

@admin.route('/sessions/delete/<id>', methods=['DELETE'])
@login_required
def adminDeleteSession(id):
    if current_user.name != "Admin":
        return "Fail"
    flash("Successfully deleted session", "success")
    sessionQueries.deleteSession(id)
    return redirect(url_for("admin.adminSessions"))


@admin.route('/sessions/add_session', methods=['GET', 'POST'])
@login_required
def adminAddSessions():
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    global do_reset
    if do_reset:
        do_reset = False
        reset = True
    else:
        reset = False
    return render_template("admin/adminSessions.html", user = current_user, do_reset = reset)

@admin.route('/sessions/addSession/<amount>', methods=['POST'])
@login_required
def adminAddSession(amount):
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    host = request.form.get('host')
    date = request.form.get('date'); date_split = date.split("/")
    duration = request.form.get('duration'); duration_split = duration.split(".")
    small_blind = request.form.get('smallblind'); small_blind_split = small_blind.split(".")
    big_blind = request.form.get('bigblind'); big_blind_split = big_blind.split(".")
    is_straddle = request.form.get('straddle') != None
    is_seven_deuce = request.form.get('sevendeuce') != None
    if not userQueries.getUser(host):
        flash("the host '" + host +"' does not exist", "error")
        return redirect(url_for('admin.adminAddSessions'))
    elif len(date_split) != 3 or not date_split[0].isdigit() or not date_split[1].isdigit() or not date_split[2].isdigit() or len(date_split[0]) != 2 or len(date_split[1]) != 2 or len(date_split[2]) != 4:
        flash("Please fill in a correct date (DD/MM/YYYY)", "error")
        return redirect(url_for('admin.adminAddSessions'))
    elif len(duration_split) > 2 or not duration_split[0].isdigit() or (len(duration_split) == 2 and not duration_split[1].isdigit()):
        flash("Please fill in a correct duration", "error")
        return redirect(url_for('admin.adminAddSessions'))
    elif len(small_blind_split) > 2 or not small_blind_split[0].isdigit() or (len(small_blind_split) == 2 and not small_blind_split[1].isdigit()):
        flash("Please fill in a correct small blind", "error")
        return redirect(url_for('admin.adminAddSessions'))
    elif len(big_blind_split) > 2 or not big_blind_split[0].isdigit() or (len(big_blind_split) == 2 and not big_blind_split[1].isdigit()):
        flash("Please fill in a correct big blind", "error")
        return redirect(url_for('admin.adminAddSessions'))
    person_session = [];used_names = []; total_in = 0; total_out = 0
    for id in range(1, int(amount) + 1):
        id = str(id)
        name = request.form.get('name' + id)
        begin_stack = request.form.get('begin' + id)
        added_stack = request.form.get('added' + id)
        end_stack = request.form.get('end' + id)
        if (not userQueries.getUser(name)):
            flash("the name '" + name +"' does not exist", "error")
        elif (name in used_names):
            flash("the name '" + name +"' has been used twice", "error")
        elif (not (("." in begin_stack and begin_stack.split(".", 1)[0].isdigit() and begin_stack.split(".", 1)[1].isdigit()) or begin_stack.isdigit())):
            flash("the field 'Begin stack' for "+ name +" is not a positive number", "error")
        elif (not (("." in added_stack and added_stack.split(".", 1)[0].isdigit() and added_stack.split(".", 1)[1].isdigit()) or added_stack.isdigit())):
            flash("the field 'Added chips' for "+ name +" is not a positive number", "error")
        elif (not (("." in end_stack and end_stack.split(".", 1)[0].isdigit() and end_stack.split(".", 1)[1].isdigit()) or end_stack.isdigit())):
            flash("the field 'End stack' for "+ name +" is not a positive number", "error")
        else:
            person_session.append((name, begin_stack, added_stack, end_stack))
            used_names.append(name)
            total_in += float(begin_stack) + float(added_stack)
            total_out += float(end_stack)
            continue
        return redirect(url_for('admin.adminAddSessions'))
    if (total_in != total_out):
        flash("The total amount of money going in and out is not equal", "error")
        return redirect(url_for('admin.adminAddSessions'))
    global do_reset; do_reset = True
    sessionQueries.addSession(host, date, duration, small_blind, big_blind, is_straddle, is_seven_deuce, person_session)
    flash("Succesfully added the new session", "success")
    return redirect(url_for('admin.adminSessions'))
    

@admin.route('/post-events', methods=['GET'])
@login_required
def adminPostEvents():
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    return render_template("admin/adminPostEventsOverview.html", user = current_user, post_list = postQueries.getPosts(), event_list = eventQueries.getEventsAdmin())

@admin.route('/post-events/delete-post/<id>', methods=['DELETE'])
@login_required
def adminPostEventsDeletePost(id):
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    flash("Successfully deleted post", "success")
    postQueries.deletePost(id)
    return redirect(url_for("admin.adminAddPostEvents"))

@admin.route('/post-events/delete-event/<id>', methods=['DELETE'])
@login_required
def adminPostEventsDeleteEvent(id):
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    flash("Successfully deleted event", "success")
    eventQueries.deleteEvent(id)
    return redirect(url_for("admin.adminAddPostEvents"))


@admin.route('/post-events/add', methods=['GET'])
@login_required
def adminAddPostEvents():
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    return render_template("admin/adminPostEvents.html", user = current_user)

@admin.route('/post-events/add-post', methods=['POST'])
@login_required
def adminAddPost():
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    file = request.files['file']
    title = request.form.get('title')
    text = request.form.get('text')
    if len(title) == 0:
        flash("Please enter a title", "error")
        return redirect(url_for("admin.adminAddPostEvents"))
    elif len(text) == 0:
        flash("Pleas enter some text", "error")
        return redirect(url_for("admin.adminAddPostEvents"))
    date = datetime.datetime.today().strftime('%d/%m/%Y')
    print(date)
    id = postQueries.getMaxPostID()
    if(allowed_file(file.filename)):
        postQueries.addPostWithPicture(id, title, text, date, file)
        flash("Succesfully created post with picture")
    elif len(file.filename) > 0:
        flash("File is not allowed, allowed formats are png and jpg", "error")  
        return redirect(url_for("admin.adminAddPostEvents"))
    else:
        postQueries.addPost(id, title, text, date)
        flash("Succesfully created post")  
    return redirect(url_for("admin.adminPostEvents"))

@admin.route('/post-events/edit-event/<id>', methods=['POST'])
@login_required
def adminEditEvent(id):
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    name = request.form.get("event_name")
    date = request.form.get("date"); date_split = date.split("/")
    if len(name) == 0:
        flash("Please enter a name", "error")
        return redirect(url_for("admin.adminPostEvents"))
    elif len(date_split) != 3 or not date_split[0].isdigit() or not date_split[1].isdigit() or not date_split[2].isdigit() or len(date_split[0]) != 2 or len(date_split[1]) != 2 or len(date_split[2]) != 4:
        flash("Please fill in a correct date (DD/MM/YYYY)", "error")
        return redirect(url_for("admin.adminPostEvents"))
    eventQueries.updateEvent(id, name, date)
    return redirect(url_for("admin.adminPostEvents"))

@admin.route('/post-events/edit-post/<id>', methods=['POST'])
@login_required
def adminEditPost(id):
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    file = request.files['file']
    title = request.form.get('title')
    text = request.form.get('text')
    date =  request.form.get("datePost"); date_split = date.split("/")
    if len(title) == 0:
        flash("Please enter a title", "error")
        return redirect(url_for("admin.adminPostEvents"))
    elif len(text) == 0:
        flash("Please enter some text", "error")
        return redirect(url_for("admin.adminPostEvents"))
    elif len(date_split) != 3 or not date_split[0].isdigit() or not date_split[1].isdigit() or not date_split[2].isdigit() or len(date_split[0]) != 2 or len(date_split[1]) != 2 or len(date_split[2]) != 4:
        flash("Please fill in a correct date (DD/MM/YYYY)", "error")
        return redirect(url_for("admin.adminPostEvents"))
    if(allowed_file(file.filename)):
        postQueries.updatePostWithPicture(id, title, date, text, file)
        flash("Succesfully edited post with picture")
    elif len(file.filename) > 0:
        flash("File is not allowed, allowed formats are png and jpg", "error")  
        return redirect(url_for("admin.adminPostEvents"))
    else:
        postQueries.updatePost(id, title, date, text)
        flash("Succesfully edited post")  
    return redirect(url_for("admin.adminPostEvents"))
    

@admin.route('/post-events/add-event', methods=['POST'])
@login_required
def adminAddEvent():
    event_name = request.form.get('event_name')
    date = request.form.get('date')
    date = date; date_split = date.split("/")
    if len(event_name) == 0:
        flash("Pleas fill in a name for the event", "error")
        return redirect(url_for('admin.adminPostEvents'))
    elif len(date_split) != 3 or not date_split[0].isdigit() or not date_split[1].isdigit() or not date_split[2].isdigit() or len(date_split[0]) != 2 or len(date_split[1]) != 2 or len(date_split[2]) != 4:
        flash("Please fill in a correct date (DD/MM/YYYY)", "error")
        return redirect(url_for('admin.adminPostEvents'))
    eventQueries.addEvent(date, event_name)
    flash("Successfully added new Event")
    return redirect(url_for('admin.adminPostEvents'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS