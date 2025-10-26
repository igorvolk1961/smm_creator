import requests
import base64
import io
from PIL import Image
import json
from pathlib import Path
from openai import OpenAI
from typing import Optional, Dict, Any

class ImageGenerator:
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация генератора изображений
        
        Args:
            config: Конфигурация генерации изображений
        """
        self.config = config
        self.provider = config.get('provider', 'stable_diffusion')
        self.client = requests.Session()
        
        # Инициализация клиентов в зависимости от провайдера
        if self.provider == 'gpt4o':
            gpt4o_config = config.get('gpt4o', {})
            self.openai_client = OpenAI(
                api_key=gpt4o_config.get('api_key'),
                base_url=gpt4o_config.get('base_url', 'https://api.openai.com/v1')
            )
            self.text_model = gpt4o_config.get('text_model', 'gpt-4o')
            self.image_model = gpt4o_config.get('image_model', 'dall-e-3')
        elif self.provider == 'dalle':
            dalle_config = config.get('dalle', {})
            self.openai_client = OpenAI(api_key=dalle_config.get('api_key'))
            self.model = dalle_config.get('model', 'dall-e-3')
        else:
            # WEBUI (Stable Diffusion)
            webui_config = config.get('webui', {})
            self.base_url = webui_config.get('base_url', 'http://localhost:7860')
    
    def generate_image(self, prompt, size="1024x1024", quality="standard", n=1):
        """
        Генерирует изображение по промпту в зависимости от провайдера
        
        Args:
            prompt: Текст промпта для генерации
            size: Размер изображения (например, "1024x1024")
            quality: Качество генерации ("standard" или "hd")
            n: Количество изображений
            
        Returns:
            PIL Image объект
        """
        if self.provider == 'gpt4o':
            return self._generate_with_gpt4o(prompt, size, quality, n)
        elif self.provider == 'dalle':
            return self._generate_with_dalle(prompt, size, quality, n)
        else:
            return self._generate_with_webui(prompt, size, quality, n)
    
    def _generate_with_gpt4o(self, prompt, size, quality, n):
        """Генерация через GPT-4o с vision capabilities"""
        try:
            # GPT-4o может генерировать изображения через специальный API
            # Здесь мы используем GPT-4o для создания промпта для DALL-E
            enhanced_prompt = self._enhance_prompt_with_gpt4o(prompt)
            
            # Затем используем DALL-E для генерации
            return self._generate_with_dalle(enhanced_prompt, size, quality, n)
            
        except Exception as e:
            raise Exception(f"GPT-4o generation failed: {e}")
    
    def _enhance_prompt_with_gpt4o(self, original_prompt):
        """Улучшает промпт с помощью GPT-4o"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Ты эксперт по созданию промптов для генерации изображений. Твоя задача - улучшить данный промпт, сделав его более детальным и эффективным для генерации качественных изображений. Отвечай только улучшенным промптом на английском языке."
                    },
                    {
                        "role": "user", 
                        "content": f"Улучши этот промпт для генерации изображения: {original_prompt}"
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Если GPT-4o недоступен, возвращаем оригинальный промпт
            return original_prompt
    
    def _generate_with_dalle(self, prompt, size, quality, n):
        """Генерация через DALL-E"""
        try:
            # Преобразуем размер для DALL-E
            size_mapping = {
                "1024x1024": "1024x1024",
                "1024x1792": "1024x1792", 
                "1792x1024": "1792x1024"
            }
            dalle_size = size_mapping.get(size, "1024x1024")
            
            # Используем правильную модель для DALL-E
            if self.provider == 'gpt4o':
                dalle_model = self.image_model  # Используем модель изображений из конфига
            else:
                dalle_model = self.model  # Для провайдера dalle используем настроенную модель
            
            response = self.openai_client.images.generate(
                model=dalle_model,
                prompt=prompt,
                size=dalle_size,
                quality=quality,
                n=min(n, 1)  # DALL-E поддерживает только 1 изображение за раз
            )
            
            # Скачиваем изображение
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Создаем PIL Image
            image = Image.open(io.BytesIO(image_response.content))
            return image
            
        except Exception as e:
            raise Exception(f"DALL-E generation failed: {e}")
    
    def _generate_with_webui(self, prompt, size, quality, n):
        """Генерация через Stable Diffusion"""
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