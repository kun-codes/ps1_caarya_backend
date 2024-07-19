from random import random

from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterPlayerForm, LoginForm, RegisterEmployerForm, PlayerTypeForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user

import os
# from dotenv import load_dotenv

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/find-partners')
@login_required
def market_page():
    items = Item.query.all()
    return render_template('market.html', user_type=current_user.user_type,
                           valorant_username=current_user.valorant_username,
                           username=current_user.username,
                           )

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/register-player', methods=['GET', 'POST'])
def register_player():
    form = RegisterPlayerForm()
    if form.validate_on_submit():
        import random
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              valorant_username=form.valorant_username.data,
                              password=form.password1.data,
                              user_type='player',
                              role=random.choice(['Entry Fragger', 'Sniper', 'Support', 'Anchor', 'Lurker'])
                              )

        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register-player.html', form=form)

@app.route('/register-employer', methods=['GET', 'POST'])
def register_employer():
    form = RegisterEmployerForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              valorant_username=form.valorant_username.data,
                              password=form.password1.data,
                              user_type='employer',
                              role='Employer'
                              )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register-employer.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))


@app.route('/predict')
@login_required
def predict_page():
    return render_template('predict.html', role=current_user.role)

@app.route('/find-player', methods=['GET', 'POST'])
@login_required
def find_player_page():
    form = PlayerTypeForm()
    if form.validate_on_submit():
        # Process the form data, e.g., form.playerType.data
        selected_player_type = form.playerType.data
        return redirect(url_for('predicted_players_page', role=selected_player_type))

    return render_template('find-players.html', form=form)

@app.route('/predicted-players')
@login_required
def predicted_players_page():
    role = request.args.get('role')
    players = User.query.filter_by(role=role).all()
    return render_template('predicted-players.html', players=players, role=role)