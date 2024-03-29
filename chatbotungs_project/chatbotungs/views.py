
from django.shortcuts import render
from nltk.chat.util import Chat, reflections
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from chatbot import chatear  # Importa la función chatear desde script chatbot.py
from .models import BotResponseFeedback
import json


import os
from skimage import io, img_as_ubyte
import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage import color,io, img_as_ubyte

# Definir los pares de conversación y reflecciones
mis_reflecciones = {
    "ir": "fui",
    "hola": "hey"
}

pares = [
    [
        r"(.*)se cayó el servicio(.*)|(.*)internet no anda(.*)|(.*)no me anda internet(.*)|(.*)no tengo internet(.*)|(.*)internet anda mal(.*)|(.*)me anda mal internet(.*)",
        ["Sentimos ese fallo, puede reiniciar su modem desenchufándolo por unos segundos y dejando que las luces enciendan, estaremos chequeando que nuestro sistema no tenga problemas. Si ya reinició el modem, espere por favor."]
    ],
    [
       r"(.*)Como puedo proteger mi red Wi-Fi(.*)|(.*)conectarse sin autorización?" ,
       ["Puedes proteger tu red Wi-Fi utilizando una contraseña segura y habilitando la encriptación WPA2 o WPA3. También puedes desactivar la difusión del nombre de tu red (SSID) para que no sea visible para otros dispositivos cercanos."]
    ],
    [
        r"(.*)Mi conexión a internet es más lenta en ciertas habitaciones de mi casa(.*)",
        ["Esto podría deberse a una señal Wi-Fi débil en esas áreas. Intenta mover el enrutador a un lugar más central en tu casa o utiliza un extensor de alcance Wi-Fi para mejorar la cobertura en esas áreas."]
    ],
    [
        r"¿Por qué mi velocidad de internet es más lenta de lo que debería ser según mi plan?|(.*)internet lento(.*)",
        ["La velocidad de internet puede verse afectada por varios factores, como la congestión de la red, problemas con el enrutador o cables dañados. Te recomendaría realizar una prueba de velocidad en diferentes momentos del día y, si la velocidad es consistentemente baja, contactar a nuestro servicio de atención al cliente para que podamos investigar más a fondo."]
    ],
    [
        r"(.*)bloquear ciertos sitios web en mi red(.*)",
        ["Puedes bloquear ciertos sitios web en tu red Wi-Fi utilizando la función de control parental en tu enrutador o utilizando software de filtrado de contenido. Consulta la documentación de tu enrutador para obtener instrucciones específicas."]
    ],
    [
        r"(.*)cuando hay que pagar la factura(.*)",
        ["Hay que pagarla el día 15 de cada mes por cualquier método de pago, o una vez por año si elegiste el servicio anual. También puedes adherirla al débito automático."]
    ],
    [
        r"(.*)ya reinicie mi modem y sigo sin internet(.*)",
        ["A continuación, ingrese su número de DNI para poder chequear que todo esté en orden. De no ser así, nos pondremos en contacto por su teléfono celular para brindarle una mejor atención."]
    ],
    [
        r"(.*)ampliar el servicio",
        ["Para ampliar el servicio, contacta con atención al cliente."]
    ],
    [
        r"disculpa(.*)",
        ["Estoy aquí para ayudarte, no para perdonarte."]
    ],
    [
        r"hola|hey|buenas",
        ["Hola, ¿en qué puedo ayudarte?"]
    ],
    [
        r"(.*)que quieres?|(.*)como estas?",
        ["Nada, estoy bien, solo quiero ayudarte. Gracias."]
    ],
    [
        r"nada",
        ["No dijiste nada. ¿Podrías volver a intentarlo?"]
    ],
    [
        r"(.*)creado?",
        ["Fui creado luego del Big Bang, pero mi código fuente fue descubierto en 2024."]
    ],
    [
        r"salir|chau|adios",
        ["Chau, espero haberte ayudado. Recuerda que para salir del chat debes escribir 'EXIT'."]
    ],
]

# Inicializar el chat con los pares y reflecciones
chat = Chat(pares, mis_reflecciones)

@ensure_csrf_cookie
def index(request):
    return render(request, 'chatbotungs/index.html')


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
                return JsonResponse({'error': 'El mensaje del usuario está vacío'})
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
def process_fingerprint_images(request):
    if request.method == 'POST':
        try:
            # Obtener la imagen de la solicitud
            image = request.FILES['image']

            # Imprimir o registrar la ruta completa de la imagen local
            local_image_path = os.path.join('staticfiles', 'img', 'huellas', 'imagen_local.tif')
            print("Ruta de la imagen local:", local_image_path)

            # Cargar la imagen local para comparar
            local_image = io.imread(local_image_path)
            print("Ruta de la imagen local:", local_image)
            # Convertir las imágenes a escala de grises
            image_gray = img_as_ubyte(color.rgb2gray(io.imread(image)))
            local_image_gray = img_as_ubyte(color.rgb2gray(local_image))

            # Imprimir o registrar las dimensiones de las imágenes para verificar que sean consistentes
            print("Dimensiones de la imagen recibida:", image_gray.shape)
            print("Dimensiones de la imagen local:", local_image_gray.shape)

            # Calcular el índice de similitud estructural (SSIM) entre las imágenes
            similarity_index = ssim(image_gray, local_image_gray)

            # Definir un umbral de similitud
            threshold = 0.95  # Umbral de similitud del 95%

            # Comparar el índice de similitud con el umbral
            if similarity_index >= threshold:
                # Si la similitud es alta, las imágenes son consideradas iguales
                return JsonResponse({'message': 'La imagen recibida es igual a la imagen local.'})
            else:
                # Si la similitud es baja, las imágenes son diferentes
                return JsonResponse({'message': 'La imagen recibida es diferente a la imagen local.'})
        except Exception as e:
            # Si ocurre algún error, devolver una respuesta de error
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # Si la solicitud no es POST, devolver un error de método no permitido
        return JsonResponse({'error': 'Método no permitido'}, status=405)