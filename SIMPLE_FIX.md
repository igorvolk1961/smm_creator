# Простое исправление на сервере PythonAnywhere

## Проблема: AssertionError: View function mapping is overwriting an existing endpoint function

### Решение:

1. **Откройте файл `app/smm/routes.py` на сервере**

2. **Найдите все функции `def serve_generated_image`** (их может быть несколько)

3. **Удалите все функции кроме последней** (строки 308-315):
   ```python
   @bp.route('/static/generated_images/<filename>')
   def serve_generated_image(filename):
       """Отдача сгенерированных изображений"""
       try:
           images_dir = os.path.join(current_app.root_path, '..', 'static', 'generated_images')
           return send_from_directory(images_dir, filename)
       except Exception as e:
           return f"Error serving image: {e}", 404
   ```

4. **Исправьте файл `templates/base.html`**:
   - Найдите строку с `smm.scheduler`
   - Замените на `smm.vk_publisher`

5. **Перезапустите приложение**

### Альтернатива:
Скопируйте весь содержимое файла `app/smm/routes.py` (315 строк) и замените им файл на сервере.
