# models.py
from django.db import models

class BotResponseFeedback(models.Model):
    user_question = models.TextField()
    bot_response = models.TextField()
    likes = models.IntegerField(default=0)
    liked = models.BooleanField(default=False)