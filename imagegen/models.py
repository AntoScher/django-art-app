from django.db import models
from django.contrib.auth.models import User

class GeneratedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_images')
    prompt = models.CharField(max_length=1000)
    # Хранение изображения в виде строки (например, Base64)
    image_data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Изображение пользователя {self.user.username} от {self.created_at}"
