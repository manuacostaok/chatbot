from django.contrib import admin
from .models import BotResponseFeedback

admin.site.register(BotResponseFeedback)


from .models import Usuario

# Registrar el modelo Usuario en el panel de administración
admin.site.register(Usuario)