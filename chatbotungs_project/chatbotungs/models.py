# models.py
from django.db import models

class BotResponseFeedback(models.Model):
    user_question = models.TextField()
    bot_response = models.TextField()
    likes = models.IntegerField(default=0)
    liked = models.BooleanField(default=False)


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo_electronico = models.EmailField(unique=True)
    imagen = models.ImageField(upload_to='imagenes_usuarios')

    