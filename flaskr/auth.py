import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

## Create blueprint for login, logout and register view functions.
bp = Blueprint('auth', __name__, url_prefix='/auth')

## Register view - To register new users.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    print('auth/register')
## user submits the html form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

## If there is no error, redirect the user to login page after adding the user to the database.
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

## if request is not POST, render the register template again.
    return render_template('auth/register.html')


##  Login view - Vaidate user data for Login
@bp.route('/login', methods=('GET', 'POST'))
def login():
    print('auth/login')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

## @bp.before_app_request registers a function that runs before the view
## function, no matter what URL is requested
@bp.before_app_request
def load_logged_in_user():
    print('auth/load_logged_in_user')
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

## Logout view- clears the session and log's out the user
## load_logged_in_user will not load any user.
@bp.route('/logout')
def logout():
    print('auth/logout')
    session.clear()
    return redirect(url_for('index'))

## decorator view .
## -- Need to understand this properly ----
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        print('auth/login_required')
        print(view)
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
