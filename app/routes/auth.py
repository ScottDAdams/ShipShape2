# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app.models.user import User, Role
from app.database import db
from functools import wraps

bp = Blueprint('auth', __name__)
login_manager = LoginManager()


def init_app(app):
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        # Compare the provided password directly with the stored one
        if user and user.password == password and user.active:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('views.dashboard'))

        flash('Invalid email or password', 'error')

    return render_template('login.html')



@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# Admin routes for user management
@bp.route('/admin/users')
@login_required
@admin_required
def user_list():
    users = User.query.all()
    roles = Role.query.all()
    return render_template('auth/user_list.html', users=users, roles=roles)


@bp.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def user_add():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        role_id = request.form.get('role_id')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
        else:
            user = User(email=email, name=name, role_id=role_id)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('User added successfully', 'success')
            return redirect(url_for('auth.user_list'))

    roles = Role.query.all()
    return render_template('auth/user_form.html', roles=roles)


@bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.email = request.form.get('email')
        user.name = request.form.get('name')
        user.role_id = request.form.get('role_id')

        if request.form.get('password'):
            user.set_password(request.form.get('password'))

        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('auth.user_list'))

    roles = Role.query.all()
    return render_template('auth/user_form.html', user=user, roles=roles)


@bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin() and User.query.filter_by(role_id=user.role_id).count() == 1:
        flash('Cannot delete the last admin user', 'error')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    return redirect(url_for('auth.user_list'))