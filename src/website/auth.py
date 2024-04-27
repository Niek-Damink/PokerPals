from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .database import userQueries


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    logout_user()
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        user = userQueries.getUser(name)
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                if user.name == "Admin":
                    return redirect(url_for('admin.adminUsers'))
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect login information, try again', category='error')
        else:
            flash('Incorrect login information, try again', category='error')
        
    return render_template("login.html", user=current_user) 

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login')) 