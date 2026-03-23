"""Authentication routes."""
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.extensions import db, bcrypt, limiter
from app.models import User


@auth_bp.route("/register", methods=['GET', 'POST'])
@limiter.limit("6 per hour")
def register():
    """User registration with password validation."""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # PASSWORD VALIDATION
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/register.html')
        
        if not any(char.isdigit() for char in password):
            flash('Password must contain at least one number.', 'danger')
            return render_template('auth/register.html')
        
        if not any(char.isupper() for char in password):
            flash('Password must contain at least one uppercase letter.', 'danger')
            return render_template('auth/register.html')
        
        if not any(char.islower() for char in password):
            flash('Password must contain at least one lowercase letter.', 'danger')
            return render_template('auth/register.html')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('auth.register'))
        
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already taken. Please choose another.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'Account created for {username}! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@auth_bp.route("/login", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if user and bcrypt.check_password_hash(user.password, password):
            # Log the user in
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to the page they were trying to access, or home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')


@auth_bp.route("/logout")
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.home'))