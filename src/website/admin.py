from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .dbQueries import *
from os.path import join, dirname, realpath
import os

admin = Blueprint('admin', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg'}

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
    if name == editName:
        pass
    elif user:
        flash("This username is already in use", category="error")
    elif len(editName) < 1:
        editName = name
    else:
        User.query.filter(User.name == name).update({User.name: editName}, synchronize_session=False)
        db.session.commit()

    file = request.files['file']
    print(file.filename)
    if(allowed_file(file.filename)):
        thisUser = User.query.filter_by(name=name).first()
        fileName = "avatar" + str(thisUser.id) + "." + file.filename.rsplit('.', 1)[1]
        UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/pictures/' + fileName)
        file.save(UPLOADS_PATH)
        User.query.filter(User.name == name).update({User.imgURL: 'pictures/' + fileName}, synchronize_session=False)
        db.session.commit()
    else:
        flash("File is not allowed, allowed formats are png and jpg", "error")
    return redirect(url_for('admin.adminUsers'))



@admin.route('/sessions', methods=['GET', 'POST'])
@login_required
def adminSessions():
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    return render_template("admin/adminSessions.html", user = current_user)

@admin.route('/post-events', methods=['GET', 'POST'])
@login_required
def adminPostEvents():
    if current_user.name != "Admin":
        return redirect(url_for('auth.login'))
    return render_template("admin/adminPostEvents.html", user = current_user)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS