from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User, Session, User_Session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .dbQueries import *
from os.path import join, dirname, realpath
import os

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

        user = User.query.filter_by(name=name).first()
        if user:
            flash('name already exists', category='error')
        elif len(name) < 1:
            flash('Pleas fill in a name', category='error')
        elif len(password1) < 5:
            flash('Password needs to be 5 characters', category='error')
        elif password1 != password2:
            flash('Passwords are not the same', category='error')
        else:
            new_user = User(name = name, password = generate_password_hash(password1), imgURL = "/pictures/account.png")
            db.session.add(new_user)
            db.session.commit()
            flash('Succesfully created account for ' + name, category='success')
            return redirect(url_for('admin.adminUsers'))
    return render_template("admin/adminUsers.html", user = current_user, user_list = getUserAndImage()) 


@admin.route('/users/delete/<name>', methods=['DELETE'])
@login_required
def deleteUser(name):
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(name=name).first()
    path = user.imgURL
    deleteUserName(name)
    if path != "/pictures/account.png":
        UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/' + path)
        os.remove(UPLOADS_PATH)
    return redirect(url_for('admin.adminUsers'))

@admin.route('/users/edit/<name>', methods=['POST'])
@login_required
def editUser(name):
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    editName = request.form.get('editName')
    user = User.query.filter_by(name=editName).first()
    if name == editName or len(editName) < 1:
        pass
    elif user:
        flash("This username is already in use", category="error")
    else:
        User.query.filter(User.name == name).update({User.name: editName}, synchronize_session=False)
        db.session.commit()

    file = request.files['file']
    if(allowed_file(file.filename)):
        this_user = User.query.filter_by(name=editName).first()
        fileName = "avatar" + str(this_user.id) + "." + file.filename.rsplit('.', 1)[1]
        UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/pictures/' + fileName)
        file.save(UPLOADS_PATH)
        User.query.filter(User.name == name).update({User.imgURL: 'pictures/' + fileName}, synchronize_session=False)
        db.session.commit()
    elif len(file.filename) > 0:
        flash("File is not allowed, allowed formats are png and jpg", "error")
    return redirect(url_for('admin.adminUsers'))



@admin.route('/sessions', methods=['GET', 'POST'])
@login_required
def adminSessions():
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
    the_date = request.form.get('date'); date = the_date.split("-")
    the_duration = request.form.get('duration'); duration = the_duration.split(".")
    the_small_blind = request.form.get('smallblind'); small_blind = the_small_blind.split(".")
    the_big_blind = request.form.get('bigblind'); big_blind = the_big_blind.split(".")
    is_straddle = request.form.get('straddle') != None
    is_seven_deuce = request.form.get('sevendeuce') != None
    if not User.query.filter_by(name=host).first():
        flash("the host '" + host +"' does not exist", "error")
        return redirect(url_for('admin.adminSessions'))
    elif len(date) != 3 or not date[0].isdigit() or not date[1].isdigit() or not date[2].isdigit() or len(date[0]) != 2 or len(date[1]) != 2 or len(date[2]) != 4:
        flash("Please fill in a correct date (DD-MM-YYYY)", "error")
        return redirect(url_for('admin.adminSessions'))
    elif len(duration) > 2 or not duration[0].isdigit() or (len(duration) == 2 and not duration[1].isdigit()):
        flash("Please fill in a correct duration", "error")
        return redirect(url_for('admin.adminSessions'))
    elif len(small_blind) > 2 or not small_blind[0].isdigit() or (len(small_blind) == 2 and not small_blind[1].isdigit()):
        flash("Please fill in a correct small blind", "error")
        return redirect(url_for('admin.adminSessions'))
    elif len(big_blind) > 2 or not big_blind[0].isdigit() or (len(big_blind) == 2 and not big_blind[1].isdigit()):
        flash("Please fill in a correct big blind", "error")
        return redirect(url_for('admin.adminSessions'))
    person_session = []
    used_names = []
    for id in range(1, int(amount) + 1):
        id = str(id)
        name = request.form.get('name' + id)
        begin_stack = request.form.get('begin' + id)
        added_stack = request.form.get('added' + id)
        end_stack = request.form.get('end' + id)
        if (not User.query.filter_by(name=name).first()):
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
            continue
        return redirect(url_for('admin.adminSessions'))
    global do_reset; do_reset = True
    session_ID = getMaxSessionID()
    new_session = Session(session_ID = session_ID, date=the_date, duration = the_duration, small_blind = the_small_blind, big_blind = the_big_blind, straddle = is_straddle, seven_deuce = is_seven_deuce)
    db.session.add(new_session)
    for person in person_session:
        new_person_session = User_Session(session_ID = session_ID, begin_stack = person[1], added_chips = person[2], end_stack = person[3], person_name = person[0])
        db.session.add(new_person_session)
    db.session.commit()
    flash("Succesfully added the new session", "success")
    return redirect(url_for('admin.adminSessions'))
    

@admin.route('/post-events', methods=['GET', 'POST'])
@login_required
def adminPostEvents():
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    return render_template("admin/adminPostEvents.html", user = current_user)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS