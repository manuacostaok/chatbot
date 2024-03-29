"""
URL configuration for chatbotungs_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from chatbotungs import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_response/', views.get_response, name='get_response'),
    path('feedback/', views.feedback, name='feedback'),  # Nueva ruta para la retroalimentación
    path('process_fingerprint_images/', views.process_fingerprint_images, name='process_fingerprint_images'),
    path('admin/', admin.site.urls)
]