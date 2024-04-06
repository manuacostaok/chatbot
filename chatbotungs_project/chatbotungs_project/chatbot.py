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
from sklearn.svm import SVC #machinelearn
from sklearn.decomposition import PCA #machinelearn

import nltk
nltk.download('wordnet') # util para lematización y búsqueda de sinónimos.
nltk.download('punkt')  # útil para tareas de tokenización en procesamiento del lenguaje natural.


# Definir el lematizador de NLTK
lemmatizer = WordNetLemmatizer()

# Pares de patrones y respuestas
# Diccionario de preguntas y respuestas
qa_pairs = {
    "Como puedo proteger mi red Wi-Fi": "Puedes proteger tu red Wi-Fi utilizando una contraseña segura y habilitando la encriptación WPA2 o WPA3. También puedes desactivar la difusión del nombre de tu red (SSID) para que no sea visible para otros dispositivos cercanos.",
    "conectarse sin autorización": "Puedes proteger tu red Wi-Fi utilizando una contraseña segura y habilitando la encriptación WPA2 o WPA3. También puedes desactivar la difusión del nombre de tu red (SSID) para que no sea visible para otros dispositivos cercanos.",
    "Mi conexión wifi es más lenta en ciertas habitaciones de mi casa": "Esto podría deberse a una señal Wi-Fi débil en esas áreas. Intenta mover el enrutador a un lugar más central en tu casa o utiliza un extensor de alcance Wi-Fi para mejorar la cobertura en esas áreas.",
    "el wifi esta lenta": "Esto podría deberse a una señal Wi-Fi débil en esas áreas. Intenta mover el enrutador a un lugar más central en tu casa o utiliza un extensor de alcance Wi-Fi para mejorar la cobertura en esas áreas.Si luego no mejora el dispositivo puede tener la antena dañada",
    "mi wifi tiene poco potencia": "Esto podría deberse a una señal Wi-Fi débil en esas áreas. Intenta mover el enrutador a un lugar más central en tu casa o utiliza un extensor de alcance Wi-Fi para mejorar la cobertura en esas áreas. Si luego no mejora el dispositivo puede tener la antena dañada",
    "¿Por qué mi velocidad de internet es más lenta de lo que debería ser según mi plan?": "La velocidad de internet puede verse afectada por varios factores, como la congestión de la red, problemas con el enrutador o cables dañados. Te recomendaría realizar una prueba de velocidad en diferentes momentos del día y, si la velocidad es consistentemente baja, contactar a nuestro servicio de atención al cliente para que podamos investigar más a fondo.",
    "internet lento": "La velocidad de internet puede verse afectada por varios factores, como la congestión de la red, problemas con el enrutador o cables dañados. Te recomendaría realizar una prueba de velocidad en diferentes momentos del día y, si la velocidad es consistentemente baja, contactar a nuestro servicio de atención al cliente para que podamos investigar más a fondo.",
    "la conexión es lenta": "La velocidad de internet puede verse afectada por varios factores, como la congestión de la red, problemas con el enrutador o cables dañados. Te recomendaría realizar una prueba de velocidad en diferentes momentos del día y, si la velocidad es consistentemente baja, contactar a nuestro servicio de atención al cliente para que podamos investigar más a fondo.",
    "bloquear ciertos sitios web en mi red": "Puedes bloquear ciertos sitios web en tu red Wi-Fi utilizando la función de control parental en tu enrutador o utilizando software de filtrado de contenido. Consulta la documentación de tu enrutador para obtener instrucciones específicas.",
    "se cayó el servicio": "Sentimos ese fallo, puede reiniciar su modem desenchufándolo por unos segundos y dejando que las luces enciendan, estaremos chequeando que nuestro sistema no tenga problemas, si ya reinicio el modem aguarde",
    "no funciona el servicio": "Sentimos ese fallo, puede reiniciar su modem desenchufándolo por unos segundos y dejando que las luces enciendan, estaremos chequeando que nuestro sistema no tenga problemas, si ya reinicio el modem aguarde",
    "ya reinicie mi modem y sigo sin internet": "A continuación, digite su número de DNI para poder chequear que todo esté en orden, de no ser así nos estaremos contactando por su teléfono celular para brindarle mejor atención ",
    "como colocar Wi-Fi en mi hogar": "Para colocar Wi-Fi en su hogar contacta con atención al cliente que le indicara un plan adecuado a sus necesidades 0800-555-2323 ",
    "mi plan": "Para conocer las caracteristicas de su plan contacta con atención al cliente 0800-555-2323",
    "mi servicio": "Para conocer el servicio que posee contacta con atención al cliente 0800-555-2323",
    "ampliar el servicio": "Para ampliar el servicio contacta con atención al cliente 0800-555-2323",
    "mejorar plan": "Para ampliar el servicio contacta con atención al cliente 0800-555-2323",
    "atencion al cliente": "Para contactarse con atención al cliente marque 0800-555-2323",
    "pagar la factura":"Hay que pagarla el día 15 de cada mes por cualquier método de pago, o una vez por año si elegiste el servicio anual, también puede adherirla al débito automático",
    "disculpa": "Estoy aquí para ayudarte, no para perdonarte",
    "perdon": "Estoy aquí para ayudarte, no para perdonarte",
    "hola": "Hola, ¿en qué puedo ayudarte?",
    "hey": "Hola, ¿en qué puedo ayudarte?",
    "buenas": "Hola, ¿en qué puedo ayudarte?",
    "que onda": "Hola, ¿en qué puedo ayudarte?",
    "que quieres?": "Nada, estoy bien, solo quiero ayudarte, gracias",
    "como estas?": "Nada, estoy bien, solo quiero ayudarte, gracias",
    "nada": "No dijiste nada, ¿podrías volver a intentarlo?",
    "cuando fuiste creado?": "Fui creado luego del Big Bang pero mi código fuente fue descubierto en 2024",
    "salir": "Chau, espero haberte ayudado, recuerda que para salir del chat debes escribir 'EXIT'",
    "chau": "Chau, espero haberte ayudado, recuerda que para salir del chat debes escribir 'EXIT'",
    "adios": "Chau, espero haberte ayudado, recuerda que para salir del chat debes escribir 'EXIT'",
    "exit": "Chau, espero haberte ayudado, recuerda que para salir del chat debes escribir 'EXIT'"
}

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
    print("Forma de local_image_gray:", local_image_gray.shape)  # Agregar este print para verificar la forma
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
    
