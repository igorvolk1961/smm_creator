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
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static',
                static_url_path='/static')
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    # Определяем путь к базе данных в зависимости от окружения
    import os
    if os.path.exists('instance'):
        # Если папка instance существует, используем её
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/smm_app.db'
    else:
        # Иначе создаем в корне проекта
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
    
    # Инициализируем генераторы и базу данных при запуске
    with app.app_context():
        # Импортируем модели ПЕРЕД созданием таблиц
        from app.models import User
        
        # Создаем базу данных и таблицы, если их нет
        try:
            print(f"🗄️ Путь к базе данных: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print(f"📁 Текущая директория: {os.getcwd()}")
            
            db.create_all()
            print("✅ База данных инициализирована")
            
            # Проверяем что таблицы созданы
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Созданные таблицы: {tables}")
            
            # Проверяем размер файла базы данных
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                print(f"📊 Размер файла базы данных: {size} байт")
            else:
                print(f"⚠️ Файл базы данных не найден: {db_path}")
            
        except Exception as e:
            print(f"⚠️ Ошибка инициализации базы данных: {e}")
            import traceback
            traceback.print_exc()
        
        from generators.text_gen import TextGenerator
        from generators.image_gen import ImageGenerator
        
        config = app.config['API_CONFIG']
        
        # Создаем генераторы один раз
        app.text_generator = TextGenerator(
            api_key=config['api_keys']['deepseek'],
            base_url=config['api_urls']['deepseek']
        )
        
        app.image_generator = ImageGenerator(
            config=config.get('image_generation', {
                'provider': 'webui',
                'webui': {'base_url': 'http://localhost:7860'}
            })
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
