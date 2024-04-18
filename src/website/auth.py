from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    logout_user()
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        user = User.query.filter_by(name=name).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
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

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
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
            new_user = User(name = name, password = generate_password_hash(password1), imgURL = "/pictures/pim.jpg")
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))
    
    return render_template("sign_up.html", user = current_user) 
