from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
# Importar las librerías necesarias
import re
import os
import io
import json
from skimage import color, io as skio, img_as_ubyte
from skimage.metrics import structural_similarity as ssim
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from .models import BotResponseFeedback
from .models import Usuario
from chatbot import chatear,clasificar_intencion  # Importa las funciónes desde chatbot.py
from chatbot import process_fingerprint_images
from .forms import RegistroUsuarioForm
# Función para procesar las imágenes de huellas digitales

import tempfile

#import para la carga de img
from PIL import Image
from django.conf import settings



@ensure_csrf_cookie
def index(request):
    # Consulta para obtener todas las respuestas del bot con sus likes
    bot_responses = BotResponseFeedback.objects.all()

    # Pasar los datos al contexto de la plantilla
    context = {
        'bot_responses': bot_responses,
    }

    # Renderizar la plantilla con el contexto
    return render(request, 'chatbotungs/index.html', context)

@csrf_exempt
def get_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            if user_message:
                bot_response = chatear(user_message)  # Obtiene la respuesta del bot
                return JsonResponse({'response': bot_response})  # Devuelve la respuesta como JSON
            else:
                return JsonResponse({'error': '"No dijiste nada, ¿podrías volver a intentarlo?"'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Método no permitido'})
    
def view_likes(request):
    responses_with_likes = BotResponseFeedback.objects.all()
    return render(request, 'view_likes.html', {'responses_with_likes': responses_with_likes})


def feedback(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_question = data.get('user_question')
        bot_response = data.get('bot_response')
        liked = data.get('liked', False)  # Obtener el valor de "liked" del cuerpo de la solicitud
        if user_question and bot_response:
            feedback_instance = BotResponseFeedback.objects.create(
                user_question=user_question,
                bot_response=bot_response,
                liked=liked  # Guardar el valor de "liked"
            )
            return JsonResponse({'message': 'Feedback received successfully.'})
        else:
            return JsonResponse({'error': 'Invalid data provided.'})
    else:
        return JsonResponse({'error': 'Invalid request method.'})
    
def feedback_like(request, response_id):
    # Obtener la instancia de BotResponseFeedback asociada al ID response_id
    response = get_object_or_404(BotResponseFeedback, pk=response_id)

    # Incrementar el contador de likes
    response.likes += 1
    response.save()

    # Devolver una respuesta JSON indicando que el "me gusta" fue registrado correctamente
    return JsonResponse({'message': 'Like registrado correctamente.'})
@csrf_exempt
def process_fingerprint_images_web(request):
    if request.method == 'POST':
        try:
            # Obtener el archivo de la solicitud
            image_file = request.FILES.get('image')

            if image_file:
                # Crear un archivo temporal para almacenar la imagen
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    # Escribir el contenido del archivo de imagen en el archivo temporal
                    for chunk in image_file.chunks():
                        temp_file.write(chunk)
                
                # Procesar el archivo temporal de la huella digital utilizando la función adecuada
                result = process_fingerprint_images(temp_file.name)  # Pasar el nombre del archivo
                
                # Eliminar el archivo temporal después de procesarlo
                os.unlink(temp_file.name)

                # Devolver la respuesta de la función como JSON utilizando JsonResponse
                return JsonResponse(result)
            else:
                return JsonResponse({'error': 'No se proporcionó ningún archivo de imagen'}, status=400)
        except Exception as e:
            error_response = {'error': str(e)}
            return JsonResponse(error_response, status=500)
    else:
        # Si la solicitud no es POST, devolver un error de método no permitido
        return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista principal para el chatbot
def chatbot_view(request):
    if request.method == 'POST':
        try:
            # Obtener la respuesta del usuario de la solicitud
            respuesta_usuario = request.POST.get('user_input', '')
            respuesta_bot = ''  # Inicializar la respuesta del bot

            if respuesta_usuario.lower() == 'exit':
                respuesta_bot = "exit"
            elif respuesta_usuario.strip():
                if len(respuesta_usuario.split()) == 1 and respuesta_usuario not in arrayOneWord:
                    respuesta_bot = "Lo siento, no logro comprender la pregunta. Por favor, intenta proporcionar más detalles."
                elif "login huella" in respuesta_usuario.lower():
                    # Llamar a la función process_fingerprint_images con la ruta del archivo de huella digital
                    respuesta_bot = process_fingerprint_images(request)
                else:
                    respuesta_bot = clasificar_intencion(respuesta_usuario)
            else:
                respuesta_bot = "No dijiste nada, ¿podrías volver a intentarlo?"

            return JsonResponse({'response': respuesta_bot})
        except Exception as e:
            # Manejar errores
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return render(request, 'chatbot.html')

def vista_registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo_electronico']
            imagen = form.cleaned_data['imagen']
            
            usuario = Usuario(nombre=nombre, correo_electronico=correo, imagen=imagen)
            usuario.save()
            
            return JsonResponse({'success': True, 'mensaje_alerta': 'Usuario registrado exitosamente'})
        else:
            errors = dict(form.errors)
            return JsonResponse({'success': False, 'errors': errors})
    else:
        form = RegistroUsuarioForm()
        
    context = {'form': form}
    return render(request, 'registro.html', context)


#funcion para la carga de imagenes que convierte a tif y lo guarda en nuestro proyecto
def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        uploaded_image = request.FILES['image']
        image_name = uploaded_image.name
        image_format = os.path.splitext(image_name)[1].lower()
        
        # Verifica si la extensión del archivo es válida
        if image_format not in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            return JsonResponse({'error': 'El formato de la imagen no es compatible'})
        
        # Guarda la imagen en el sistema de archivos en el directorio staticfiles/img/
        image_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'img','huella_registrada', image_name)
        with open(image_path, 'wb+') as destination:
            for chunk in uploaded_image.chunks():
                destination.write(chunk)
        
        # Convierte la imagen al formato deseado si es necesario
        if image_format not in ['.tif', '.tiff']:
            image = Image.open(image_path)
            tif_image_path = os.path.splitext(image_path)[0] + '.tif'
            image.save(tif_image_path)
        
        # Si necesitas almacenar la ubicación de la imagen en tu base de datos, hazlo aquí
        
        return JsonResponse({'message': 'Imagen subida exitosamente'})
    else:
        return JsonResponse({'error': 'Método no permitido'})