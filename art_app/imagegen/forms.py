from django import forms

class ImageGenerationForm(forms.Form):
    prompt = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(attrs={'placeholder': 'Введите описание для генерации изображения'}),
        label='Промпт для генерации'
    )
