import json
import os

import asyncio
import aiohttp
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

DJANGO_SERVER_URL = "http://127.0.0.1:8000/notify/"  # Django URL для уведомления
FUSIONBRAIN_URL = "https://api-key.fusionbrain.ai/"

class Text2ImageAPI:
    def __init__(self):
        self.URL = FUSIONBRAIN_URL
        self.AUTH_HEADERS = {
            'X-Key': f'Key {os.getenv("API_KEY")}',
            'X-Secret': f'Secret {os.getenv("SECRET_KEY")}',
        }

    async def get_model(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS) as response:
                data = await response.json()
                if response.status != 200:
                    print(f"Ошибка получения модели: {data}")
                    return None
                return data[0].get('id')

    async def generate(self, prompt, model):
        params = {
            "type": "GENERATE",
            "numImages": 1,
            "width": 1024,
            "height": 1024,
            "generateParams": {"query": prompt}
        }

        form_data = aiohttp.FormData()
        form_data.add_field("model_id", str(model))
        form_data.add_field("params", json.dumps(params), content_type="application/json")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.URL + 'key/api/v1/text2image/run',
                headers=self.AUTH_HEADERS,
                data=form_data
            ) as response:
                data = await response.json()
                if response.status != 201:
                    print(f"Ошибка генерации: {data}")
                    return None
                return data.get('uuid')

    async def check_generation(self, request_id, attempts=30, delay=10):
        async with aiohttp.ClientSession() as session:
            while attempts > 0:
                async with session.get(
                    self.URL + f'key/api/v1/text2image/status/{request_id}', headers=self.AUTH_HEADERS
                ) as response:
                    data = await response.json()
                    if response.status != 200:
                        print(f"Ошибка проверки статуса: {data}")
                        return None
                    if data.get('status') == 'DONE':
                        images = data.get('images')
                        return images
                print(f"Ожидание генерации... Осталось попыток: {attempts}")
                await asyncio.sleep(delay)
                attempts -= 1
        print("Генерация не удалась, превышено число попыток.")
        return None


async def generate_image(request):
    data = await request.json()
    user_id = data.get("user_id")
    prompt = data.get("prompt")

    fusion_api = Text2ImageAPI()
    model_id = await fusion_api.get_model()
    if not model_id:
        return web.json_response({"status": "error", "message": "Не удалось получить модель"})

    request_id = await fusion_api.generate(prompt, model_id)
    if not request_id:
        return web.json_response({"status": "error", "message": "Ошибка при запуске генерации"})

    # Отправляем Django uuid, чтобы он мог следить за генерацией
    async with aiohttp.ClientSession() as session:
        async with session.post(DJANGO_SERVER_URL, json={"user_id": user_id, "uuid": request_id, "prompt": prompt}) as response:
            print(f"[aiohttp] Отправлен UUID в Django: {await response.text()}")

    # Ждём генерацию
    images = await fusion_api.check_generation(request_id)
    if not images:
        async with aiohttp.ClientSession() as session:
            async with session.post(DJANGO_SERVER_URL, json={"user_id": user_id, "error": "Генерация не удалась"}) as response:
                print(f"[aiohttp] Ошибка генерации, отправлена в Django: {await response.text()}")
        return web.json_response({"status": "failed"})

    # **ПРАВИЛЬНЫЙ ФОРМАТ `image_data`** (теперь массив!)
    async with aiohttp.ClientSession() as session:
        async with session.post(DJANGO_SERVER_URL, json={"user_id": user_id, "prompt": prompt, "image_data": [images[0]]}) as response:
            print(f"[aiohttp] Изображение отправлено в Django: {await response.text()}")


    return web.json_response({"status": "completed"})


app = web.Application()
app.router.add_post("/generate", generate_image)

if __name__ == "__main__":
    web.run_app(app, host="127.0.0.1", port=8080)
