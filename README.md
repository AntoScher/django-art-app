# Django Image Generator

## Описание
Django-приложение для генерации изображений с использованием сервиса FusionBrain. Работает с `aiohttp`-сервисом, который отправляет запросы в Django (`notify`).

## Требования
Перед запуском убедись, что установлены:
- **Python 3.8+**
- **Django**
- **aiohttp**

## Установка
### 1. Клонирование репозитория
```bash
git clone <репозиторий>
cd <папка_проекта>
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/macOS
venv\Scripts\activate    # Для Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
Создай файл `.env` в корневой папке проекта и добавь в него:
```env
DJANGO_SECRET_KEY='django-insecure-4p$em_66nto*#l-)^_$#88xlh%(r(_nxg&#1k!fkase2h1%a*2'
API_KEY='89EE7FEBBFD40F7F54F70D55876756FC'
SECRET_KEY='3ABFB332E4DB01045608AF5DE67ADB03'
```

### 5. Применение миграций
```bash
python manage.py migrate
```

### 6. Запуск сервера
```bash
python manage.py runserver
```

## Структура проекта
```
project/
│── accounts/        # Приложение авторизации
│   ├── __init__.py    
│   ├── models.py    # Модель хранения пользователей
│   ├── forms.py     # Формы для авторизации
│   ├── views.py     # Основные представления Django
│── art_app/         # Core приложение
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│── imagegen/        # Приложение генерации изображений
│   ├── __init__.py
│   ├── models.py    # Модель хранения изображений
│   ├── forms.py     # Формы для запросов не генерацию
│   ├── views.py     # Основные представления Django
│── .env             # Файл с переменными окружения
│── manage.py        # Управление Django
│── requirements.txt # Зависимости
```

## API
### Запрос на генерацию изображения
**Метод:** `POST`
**URL:** `http://127.0.0.1:8080/generate`

#### **Пример запроса:**
```json
{
    "user_id": 1,
    "prompt": "кот в сапогах"
}
```

### Оповещение Django о готовности изображения
**Метод:** `POST`
**URL:** `http://127.0.0.1:8000/notify/`

#### **Пример успешного ответа:**
```json
{
    "status": "ok"
}
```

## Инструкция по использованию
1. **Запусти Django-сервер** (`python manage.py runserver`).
2. **Запусти aiohttp-сервис** (`python image_generator.py`)

## Тестирование
1. **Отправь запрос на генерацию** через веб-интерфейс или Postman.
2. **Дождись результата и проверь изображения в галерее.**

---
Если возникли вопросы — смотри логи Django и `aiohttp`. 🚀

