from openai import OpenAI

class TextGenerator:
    def __init__(self, api_key, base_url):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.tone = None
        self.topic = None
    
    def set_tone(self, tone):
        self.tone = tone
    
    def set_topic(self, topic):
        self.topic = topic

    def generate_post(self):
        if not self.tone or not self.topic:
            raise ValueError("Tone and topic must be set before generating post")
            
        response = self.client.chat.completions.create(
          model="deepseek-chat",
          response_format={"type": "json_object"},
          messages=[
            {"role": "system", "content": "Ты высококвалифицированный SMM специалист, который будет помогать в генерации текста для постов с заданной тебе тематикой и заданным тоном. Ответ должен быть в формате json."},
            {"role": "user", "content": f"Сгенерируй пост, используя тон: {self.tone}, для соцсетей с темой {self.topic}"}
            ]
          )
        return response.choices[0].message.content

    def generate_post_image_description(self):
        if not self.topic:
            raise ValueError("Topic must be set before generating image description")
            
        response = self.client.chat.completions.create(
          model="deepseek-chat",
          messages=[
            {"role": "system", "content": "Ты ассистент, который составит промпт для нейросети, которая будет генерировать изображения. Ты должен составлять промпт на заданную тематику на английском языке."},
            {"role": "user", "content": f"Сгенерируй пормпт на английском языке для генерации изображения для соцсетей с темой {self.topic}."}
          ]
        )
        return response.choices[0].message.content