#En este ejemplo, primero usamos PCA para reducir la dimensionalidad de las imágenes de huellas digitales y la imagen local. 
#    Luego, entrenamos un clasificador SVM con las características extraídas de la imagen local.
#     Finalmente, utilizamos el clasificador para predecir si la huella digital es similar o diferente a la imagen local.

def preprocess_text(sentence):
    # Tokenización y lematización
    print('sentence')
    print(sentence)    
    tokens = word_tokenize(sentence)
    print('tokens')
    print(tokens)
    lemmatized_tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens ]
    print('lemmatized_tokens')
    print(lemmatized_tokens)
    return " ".join(lemmatized_tokens)

# Crear un vectorizador TF-IDF para clasificación de intenciones
vectorizer = TfidfVectorizer(preprocessor=preprocess_text) # Se indica que funcion preprocesador se va a utilizar
preguntas = list(qa_pairs.keys())
preguntas_vect = vectorizer.fit_transform(preguntas)

# Las Etiquetas de las intenciones son esenciales para que el clasificador pueda aprender 
# la relación entre las características de entrada (las preguntas del usuario) 
# y las clases a las que pertenecen (las respuestas correspondientes).
etiquetas = [idx for idx in range(len(qa_pairs))] 

# Entrenar un clasificador SVM para clasificar la intención del usuario
clasificador = SVC(kernel='linear')
clasificador.fit(preguntas_vect, etiquetas) # Se realiza la clasificacion con la relacion entre preguntas y etiquetas

# Función para clasificar la intención del usuario
def clasificar_intencion(respuesta_usuario):
    respuesta_usuario = preprocess_text(respuesta_usuario)  
    respuesta_usuario_vect = vectorizer.transform([respuesta_usuario])
    return clasificador.predict(respuesta_usuario_vect)[0] 

# Función para generar respuestas
def generar_respuesta(intencion):
    return list(qa_pairs.values())[intencion]

# Función para chatear con el usuario
def chatear(respuesta_usuario):     
    if respuesta_usuario.strip():  # Verificar si la entrada tiene sentido 
        intencion = clasificar_intencion(respuesta_usuario) #devuelve la etiqueta con la intencion mas cercana
        respuesta_bot = generar_respuesta(intencion) #devuelve la respuesta mas cercana que debe dar el 
    else: # Verificar si la entrada no está vacía
        respuesta_bot = "No dijiste nada, ¿podrías volver a intentarlo?"

    return respuesta_bot if respuesta_bot else "Lo siento, ha ocurrido un error inesperado."

