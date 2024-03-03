from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db,mail
from flask_mail import Message
from flask_login import login_user, login_required, logout_user, current_user
import random
import string
import sqlite3
import time, datetime

login_allowance_time = 10 #in seconds
auth = Blueprint('auth', __name__)

conn = sqlite3.connect(
    "img_db", check_same_thread=False)

conn_user = sqlite3.connect(
    "./instance/database.db", check_same_thread=False)

#add about us page
@auth.route('/about')
def aboutus():
    return render_template('about.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        #session["eml"] = email
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            cursor_user = conn_user.cursor()
            slct_string = f"SELECT * FROM sessions WHERE email = '{email}'"
            cursor_user.execute(slct_string)
            row = cursor_user.fetchone()
            if row is not None:
                login_cond = (datetime.datetime.now() - datetime.datetime.strptime(row[2],"%Y-%m-%d %H:%M:%S.%f")).total_seconds() >= login_allowance_time
            else:
                login_cond = 1
            if check_password_hash(user.password, password) and login_cond: #check last logout of the user
                
                login_time = str(datetime.datetime.now())
                if row is not None:
                    cursor_user.execute(f"UPDATE sessions SET last_login = '{login_time}' WHERE email = '{email}'")
                    conn_user.commit()
                else:
                    cursor_user.execute(f"INSERT INTO sessions (email, last_login, last_logout, user) VALUES (?, ?, ?, ?)",(email, login_time, login_time, str(-1)))
                    conn_user.commit()
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                cursor_user.execute(f"UPDATE sessions SET user = '{current_user}' WHERE email = '{email}'")
                conn_user.commit()
                return redirect(url_for('views.home'))
            else:
                if not login_cond:
                    flash(f'Please wait for {login_allowance_time}s before logging in', category='error')
                else:
                    flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    # flash('Please wait for sometime before you login again', category='failure')
    cursor_user = conn_user.cursor()
    logout_time = str(datetime.datetime.now())
    cursor_user.execute(f"UPDATE sessions SET last_logout = '{logout_time}' WHERE user = '{current_user}'")
    conn_user.commit()
    logout_user()
    login_wait = 0
    time.sleep(login_wait)
    
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        age = request.form.get('age')
        gender = request.form.get('gender')
        rod = request.form.get('rod')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First _name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'), age=age, gender=gender, rod=rod)
            db.session.add(new_user)
            db.session.commit()
            # id = db.session.execute('SELECT ID FROM USER WHERE EMAIL = {}'.format(email))
            # cur = conn.cursor()
            # cur.execute("INSERT INTO data (id, email, password, name, age, gender, rod) VALUES (?, ?, ?, ?, ?,?, ?)",
            #     (id,email, generate_password_hash(password1), first_name,age, gender,rod))
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", user=current_user)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate a unique token for password reset
            reset_token = user.generate_reset_token()

            # Send an email with the reset link
            send_reset_email(user.email, reset_token)

            flash('Password reset link has been sent to your email.', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email not found. Please register.', category='error')

    return render_template('forgot_password.html', user=current_user)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_token(token)

    if user is None:
        flash('Invalid or expired token. Please request a new one.', category='error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password == confirm_password:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            user.reset_token = None
            user.reset_token_expires = None
            db.session.commit()

            flash('Your password has been reset successfully.', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('Passwords do not match. Please try again.', category='error')

    return render_template('reset_password.html', user=current_user)
def send_reset_email(email, reset_token):
    msg = Message('Password Reset', recipients=[email])
    reset_url = url_for('auth.reset_password', token=reset_token, _external=True)
    msg.body = f"Click the following link to reset your password: {reset_url}"
    mail.send(msg)

@auth.route('/thankyou')
def thankyou():
    user = conn_user.cursor()
    return render_template('thankyou.html', user=user)



   