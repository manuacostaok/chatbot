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
from chatbot import chatear,clasificar_intencion  # Importa la función chatear desde script chatbot.py
from .forms import RegistroUsuarioForm
# Función para procesar las imágenes de huellas digitales
from chatbot import process_fingerprint_images
import tempfile

# Reflecciones para NLTK
mis_reflecciones = {
    "ir": "fui",
    "hola": "hey",
}


# Definir el lematizador de NLTK
lemmatizer = WordNetLemmatizer()

#setup array con palabras clave
arrayOneWord = ['hola','hey','buenas','nada','salir','chau','adios','exit','disculpa','perdon']

# Pares de patrones y respuestas
pares = [
    [
        r"(.*)se cayó el servicio(.*)|(.*)mi internet no anda(.*)|(.*)no me anda internet(.*)|(.*)no tengo internet(.*)",
        ["Sentimos ese fallo, puede reiniciar su modem desenchufándolo por unos segundos y dejando que las luces enciendan, estaremos chequeando que nuestro sistema no tenga problemas, si ya reinicio el modem aguarde"]
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
        ["Hay que pagarla el día 15 de cada mes por cualquier método de pago, o una vez por año si elegiste el servicio anual, también puede adherirla al débito automático",]
    ],
    [
        r"(.*)ya reinicie mi modem y sigo sin internet(.*)",
        ["A continuación, digite su número de DNI para poder chequear que todo esté en orden, de no ser así nos estaremos contactando por su teléfono celular para brindarle mejor atención ",]
    ],
    [
        r"(.*)ampliar el servicio",
        ["Para ampliar el servicio contacta con atención al cliente",]
    ],
    [
        r"disculpa|perdon",
        ["Estoy aquí para ayudarte, no para perdonarte",]
    ],
    [
        r"hola|hey|buenas",
        ["Hola, ¿en qué puedo ayudarte?",]
    ],
    [
        r"(.*)que quieres?|(.*)como estas?",
        ["Nada, estoy bien, solo quiero ayudarte, gracias",]
    ],
    [
        r"nada",
        ["No dijiste nada, ¿podrías volver a intentarlo?",]
    ],
    [
        r"(.*)creado?",
        ["Fui creado luego del Big Bang pero mi código fuente fue descubierto en 2024",]
    ],
    [
        r"salir|chau|adios",
        ["Chau, espero haberte ayudado, recuerda que para salir del chat debes escribir 'EXIT'"]
    ],
]



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
    mensaje_alerta = None  # Inicializa el mensaje de alerta como nulo
    
    if request.method == 'POST':
        # Procesar el formulario si se ha enviado
        form = RegistroUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            # Obtener los datos del formulario validados
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo_electronico']
            imagen = form.cleaned_data['imagen']
            
            # Guardar los datos en la base de datos
            usuario = Usuario(nombre=nombre, correo_electronico=correo, imagen=imagen)
            usuario.save()
            
            # Configurar el mensaje de alerta
            mensaje_alerta = "Usuario registrado exitosamente"
    else:
        # Mostrar el formulario en caso de una solicitud GET
        form = RegistroUsuarioForm()
        
    # Pasar el formulario y el mensaje de alerta al contexto de la plantilla
    context = {'form': form, 'mensaje_alerta': mensaje_alerta}
    return render(request, 'registro.html', context)


def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('pagina_inicio')  # Redirige a la página de inicio después de registrar al usuario
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registro_usuario.html', {'form': form})