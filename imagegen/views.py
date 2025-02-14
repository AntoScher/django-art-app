import json
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import GeneratedImage
from .forms import ImageGenerationForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe


GENERATOR_SERVER_URL = "http://127.0.0.1:8080/generate"


@login_required
def home(request):
    # Сбрасываем generation_status при каждом запуске
    print("[home] Сброс session['generation_status'] в 'ready'")
    request.session['generation_status'] = 'ready'

    if request.method == 'POST':
        form = ImageGenerationForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['prompt']
            request.session['generation_status'] = 'pending'
            print(
                f"[home] Начало генерации. Установлен 'generation_status' в 'pending' для пользователя {request.user.id}")

            # Отправляем запрос на генерацию, но не проверяем статус вручную
            response = requests.post(GENERATOR_SERVER_URL, json={
                "user_id": request.user.id,
                "prompt": prompt
            })

            print(f"[home] Отправлен запрос на генерацию: статус {response.status_code}, ответ {response.text}")

            if response.status_code == 200:
                return redirect('home')

    else:
        form = ImageGenerationForm()

    images = GeneratedImage.objects.filter(user=request.user).order_by('-created_at')
    print(f"[home] Загружены изображения из БД: {len(images)} записей")

    for image in images:
        if image.image_data:  # Проверяем, есть ли данные
            image.image_data = mark_safe(f"data:image/jpeg;base64,{image.image_data[2:-2]}")

    error_message = request.session.pop('error_message', None)
    if error_message:
        print(f"[home] Ошибка из сессии: {error_message}")

    return render(request, 'imagegen/home.html', {
        'form': form,
        'images': images,
        'generation_status': request.session.get('generation_status', 'ready'),
        'error_message': error_message
    })


@csrf_exempt
def notify(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(f"[notify] Получен POST-запрос: {data}")

        user_id = data.get("user_id")
        error = data.get("error")
        uuid = data.get("uuid")

        if error:
            request.session['generation_status'] = 'ready'
            request.session['error_message'] = error
            print(f"[notify] Ошибка при генерации: {error}")
            return JsonResponse({"status": "error_handled"})

        if uuid:
            request.session['uuid'] = uuid  # Сохраняем UUID, но не проверяем статус в `home`
            print(f"[notify] Сохранён UUID генерации: {uuid} для пользователя {user_id}")
            return JsonResponse({"status": "waiting"})

        prompt = data.get("prompt")
        image_data = data.get("image_data")

        if user_id and image_data:
            print(f"[notify] Получено изображение для пользователя {user_id}. Сохранение в БД...")

            try:
                GeneratedImage.objects.create(
                    user_id=user_id,
                    prompt=prompt,
                    image_data=image_data
                )
                print("[notify] Успешно сохранено в БД")
            except Exception as e:
                print(f"[notify] Ошибка при сохранении в БД: {e}")

            request.session['generation_status'] = 'ready'
            return JsonResponse({"status": "ok"})

        print("[notify] Ошибка: отсутствуют обязательные данные")
        return JsonResponse({"status": "error"}, status=400)

    print("[notify] Некорректный метод запроса")
    return JsonResponse({"status": "error"}, status=400)


def welcome(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'imagegen/welcome.html')
