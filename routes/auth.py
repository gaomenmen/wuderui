from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import login_manager, db
from models.admin_user import AdminUser

auth_bp = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.must_change_password:
                flash('Please change your default password before continuing.', 'warning')
                return redirect(url_for('auth.change_password'))
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('auth/login.html')


@auth_bp.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        if not current_user.check_password(old_password):
            flash('Current password is incorrect.', 'error')
        elif len(new_password) < 8:
            flash('New password must be at least 8 characters.', 'error')
        elif new_password != confirm:
            flash('Passwords do not match.', 'error')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('admin.dashboard'))
    return render_template('auth/change_password.html')


@auth_bp.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
