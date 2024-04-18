from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .dbQueries import *

admin = Blueprint('admin', __name__)

@admin.route('/users', methods=['GET', 'POST', 'DELETE'])
@login_required
def adminUsers():
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
    deleteUserName(name)
    return redirect(url_for('admin.adminUsers'))


@admin.route('/sessions', methods=['GET', 'POST'])
@login_required
def adminSessions():
    return render_template("admin/adminSessions.html", user = current_user)

@admin.route('/post-events', methods=['GET', 'POST'])
@login_required
def adminPostEvents():
    return render_template("admin/adminPostEvents.html", user = current_user)
