import json
import sys
from pathlib import Path

# Добавляем путь к папке generators
sys.path.append(str(Path(__file__).parent / 'generators'))

from text_gen import TextGenerator
#from image_gen import ImageGenerator
from pathlib import Path

# Загружаем конфигурацию из JSON файла
project_root = Path(__file__).parent.parent
config_path = 'config.json'

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

deepseek_api_key = config['api_keys']['deepseek']
deepseek_base_url = config['api_urls']['deepseek']
stable_diffusion_base_url = config['api_urls']['stable_diffusion']

post_gen = TextGenerator(deepseek_api_key, deepseek_base_url, tone="позитивный и весёлый", topic="""
Новая коллекция кухонных ножей от компании ZeroKnifes""")
content = post_gen.generate_post()
img_desc = post_gen.generate_post_image_description()

#img_gen = ImageGenerator(stable_diffusion_base_url)
#image_file_name = img_gen.generate_and_save(img_desc)

print(content)
#print(img_desc)
#print(image_file_name)