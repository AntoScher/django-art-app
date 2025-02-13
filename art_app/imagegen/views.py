import json
import time

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

import requests

from .forms import ImageGenerationForm
from .models import GeneratedImage

GENERATOR_SERVER_URL = "http://127.0.0.1:8080/generate"

import json
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import GeneratedImage
from .forms import ImageGenerationForm

GENERATOR_SERVER_URL = "http://127.0.0.1:8080/generate"
FUSIONBRAIN_STATUS_URL = "https://api-key.fusionbrain.ai/key/api/v1/text2image/status/"

@login_required
def home(request):
    if request.session.get('generation_status') == 'pending' and 'uuid' in request.session:
        uuid = request.session['uuid']
        response = requests.get(FUSIONBRAIN_STATUS_URL + uuid, headers={
            "X-Key": f"Key {settings.FUSIONBRAIN_API_KEY}",
            "X-Secret": f"Secret {settings.FUSIONBRAIN_SECRET_KEY}"
        })
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'DONE':
                request.session['generation_status'] = 'ready'

    if request.method == 'POST':
        form = ImageGenerationForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['prompt']
            request.session['generation_status'] = 'pending'

            response = requests.post(GENERATOR_SERVER_URL, json={
                "user_id": request.user.id,
                "prompt": prompt
            })

            if response.status_code == 200:
                return redirect('home')

    else:
        form = ImageGenerationForm()

    images = GeneratedImage.objects.filter(user=request.user).order_by('-created_at')
    error_message = request.session.pop('error_message', None)

    return render(request, 'imagegen/home.html', {
        'form': form,
        'images': images,
        'generation_status': request.session.get('generation_status', 'ready'),
        'error_message': error_message
    })

def notify(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get("user_id")
        error = data.get("error")
        uuid = data.get("uuid")

        if error:
            request.session['generation_status'] = 'ready'
            request.session['error_message'] = error
            return JsonResponse({"status": "error_handled"})

        if uuid:
            request.session['uuid'] = uuid  # Сохраняем UUID для проверки статуса
            return JsonResponse({"status": "waiting"})

        prompt = data.get("prompt")
        image_data = data.get("image_data")

        if user_id and image_data:
            GeneratedImage.objects.create(
                user_id=user_id,
                prompt=prompt,
                image_data=image_data
            )
            request.session['generation_status'] = 'ready'

        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)


def welcome(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'imagegen/welcome.html')

