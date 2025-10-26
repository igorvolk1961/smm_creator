#!/usr/bin/env python3
"""
Скрипт для обновления файлов на сервере PythonAnywhere
Запускать на сервере для исправления дублирующих функций
"""

import os
import shutil
from pathlib import Path

def fix_routes_file():
    """Исправляет файл routes.py, удаляя дублирующие функции"""
    
    routes_file = "app/smm/routes.py"
    
    if not os.path.exists(routes_file):
        print(f"❌ Файл {routes_file} не найден")
        return False
    
    # Создаем резервную копию
    backup_file = f"{routes_file}.backup"
    shutil.copy2(routes_file, backup_file)
    print(f"📋 Создана резервная копия: {backup_file}")
    
    # Читаем файл
    with open(routes_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Находим все функции serve_generated_image
    serve_function_lines = []
    for i, line in enumerate(lines):
        if 'def serve_generated_image' in line:
            serve_function_lines.append(i)
    
    print(f"🔍 Найдено функций serve_generated_image: {len(serve_function_lines)}")
    
    if len(serve_function_lines) <= 1:
        print("✅ Дублирующих функций не найдено")
        return True
    
    # Удаляем все функции кроме последней
    lines_to_remove = []
    for i in range(len(serve_function_lines) - 1):
        start_line = serve_function_lines[i]
        # Находим конец функции (следующая функция или конец файла)
        end_line = start_line + 1
        while end_line < len(lines):
            if (lines[end_line].strip().startswith('def ') or 
                lines[end_line].strip().startswith('@bp.route') or
                end_line == len(lines) - 1):
                break
            end_line += 1
        
        # Добавляем строки для удаления
        for j in range(start_line, end_line):
            lines_to_remove.append(j)
    
    # Удаляем строки в обратном порядке
    for line_num in sorted(lines_to_remove, reverse=True):
        del lines[line_num]
    
    # Записываем исправленный файл
    with open(routes_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ Удалено {len(lines_to_remove)} строк с дублирующими функциями")
    print(f"📝 Файл {routes_file} обновлен")
    
    return True

def main():
    print("🚀 Исправление файла routes.py на сервере...")
    
    if fix_routes_file():
        print("✅ Исправление завершено успешно!")
        print("🔄 Перезапустите приложение на PythonAnywhere")
    else:
        print("❌ Ошибка при исправлении файла")

if __name__ == "__main__":
    main()
