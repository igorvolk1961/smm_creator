#!/usr/bin/env python3
"""
Скрипт для принудительной инициализации базы данных на сервере
"""

import os
import sys
from pathlib import Path

def init_database():
    """Принудительно создать базу данных"""
    
    # Добавляем текущую директорию в путь
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        from app import create_app, db
        from app.models import User
        
        print("🚀 Инициализация базы данных на сервере...")
        print(f"📁 Рабочая директория: {os.getcwd()}")
        
        app = create_app()
        
        with app.app_context():
            # Удаляем старый файл базы данных если он пустой
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                print(f"📊 Текущий размер файла: {size} байт")
                
                if size == 0:
                    print("🗑️ Удаляем пустой файл базы данных...")
                    os.remove(db_path)
            
            # Создаем папку instance если её нет
            instance_dir = Path('instance')
            if not instance_dir.exists():
                instance_dir.mkdir()
                print("📁 Создана папка instance")
            
            # Принудительно создаем все таблицы
            print("🔨 Создание таблиц...")
            db.create_all()
            
            # Проверяем результат
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Созданные таблицы: {tables}")
            
            # Проверяем размер файла
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                print(f"📊 Новый размер файла: {size} байт")
                
                if size > 0:
                    print("🎉 База данных успешно создана!")
                else:
                    print("⚠️ Файл базы данных все еще пустой")
            else:
                print("❌ Файл базы данных не создан")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    init_database()
