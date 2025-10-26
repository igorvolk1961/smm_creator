from flask import render_template, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.smm import bp
from generators.vk_publisher import VKPublisher
from generators.image_gen import ImageGenerator
import os
from datetime import datetime, timedelta

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        vk_api_id = request.form.get('vk_api_id')
        vk_group_id = request.form.get('vk_group_id')
        
        if username:
            current_user.username = username
        if email:
            current_user.email = email
        if vk_api_id:
            current_user.vk_api_id = vk_api_id
        if vk_group_id:
            current_user.vk_group_id = vk_group_id
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Профиль обновлен'})
    
    return render_template('smm/profile.html')

@bp.route('/content-generator')
@login_required
def content_generator():
    return render_template('smm/content_generator.html')

@bp.route('/vk-publisher')
@login_required
def vk_publisher():
    return render_template('smm/vk_publisher.html')

@bp.route('/analytics')
@login_required
def analytics():
    return render_template('smm/analytics.html')

@bp.route('/generate-content', methods=['POST'])
@login_required
def generate_content():
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        style = data.get('style', '')
        platform = data.get('platform', '')
        
        if not topic:
            return jsonify({'success': False, 'error': 'Тема не может быть пустой'}), 400
        
        # Генерируем контент
        text_generator = current_app.text_generator
        
        # Генерируем текст сообщения
        message_prompt = f"Создай пост для {platform} на тему '{topic}' в стиле {style}. Пост должен быть интересным и привлекательным."
        message = text_generator.generate_text(message_prompt)
        
        # Генерируем описание изображения
        image_prompt = f"Создай описание изображения для поста на тему '{topic}' в стиле {style}. Описание должно быть детальным и подходящим для генерации изображения."
        image_description = text_generator.generate_text(image_prompt)
        
        return jsonify({
            'success': True,
            'message': message,
            'image_description': image_description
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/vk/groups')
@login_required
def get_vk_groups():
    """Получить список групп VK пользователя"""
    try:
        config = current_app.config['API_CONFIG']
        vk_token = config['api_keys']['vk_access_token']
        
        vk_publisher = VKPublisher(vk_token)
        groups = vk_publisher.get_groups()
        
        return jsonify(groups)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/vk/publish', methods=['POST'])
@login_required
def publish_to_vk():
    """Публикация поста в VK"""
    try:
        # Проверяем тип контента
        if request.content_type and 'application/json' in request.content_type:
            # Данные приходят из генератора контента
            data = request.get_json()
            message = data.get('message', '')
            photo_file = None
        else:
            # Данные приходят из формы публикатора
            message = request.form.get('message', '')
            photo_file = request.files.get('photo')
        
        if not message:
            return jsonify({'success': False, 'error': 'Текст поста не может быть пустым'}), 400
        
        config = current_app.config['API_CONFIG']
        vk_token = config['api_keys']['vk_access_token']
        vk_group_id = config['api_keys']['vk_group_id']
        
        vk_publisher = VKPublisher(vk_token, vk_group_id)
        
        # Обработка фотографии
        photo_path = None
        if photo_file and photo_file.filename:
            upload_dir = 'uploads'
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            filename = f"vk_photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            photo_path = os.path.join(upload_dir, filename)
            photo_file.save(photo_path)
        
        # Публикуем пост
        result = vk_publisher.publish_post(
            message=message,
            photo_path=photo_path,
            group_id=vk_group_id,
            from_group=True
        )
        
        # Удаляем временный файл
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/vk/schedule', methods=['POST'])
@login_required
def schedule_vk_post():
    """Планирование поста в VK"""
    try:
        message = request.form.get('message', '')
        publish_date = request.form.get('publish_date', '')
        
        if not message or not publish_date:
            return jsonify({'success': False, 'error': 'Текст и дата публикации обязательны'}), 400
        
        config = current_app.config['API_CONFIG']
        vk_token = config['api_keys']['vk_access_token']
        vk_group_id = config['api_keys']['vk_group_id']
        
        vk_publisher = VKPublisher(vk_token, vk_group_id)
        
        # Парсим дату
        try:
            publish_datetime = datetime.strptime(publish_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            return jsonify({'success': False, 'error': 'Неверный формат даты'}), 400
        
        result = vk_publisher.schedule_post(
            message=message,
            publish_date=publish_datetime,
            group_id=vk_group_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/vk/stats/<post_id>')
@login_required
def get_vk_post_stats(post_id):
    """Получить статистику поста VK"""
    try:
        group_id = request.args.get('group_id')
        
        config = current_app.config['API_CONFIG']
        vk_token = config['api_keys']['vk_access_token']
        vk_group_id = config['api_keys']['vk_group_id']
        
        # Используем группу из конфига, игнорируем переданный group_id
        vk_publisher = VKPublisher(vk_token, vk_group_id)
        stats = vk_publisher.get_post_stats(post_id, vk_group_id)
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/generate-image', methods=['POST'])
@login_required
def generate_image():
    """Генерация изображения по описанию"""
    try:
        data = request.get_json()
        description = data.get('description', '')
        
        if not description:
            return jsonify({'success': False, 'error': 'Описание изображения не может быть пустым'}), 400
        
        img_gen = current_app.image_generator
        
        # Создаем папку для изображений если не существует
        images_dir = 'static/generated_images'
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        # Генерируем уникальное имя файла
        filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(images_dir, filename)
        
        # Генерируем и сохраняем изображение
        img_gen.generate_and_save(description, filepath)
        
        # Возвращаем URL изображения
        image_url = f"/static/generated_images/{filename}"
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'message': 'Изображение успешно сгенерировано',
            'provider': img_gen.provider
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/vk/check-token')
@login_required
def check_vk_token():
    """Проверить валидность VK токена"""
    try:
        config = current_app.config['API_CONFIG']
        vk_token = config['api_keys']['vk_access_token']
        
        vk_publisher = VKPublisher(vk_token)
        result = vk_publisher.check_token()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/vk/group-stats')
@login_required
def get_vk_group_stats():
    """Получить статистику группы VK"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        interval = request.args.get('interval', 'day')
        stats_groups = request.args.get('stats_groups')
        
        config = current_app.config['API_CONFIG']
        vk_token = config['api_keys']['vk_access_token']
        vk_group_id = config['api_keys']['vk_group_id']
        
        vk_publisher = VKPublisher(vk_token, vk_group_id)
        stats = vk_publisher.get_group_stats(
            group_id=vk_group_id,
            date_from=date_from,
            date_to=date_to,
            interval=interval,
            stats_groups=stats_groups
        )
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/static/generated_images/<filename>')
def serve_generated_image(filename):
    """Отдача сгенерированных изображений"""
    try:
        images_dir = os.path.join(current_app.root_path, '..', 'static', 'generated_images')
        return send_from_directory(images_dir, filename)
    except Exception as e:
        return f"Error serving image: {e}", 404