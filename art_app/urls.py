from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from imagegen import views as imagegen_views
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', imagegen_views.welcome, name='welcome'),
    path('home/', imagegen_views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', accounts_views.signup, name='signup'),
    path('notify/', imagegen_views.notify, name='notify'),
]
