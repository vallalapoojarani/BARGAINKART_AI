from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home_dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        # Match by email (case-insensitive) OR roll number OR name
        id_lower = identifier.lower()
        user = User.query.filter(
            (User.email.ilike(id_lower)) |
            (User.roll_number.ilike(identifier)) |
            (User.name.ilike(f"%{identifier}%"))
        ).first()

        # If not found directly, also handle guide/short name mappings
        if not user:
            clean_id = id_lower.replace('smt.', '').replace('dr.', '').replace(' ', '').replace('.', '')
            all_users = User.query.all()
            for u in all_users:
                u_clean = u.name.lower().replace('smt.', '').replace('dr.', '').replace(' ', '').replace('.', '')
                u_roll = (u.roll_number or '').lower().replace('smt.', '').replace('dr.', '').replace(' ', '').replace('.', '')
                if clean_id and (clean_id in u_clean or u_clean in clean_id or clean_id in u_roll or u_roll in clean_id or ('vaishnavi' in clean_id and 'vaishnavi' in u_clean)):
                    user = u
                    break

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.name} ({user.designation or 'Member'})!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.home_dashboard'))
        else:
            flash("Invalid email, roll number, or password. Please verify your credentials.", "danger")

    return render_template('login.html')


@auth_bp.route('/quick-login/<identifier>')
def quick_login(identifier):
    """Direct one-click sign in for Academic Evaluation & Presentation."""
    user = User.query.filter(
        (User.email.ilike(identifier)) |
        (User.roll_number.ilike(identifier)) |
        (User.name.ilike(f"%{identifier}%"))
    ).first()
    if not user:
        clean_id = identifier.lower().replace('smt.', '').replace(' ', '').replace('.', '')
        for u in User.query.all():
            u_clean = u.name.lower().replace('smt.', '').replace(' ', '').replace('.', '')
            u_roll = (u.roll_number or '').lower().replace('smt.', '').replace(' ', '').replace('.', '')
            if clean_id and (clean_id in u_clean or u_clean in clean_id or clean_id in u_roll or u_roll in clean_id or ('vaishnavi' in clean_id and 'vaishnavi' in u_clean)):
                user = u
                break
    if user:
        login_user(user)
        flash(f"Signed in as {user.name} ({user.designation}) for Academic Demonstration.", "success")
        return redirect(url_for('dashboard.home_dashboard'))
    flash("Account not found.", "warning")
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip() or '+91 98765 43210'
        address = request.form.get('address', '').strip() or 'Bengaluru, Karnataka'

        if not name or not email or not password:
            flash("Please fill in all required fields.", "warning")
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists. Please log in.", "danger")
            return redirect(url_for('auth.login'))

        new_user = User(
            name=name,
            email=email,
            role='user',
            phone=phone,
            address=address
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Registration successful! Welcome to BARGAINKART.", "success")
        return redirect(url_for('dashboard.home_dashboard'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been securely logged out.", "info")
    return redirect(url_for('products.landing'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            # Simulated OTP flow for academic demonstration
            flash("Password reset instructions and verification token sent to your registered email.", "success")
        else:
            flash("Email address not found in system. Please verify or register.", "warning")
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name).strip()
        current_user.phone = request.form.get('phone', current_user.phone).strip()
        current_user.address = request.form.get('address', current_user.address).strip()
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('auth.profile'))

    return render_template('profile.html', user=current_user)


# API endpoints
@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        login_user(user)
        return jsonify({'success': True, 'user': user.to_dict(), 'redirect': url_for('dashboard.home_dashboard')})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already registered'}), 400

    new_user = User(
        name=data.get('name', 'User'),
        email=email,
        phone=data.get('phone', '+91 98765 43210'),
        address=data.get('address', 'Bengaluru, India')
    )
    new_user.set_password(data.get('password', 'Demo@123'))
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return jsonify({'success': True, 'user': new_user.to_dict()})
