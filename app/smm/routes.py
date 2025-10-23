from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.smm import bp

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        data = request.get_json()
        current_user.vk_api_id = data.get('vk_api_id')
        current_user.vk_group_id = data.get('vk_group_id')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Настройки сохранены'})
    
    return render_template('smm/profile.html', user=current_user)

@bp.route('/content-generator')
@login_required
def content_generator():
    return render_template('smm/content_generator.html')

@bp.route('/generate', methods=['POST'])
@login_required
def generate_content():
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        tone = data.get('tone', 'позитивный')
        
        # Используем уже созданный генератор
        text_gen = current_app.text_generator
        text_gen.set_tone(tone)
        text_gen.set_topic(topic)
        
        post_content = text_gen.generate_post()
        # image_description = text_gen.generate_post_image_description()
        
        # # Генерируем изображение
        # img_gen = current_app.image_generator
        # image_url = img_gen.generate_image(image_description)
        
        return jsonify({
            'success': True,
            'post_content': post_content
            # 'image_description': image_description,
            # 'image_url': image_url
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/analytics')
@login_required
def analytics():
    return render_template('smm/analytics.html')

@bp.route('/scheduler')
@login_required
def scheduler():
    return render_template('smm/scheduler.html')
