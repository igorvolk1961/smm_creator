import requests
import base64
import io
from PIL import Image
import json
from pathlib import Path

class ImageGenerator:
    def __init__(self, base_url):
        self.base_url = base_url
       
        self.client = requests.Session()
    
    def generate_image(self, prompt, size="1024x1024", quality="standard", n=1):
        """
        Генерирует изображение по промпту
        Аналогично OpenAI API, но возвращает PIL Image вместо URL
        """
        # Парсим размер
        width, height = map(int, size.split('x'))
        
        # Настройки качества
        steps = 20 if quality == "standard" else 30
        
        # Базовый payload для Stable Diffusion
        payload = {
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, cartoon, anime, ugly, bad anatomy",
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": 7,
            "sampler_name": "DPM++ 2M Karras",
            "seed": -1,
            "batch_size": n
        }
        
        try:
            response = self.client.post(
                url=f'{self.base_url}/sdapi/v1/txt2img',
                json=payload,
                timeout=120  # Увеличиваем таймаут для генерации
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'images' in result and len(result['images']) > 0:
                # Декодируем base64 и возвращаем PIL Image
                image_data = base64.b64decode(result['images'][0])
                image = Image.open(io.BytesIO(image_data))
                return image
            else:
                raise Exception("No images in response")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Stable Diffusion API request failed: {e}")

    def generate_and_save(self, prompt, filename="generated_image.png", **kwargs):
        """Генерирует и сохраняет изображение"""
        image = self.generate_image(prompt, **kwargs)
        image.save(filename)
        return filename