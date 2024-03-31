import re
import os  
import io  
from skimage import color, io as skio, img_as_ubyte
from skimage.metrics import structural_similarity as ssim
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Importar las reflecciones y el chat de NLTK
from nltk.chat.util import reflections

import nltk
nltk.download('wordnet')
nltk.download('punkt')

# Reflecciones para NLTK
mis_reflecciones = {
    "ir": "fui",
    "hola": "hey",
}

# Definir el lematizador de NLTK
lemmatizer = WordNetLemmatizer()

#setup array con palabras clave
arrayOneWord = ['hola','hey','buenas','nada','salir','chau','adios','exit']
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
        r"disculpa(.*)",
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

# Función para preprocesar el texto del usuario
def preprocess_text(sentence):
    # Tokenización
    tokens = word_tokenize(sentence)
    # Lematización
    lemmatized_tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]
    return " ".join(lemmatized_tokens)

# Crear un vectorizador TF-IDF para clasificación de intenciones
vectorizer = TfidfVectorizer(preprocessor=preprocess_text)
preguntas = [pair[0] for pair in pares]
preguntas_vect = vectorizer.fit_transform(preguntas)

# Función para clasificar la intención del usuario usando scikit-learn
def clasificar_intencion(respuesta_usuario):
    respuesta_usuario = preprocess_text(respuesta_usuario)
    respuesta_usuario_vect = vectorizer.transform([respuesta_usuario])
    similitud = cosine_similarity(respuesta_usuario_vect, preguntas_vect)
    idx = similitud.argmax()
    return pares[idx][1][0]

# Función para procesar las imágenes de huellas digitales
def process_fingerprint_images(image_path):
    # Ruta de la imagen local
    local_image_path = os.path.join('staticfiles', 'img', 'huella_registrada', 'imagen_local.tif')
    
    print("Cargando la imagen local...")
    try:
        # Cargar la imagen local para comparar
        local_image = skio.imread(local_image_path)
        # Convertir a RGB si es necesario
        if local_image.ndim != 3 or local_image.shape[2] != 3:
            local_image = color.gray2rgb(local_image)
        print("Imagen local cargada correctamente.")
    except Exception as e:
        # Si ocurre algún error al cargar la imagen local
        print("Error al cargar la imagen local:", e)
        return {'error': 'Error al cargar la imagen local.'}
    
    print("Cargando la imagen de huella digital...")
    try:
        # Cargar la imagen de huella digital para comparar
        fingerprint_image = skio.imread(image_path)
        # Convertir a RGB si es necesario
        if fingerprint_image.ndim != 3 or fingerprint_image.shape[2] != 3:
            fingerprint_image = color.gray2rgb(fingerprint_image)
        print("Imagen de huella digital cargada correctamente.")
    except Exception as e:
        # Si ocurre algún error al cargar la imagen de huella digital
        print("Error al cargar la imagen de huella digital:", e)
        return {'error': 'Error al cargar la imagen de huella digital.'}
    
    # Convertir ambas imágenes a escala de grises
    local_image_gray = color.rgb2gray(local_image)
    fingerprint_image_gray = color.rgb2gray(fingerprint_image)
    print("Imágenes convertidas a escala de grises.")
    
    # Calcular el índice de similitud estructural (SSIM) entre las imágenes
    try:
        similarity_index = ssim(local_image_gray, fingerprint_image_gray, data_range=1.0)
        print("Índice de similitud estructural calculado:", similarity_index)
    except Exception as e:
        print("Error al calcular el índice de similitud estructural:", e)
        return {'error': 'Error al calcular el índice de similitud estructural.'}
    
    # Definir un umbral de similitud
    threshold = 0.95  # Umbral de similitud del 95%
    
    # Comparar el índice de similitud con el umbral
    if similarity_index >= threshold:
        # Si la similitud es alta, las imágenes son consideradas iguales
        print("La huella digital es similar a la imagen local.")
        return {'message': 'La huella digital es similar a la imagen local.'}
    else:
        # Si la similitud es baja, las imágenes son diferentes
        print("La huella digital es diferente a la imagen local.")
        return {'message': 'La huella digital es diferente a la imagen local.'}

# Función para chatear con el usuario
def chatear(respuesta_usuario):
    if respuesta_usuario.lower() == 'exit':
        respuesta_bot = "exit"
    elif respuesta_usuario.strip():  # Verificar si la entrada tiene sentido
        if len(respuesta_usuario.split()) == 1 and respuesta_usuario not in arrayOneWord :  # Verificar si la entrada tiene solo una palabra
            respuesta_bot = "Lo siento, no logro comprender la pregunta. Por favor, intenta proporcionar más detalles."
        elif "login huella" in respuesta_usuario.lower():
            # Llamar a la función process_fingerprint_images con la ruta del archivo de huella digital
            respuesta_bot = process_fingerprint_images('./staticfiles/img/huellas_dataset/101_2.tif')
            print("Bot:", respuesta_bot)  # Imprimir la respuesta del bot
        else:
            respuesta_bot = clasificar_intencion(respuesta_usuario)
    else: # Verificar si la entrada no está vacía
        respuesta_bot = "No dijiste nada, ¿podrías volver a intentarlo?"

    return respuesta_bot if respuesta_bot else "Lo siento, ha ocurrido un error inesperado."

# Iniciar el chat
if __name__ == "__main__":
    while True:  # Bucle infinito para mantener la conversación
        respuesta_usuario = input("Usuario: ")  # Obtener la respuesta del usuario
        respuesta_bot = chatear(respuesta_usuario)  # Llamar a la función chatear con la respuesta del usuario como argumento
        
        if isinstance(respuesta_bot, dict):
            # Si la respuesta es un diccionario, imprimir el mensaje de error
            print(respuesta_bot.get('error', 'Error desconocido de la funcion main.'))
        elif respuesta_bot.lower() == "exit":
            # Si la respuesta del bot es "exit", salir del bucle
            print("¡Hasta luego!")
            break
        else:
            # Imprimir la respuesta del bot
            print("Bot:", respuesta_bot)
        