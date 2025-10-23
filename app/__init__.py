from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import json
from pathlib import Path

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smm_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализация расширений
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
    login_manager.login_message_category = 'info'

    # Загружаем конфигурацию
    with open('config.json', 'r', encoding='utf-8') as f:
        app.config['API_CONFIG'] = json.load(f)
    
    # Инициализируем генераторы один раз при запуске
    with app.app_context():
        from generators.text_gen import TextGenerator
        from generators.image_gen import ImageGenerator
        
        config = app.config['API_CONFIG']
        
        # Создаем генераторы один раз
        app.text_generator = TextGenerator(
            api_key=config['api_keys']['deepseek'],
            base_url=config['api_urls']['deepseek']
        )
        
        app.image_generator = ImageGenerator(
            base_url=config['api_urls']['deepseek']
        )

    # Регистрируем блюпринты
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.smm import bp as smm_bp
    app.register_blueprint(smm_bp, url_prefix='/smm')

    # Настройка загрузчика пользователей
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
