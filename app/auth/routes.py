from flask import render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.auth import bp
import requests

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

# VK ID SDK маршруты

@bp.route('/vk/callback', methods=['POST'])
def vk_callback():
    """Обработка callback от VK ID SDK"""
    data = request.get_json()
    access_token = data.get('access_token')
    user_id = data.get('user_id')
    
    if not access_token or not user_id:
        return jsonify({'success': False, 'error': 'Не получен токен или ID пользователя'})
    
    try:
        # Получаем информацию о пользователе
        user_info_url = "https://api.vk.com/method/users.get"
        user_params = {
            'user_ids': user_id,
            'fields': 'screen_name,photo_50',
            'access_token': access_token,
            'v': '5.131'
        }
        
        user_response = requests.get(user_info_url, params=user_params)
        user_data = user_response.json()
        
        if 'error' in user_data:
            return jsonify({'success': False, 'error': 'Ошибка получения данных пользователя'})
        
        vk_user = user_data['response'][0]
        
        # Ищем или создаем пользователя
        user = User.query.filter_by(vk_api_id=str(user_id)).first()
        
        if not user:
            # Создаем нового пользователя
            username = vk_user.get('screen_name', f"vk_user_{user_id}")
            email = f"{username}@vk.local"  # Временный email
            
            user = User(
                username=username,
                email=email,
                vk_api_id=str(user_id)
            )
            user.set_password('vk_auth')  # Временный пароль
            db.session.add(user)
            db.session.commit()
        
        # Авторизуем пользователя
        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('main.dashboard')})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка авторизации: {str(e)}'})
