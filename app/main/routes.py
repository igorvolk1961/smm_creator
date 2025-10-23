from flask import render_template, redirect, url_for
from flask_login import current_user
from app.main import bp

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@bp.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('main/dashboard.html', user=current_user)
