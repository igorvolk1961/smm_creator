# Инструкции для исправления ошибок на сервере PythonAnywhere

## Проблема 1: Дублирующая функция serve_generated_image

### Решение:
1. Зайдите в консоль PythonAnywhere
2. Перейдите в папку проекта: `cd ~/smm_creator`
3. Запустите скрипт исправления: `python update_server.py`

### Или вручную:
1. Откройте файл `app/smm/routes.py`
2. Найдите все функции `def serve_generated_image`
3. Удалите все кроме последней (строки 308-315)

## Проблема 2: Ошибка в шаблоне base.html

### Решение:
1. Откройте файл `templates/base.html`
2. Найдите строку 77:
   ```html
   <a class="nav-link {% if request.endpoint == 'smm.scheduler' %}active{% endif %}" href="{{ url_for('smm.scheduler') }}">
   ```
3. Замените на:
   ```html
   <a class="nav-link {% if request.endpoint == 'smm.vk_publisher' %}active{% endif %}" href="{{ url_for('smm.vk_publisher') }}">
   ```

## После исправления:
1. Перезапустите приложение на PythonAnywhere
2. Проверьте, что ошибки исчезли

## Альтернативное решение:
Если у вас есть доступ к файлам через веб-интерфейс PythonAnywhere:
1. Скопируйте содержимое исправленного файла `app/smm/routes.py` (315 строк)
2. Вставьте его в файл на сервере, заменив содержимое
3. Также исправьте `templates/base.html` как указано выше
