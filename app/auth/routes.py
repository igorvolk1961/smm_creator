from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.auth import bp

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'error': 'Пользователь с таким именем уже существует'})
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'Пользователь с таким email уже существует'})
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('main.dashboard')})
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return jsonify({'success': True, 'redirect': url_for('main.dashboard')})
        else:
            return jsonify({'success': False, 'error': 'Неверное имя пользователя или пароль'})
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
