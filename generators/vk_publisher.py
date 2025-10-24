import requests
import json
from typing import Optional, Dict, Any

class VKPublisher:
    def __init__(self, access_token: str, group_id: Optional[str] = None):
        """
        Инициализация VK Publisher
        
        Args:
            access_token: Токен доступа VK
            group_id: ID группы для публикации (опционально)
        """
        self.access_token = access_token
        self.group_id = group_id
        self.base_url = "https://api.vk.com/method"
    
    def check_token(self) -> Dict[str, Any]:
        """
        Проверить валидность токена доступа
        
        Returns:
            Словарь с результатом проверки
        """
        url = f"{self.base_url}/users.get"
        params = {
            'access_token': self.access_token,
            'v': '5.131'
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP Error {response.status_code}: {response.text}'
                }
            
            try:
                data = response.json()
            except ValueError as json_error:
                return {
                    'success': False,
                    'error': f'Ошибка парсинга JSON: {str(json_error)}. Ответ: {response.text[:200]}'
                }
            
            if 'error' in data:
                return {
                    'success': False,
                    'error': f"VK API Error: {data['error']['error_msg']}"
                }
            
            return {
                'success': True,
                'user_info': data['response'][0]
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Ошибка сети: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка проверки токена: {str(e)}'
            }
        
    def get_user_groups(self) -> Dict[str, Any]:
        """
        Получить список групп пользователя
        
        Returns:
            Словарь с информацией о группах
        """
        url = f"{self.base_url}/groups.get"
        params = {
            'access_token': self.access_token,
            'extended': 1,
            'fields': 'id,name,screen_name,photo_50',
            'v': '5.131'
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'error' in data:
                raise Exception(f"VK API Error: {data['error']['error_msg']}")
                
            return data['response']
        except Exception as e:
            raise Exception(f"Ошибка получения групп: {str(e)}")
    
    def upload_photo(self, photo_path: str, group_id: Optional[str] = None) -> str:
        """
        Загрузить фото на сервер VK
        
        Args:
            photo_path: Путь к файлу фото
            group_id: ID группы (если публикуем в группу)
            
        Returns:
            Строка с данными фото для публикации
        """
        # Получаем адрес сервера для загрузки
        upload_url = self._get_upload_server(group_id)
        
        # Загружаем файл
        with open(photo_path, 'rb') as f:
            files = {'photo': f}
            response = requests.post(upload_url, files=files)
            
        upload_data = response.json()
        
        if 'error' in upload_data:
            raise Exception(f"Ошибка загрузки фото: {upload_data['error']['error_msg']}")
        
        # Сохраняем фото
        save_url = f"{self.base_url}/photos.save"
        save_params = {
            'access_token': self.access_token,
            'photo': upload_data['photo'],
            'server': upload_data['server'],
            'hash': upload_data['hash'],
            'v': '5.131'
        }
        
        if group_id:
            save_params['group_id'] = group_id
            
        save_response = requests.get(save_url, params=save_params)
        save_data = save_response.json()
        
        if 'error' in save_data:
            raise Exception(f"Ошибка сохранения фото: {save_data['error']['error_msg']}")
        
        photo = save_data['response'][0]
        return f"photo{photo['owner_id']}_{photo['id']}"
    
    def _get_upload_server(self, group_id: Optional[str] = None) -> str:
        """
        Получить адрес сервера для загрузки фото
        
        Args:
            group_id: ID группы
            
        Returns:
            URL сервера для загрузки
        """
        url = f"{self.base_url}/photos.getUploadServer"
        params = {
            'access_token': self.access_token,
            'v': '5.131'
        }
        
        if group_id:
            params['group_id'] = group_id
            
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            raise Exception(f"Ошибка получения сервера: {data['error']['error_msg']}")
            
        return data['response']['upload_url']
    
    def publish_post(self, message: str, photo_path: Optional[str] = None, 
                    group_id: Optional[str] = None, from_group: bool = True) -> Dict[str, Any]:
        """
        Опубликовать пост в VK
        
        Args:
            message: Текст поста
            photo_path: Путь к файлу фото (опционально)
            group_id: ID группы для публикации
            from_group: Публиковать от имени группы
            
        Returns:
            Словарь с результатом публикации
        """
        url = f"{self.base_url}/wall.post"
        params = {
            'access_token': self.access_token,
            'message': message,
            'v': '5.131'
        }
        
        if group_id:
            params['owner_id'] = f"-{group_id}"
            if from_group:
                params['from_group'] = 1
        
        # Добавляем фото если указано
        if photo_path:
            try:
                photo_attachment = self.upload_photo(photo_path, group_id)
                params['attachments'] = photo_attachment
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Ошибка загрузки фото: {str(e)}'
                }
        
        try:
            response = requests.get(url, params=params)
            
            # Проверяем статус ответа
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP Error {response.status_code}: {response.text}'
                }
            
            # Проверяем содержимое ответа
            try:
                data = response.json()
            except ValueError as json_error:
                return {
                    'success': False,
                    'error': f'Ошибка парсинга JSON: {str(json_error)}. Ответ: {response.text[:200]}'
                }
            
            if 'error' in data:
                return {
                    'success': False,
                    'error': f"VK API Error: {data['error']['error_msg']}"
                }
            
            return {
                'success': True,
                'post_id': data['response']['post_id'],
                'message': 'Пост успешно опубликован'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Ошибка сети: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка публикации: {str(e)}'
            }
    
    def schedule_post(self, message: str, publish_date: int, photo_path: Optional[str] = None,
                     group_id: Optional[str] = None, from_group: bool = True) -> Dict[str, Any]:
        """
        Запланировать публикацию поста
        
        Args:
            message: Текст поста
            publish_date: Unix timestamp времени публикации
            photo_path: Путь к файлу фото (опционально)
            group_id: ID группы для публикации
            from_group: Публиковать от имени группы
            
        Returns:
            Словарь с результатом планирования
        """
        url = f"{self.base_url}/wall.post"
        params = {
            'access_token': self.access_token,
            'message': message,
            'publish_date': publish_date,
            'v': '5.131'
        }
        
        if group_id:
            params['owner_id'] = f"-{group_id}"
            if from_group:
                params['from_group'] = 1
        
        # Добавляем фото если указано
        if photo_path:
            try:
                photo_attachment = self.upload_photo(photo_path, group_id)
                params['attachments'] = photo_attachment
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Ошибка загрузки фото: {str(e)}'
                }
        
        try:
            response = requests.get(url, params=params)
            
            # Проверяем статус ответа
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP Error {response.status_code}: {response.text}'
                }
            
            # Проверяем содержимое ответа
            try:
                data = response.json()
            except ValueError as json_error:
                return {
                    'success': False,
                    'error': f'Ошибка парсинга JSON: {str(json_error)}. Ответ: {response.text[:200]}'
                }
            
            if 'error' in data:
                return {
                    'success': False,
                    'error': f"VK API Error: {data['error']['error_msg']}"
                }
            
            return {
                'success': True,
                'post_id': data['response']['post_id'],
                'message': 'Пост успешно запланирован'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Ошибка сети: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка планирования: {str(e)}'
            }
    
    def get_post_stats(self, post_id: str, group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Получить статистику поста
        
        Args:
            post_id: ID поста
            group_id: ID группы
            
        Returns:
            Словарь со статистикой
        """
        url = f"{self.base_url}/wall.getById"
        params = {
            'access_token': self.access_token,
            'posts': f"{group_id}_{post_id}" if group_id else post_id,
            'v': '5.131'
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP Error {response.status_code}: {response.text}'
                }
            
            try:
                data = response.json()
            except ValueError as json_error:
                return {
                    'success': False,
                    'error': f'Ошибка парсинга JSON: {str(json_error)}. Ответ: {response.text[:200]}'
                }
            
            if 'error' in data:
                return {
                    'success': False,
                    'error': f"VK API Error: {data['error']['error_msg']}"
                }
            
            # Проверяем структуру ответа
            if 'response' not in data:
                return {
                    'success': False,
                    'error': 'Некорректный ответ от VK API'
                }
            
            response = data['response']
            if 'items' not in response or not response['items']:
                return {
                    'success': False,
                    'error': 'Пост не найден или недоступен'
                }
            
            post = response['items'][0]
            return {
                'success': True,
                'post_id': post.get('id', 'N/A'),
                'likes': post.get('likes', {}).get('count', 0),
                'reposts': post.get('reposts', {}).get('count', 0),
                'comments': post.get('comments', {}).get('count', 0),
                'views': post.get('views', {}).get('count', 0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения статистики: {str(e)}'
            }
    
    def get_group_stats(self, group_id: str, date_from: Optional[str] = None, 
                       date_to: Optional[str] = None, interval: str = 'day',
                       stats_groups: Optional[str] = None) -> Dict[str, Any]:
        """
        Получить статистику сообщества
        
        Args:
            group_id: ID группы
            date_from: Начальная дата в формате YYYY-MM-DD
            date_to: Конечная дата в формате YYYY-MM-DD
            interval: Временной интервал (day, week, month, year, all)
            stats_groups: Фильтр статистики (visitors, reach, activity)
            
        Returns:
            Словарь со статистикой сообщества
        """
        url = f"{self.base_url}/stats.get"
        params = {
            'access_token': self.access_token,
            'group_id': group_id,
            'interval': interval,
            'v': '5.131'
        }
        
        # Добавляем параметры даты если указаны (используем timestamp)
        if date_from:
            try:
                from datetime import datetime
                dt = datetime.strptime(date_from, '%Y-%m-%d')
                params['timestamp_from'] = int(dt.timestamp())
            except ValueError:
                pass  # Игнорируем неверный формат даты
        if date_to:
            try:
                from datetime import datetime
                dt = datetime.strptime(date_to, '%Y-%m-%d')
                params['timestamp_to'] = int(dt.timestamp())
            except ValueError:
                pass  # Игнорируем неверный формат даты
        if stats_groups:
            params['stats_groups'] = stats_groups
            
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'error' in data:
                return {
                    'success': False,
                    'error': f"VK API Error: {data['error']['error_msg']}"
                }
            
            return {
                'success': True,
                'stats': data['response']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения статистики сообщества: {str(e)}'
            }
    
    def get_app_stats(self, app_id: str, date_from: Optional[str] = None,
                     date_to: Optional[str] = None, interval: str = 'day') -> Dict[str, Any]:
        """
        Получить статистику приложения
        
        Args:
            app_id: ID приложения
            date_from: Начальная дата в формате YYYY-MM-DD
            date_to: Конечная дата в формате YYYY-MM-DD
            interval: Временной интервал (day, week, month, year, all)
            
        Returns:
            Словарь со статистикой приложения
        """
        url = f"{self.base_url}/stats.get"
        params = {
            'access_token': self.access_token,
            'app_id': app_id,
            'interval': interval,
            'v': '5.131'
        }
        
        # Добавляем параметры даты если указаны (используем timestamp)
        if date_from:
            try:
                from datetime import datetime
                dt = datetime.strptime(date_from, '%Y-%m-%d')
                params['timestamp_from'] = int(dt.timestamp())
            except ValueError:
                pass  # Игнорируем неверный формат даты
        if date_to:
            try:
                from datetime import datetime
                dt = datetime.strptime(date_to, '%Y-%m-%d')
                params['timestamp_to'] = int(dt.timestamp())
            except ValueError:
                pass  # Игнорируем неверный формат даты
            
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'error' in data:
                return {
                    'success': False,
                    'error': f"VK API Error: {data['error']['error_msg']}"
                }
            
            return {
                'success': True,
                'stats': data['response']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения статистики приложения: {str(e)}'
            }
