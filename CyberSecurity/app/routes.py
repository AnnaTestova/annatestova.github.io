from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from . import db, login_manager
from .models import User, Credential
from .forms import RegisterForm, LoginForm, CredentialForm
from .crypto_utils import generate_key, encrypt_password, decrypt_password
from .forms import LogoutForm
import bcrypt

app = Blueprint('main', __name__) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('main.login')) 

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    print("Register route accessed")
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists. Try another.")
            return redirect(url_for('main.register'))

        hashed_pw = bcrypt.hashpw(form.password.data.encode(), bcrypt.gensalt())
        key = generate_key()  
        new_user = User(username=form.username.data, password_hash=hashed_pw, key=key)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created. Please log in.")
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.checkpw(form.password.data.encode(), user.password_hash):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash("Invalid username or password.")
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    creds = Credential.query.filter_by(user_id=current_user.id).all()
    logout_form = LogoutForm()
    return render_template('dashboard.html', credentials=creds, logout_form=logout_form)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = CredentialForm()
    if form.validate_on_submit():
        encrypted_pw = encrypt_password(form.password.data, current_user.key)

        cred = Credential(
            site=form.site.data,
            login=form.username.data,
            password_encrypted=encrypted_pw,
            user_id=current_user.id
        )
        db.session.add(cred)
        db.session.commit()
        flash("Credential saved.")
        return redirect(url_for('main.dashboard'))
    return render_template('add_password.html', form=form)

