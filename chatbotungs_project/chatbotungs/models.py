# models.py
from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo_electronico = models.EmailField()
    imagen = models.ImageField(upload_to='./img/usuarios_registrados')

class BotResponseFeedback(models.Model):
    user_question = models.TextField()
    bot_response = models.TextField()
    likes = models.IntegerField(default=0)
    liked = models.BooleanField(default=False)




    