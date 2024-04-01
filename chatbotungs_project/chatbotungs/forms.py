from django import forms
from .models import Usuario

class RegistroUsuarioForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    correo_electronico = forms.EmailField()
    imagen = forms.ImageField()