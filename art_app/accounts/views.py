from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Можно автоматически авторизовать пользователя после регистрации
            login(request, user)
            return redirect('home')  # Перенаправление на главную страницу (home)
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
