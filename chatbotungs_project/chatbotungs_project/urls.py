from django.contrib import admin
from django.urls import path
from chatbotungs import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('get_response/', views.get_response, name='get_response'),
    path('feedback/', views.feedback, name='feedback'),  # Ruta para la retroalimentación
    path('process_fingerprint_images_web/', views.process_fingerprint_images_web, name='process_fingerprint_images_web'),  # Corrección de la URL
    path('upload-image/', views.upload_image, name='upload_image'),  # Nueva ruta para la carga de imágenes
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)