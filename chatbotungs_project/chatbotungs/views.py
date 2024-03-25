from django.shortcuts import render
from django.http import JsonResponse
from nltk.chat.util import Chat, reflections

# Definir los pares de conversación y reflecciones
mis_reflecciones = {
    "ir": "fui",
    "hola": "hey",
    " ": "nada",
    "": "nada"
}

pares = [
    [
        r"(.*)se cayó el servicio(.*)|(.*)mi internet no anda(.*)|(.*)no me anda internet(.*)|(.*)no tengo internet(.*)",
        ["Sentimos ese fallo, puede reiniciar su modem desenchufandolo por unos segundos y dejando que las luces enciendan, estaremos checkeando que nuestro sistema no tenga problemas, si ya reinicio el modem aguarde"]
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
        ["Hay que pagarla el dia 15 de cada mes por cualquier método de pago, o una vez por año si elegiste el servicio anual, también puede adherirla al debito automático",]
    ],
    [
        r"(.*)ya reinicie mi modem y sigo sin internet(.*)",
        ["A continuacion, digite su numero de dni para poder chequear que todo esté en orden, de no ser así nos estaremos contactado por su telefono celular para brindarle mejor atención ",]
    ],
    [
        r"(.*)ampliar el servicio",
        ["Para ampliar el servicio contacta con atención al cliente",]
    ],
    [
        r"disculpa(.*)",
        ["Estoy aquí para ayudarte, no para perdonarte",]
    ],
    [
        r"hola|hey|buenas",
        ["Hola, en que puedo ayudarte?",]
    ],
    [
        r"(.*)que quieres?|(.*)como estas?",
        ["Nada, estoy bien, solo quiero ayudarte, gracias",]
    ],
    [
        r"nada",
        ["No dijiste nada podrias volver a intentar",]
    ],
    [
        r"(.*)creado?",
        ["Fui creado luego del bigbang pero mi codigo fuente fue descubierto en 2024",]
    ],
    [
        r"exit|salir|chau|adios",
        ["Chau,espero haberte ayudado"]
],
]
# Inicializar el chat con los pares y reflecciones
chat = Chat(pares, mis_reflecciones)

def index(request):
    return render(request, 'chatbotungs/index.html')

def get_response(request):
    try:
        if request.method == 'POST':
            user_message = request.POST.get('message')
            if not user_message.strip():
                bot_response = "No dijiste nada. ¿Podrías volver a intentarlo?"
            else:
                bot_response = chat.respond(user_message)
            return JsonResponse({'response': bot_response})
        else:
            return JsonResponse({'error': 'No se recibió una solicitud POST'})
    except Exception as e:
        return JsonResponse({'error': str(e)})