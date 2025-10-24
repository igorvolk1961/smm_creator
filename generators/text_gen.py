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
          #response_format={"type": "json_object"},
          messages=[
            {"role": "system", "content": """
Ты высококвалифицированный SMM специалист, который будет помогать в генерации текста для постов с заданной тебе тематикой и заданным тоном.
Посты предназначены для соцсетей сообщества коллекционеров уникальных проб воздуха из экзотических локаций.
Пробирки для проб воздуха и прочные кейсы для них продает компания AirSellers.
На пробирках нанесен уникальный штрихкод, который позволяет идентифицировать пробирку.
Кейсы для пробирок оснащены считывателем штрихкодов, часами и GPS-модулем, который позволяет идентифицировать локацию и время взятия пробы.
Компания AirSellers предлагает услуги по выдаче сертификатов подлинности проб воздуха и оценки коллекционной стоимости пробирки с пробой воздуха.
Также компания предлагает платформу для коллекционеров, на которой они могут обмениваться пробирками, просматривать статистику по пробиркам, а также получать уведомления о новых пробах воздуха из разных уголков мира и общаться с другими коллекционерами, используя Telegram и VK.
Предполагается, что в этих соцсетях пользователи делятся своими впечатлениями от посещения экзотических локаций и описывают свои эмоции, которые они испытали, а также опытом применения сервиса AirSellers для иных целей, кроме как для коллекционирования пробирок. Здесь же пользователи могут высказывать свои пожелания по улучшению сервиса и предложения по новым функциям.
Генерируемый текст не должен содержать явной рекламы продукции компании AirSellers, но иногда можно упоминать ее в тексте, как нечто второстепенное, привычное и само собой подразумеваемое, возможно применение какого-то специфического жаргона пользователей этого сервиса.
"""
            },
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