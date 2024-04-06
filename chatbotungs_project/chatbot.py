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
    "proteger red Wi-Fi": "Puedes proteger tu red Wi-Fi utilizando una contraseña segura y habilitando la encriptación WPA2 o WPA3. También puedes desactivar la difusión del nombre de tu red (SSID) para que no sea visible para otros dispositivos cercanos.",
    "el horario de atencion": "el horario de atencion es de 9 a 18 hs en el local Juan María Gutiérrez 1150",
    "contratar un servicio proxy": "Ya registre su pedido, el personal de atencion al cliente se estará comunicando a la brevedad.",
    "contratar un servicio vpn": "Ya registre su pedido, el personal de atencion al cliente se estará comunicando a la brevedad.",
    "wifi lenta en ciertas habitaciones": "Esto podría deberse a una señal Wi-Fi débil en esas áreas. Intenta mover el enrutador a un lugar más central en tu casa o utiliza un extensor de alcance Wi-Fi para mejorar la cobertura en esas áreas.",
    "wifi lento ": "Esto podría deberse a una señal Wi-Fi débil en esas áreas. Intenta mover el enrutador a un lugar más central en tu casa o utiliza un extensor de alcance Wi-Fi para mejorar la cobertura en esas áreas.Si luego no mejora el dispositivo puede tener la antena dañada",
    " wifi tiene poco potencia": "Esto podría deberse a una señal Wi-Fi débil en esas áreas. Intenta mover el enrutador a un lugar más central en tu casa o utiliza un extensor de alcance Wi-Fi para mejorar la cobertura en esas áreas. Si luego no mejora el dispositivo puede tener la antena dañada",
    "tengo fallas tecnicas": "Voy a informar al servicio tecnico para que se esten comunicando para solucionarle el problema.",
    "¿la velocidad de internet es más lenta de lo que debería ser el plan?": "La velocidad de internet puede verse afectada por varios factores, como la congestión de la red, problemas con el enrutador o cables dañados. Te recomendaría realizar una prueba de velocidad en diferentes momentos del día y, si la velocidad es consistentemente baja, contactar a nuestro servicio de atención al cliente para que podamos investigar más a fondo.",
    "internet lento": "La velocidad de internet puede verse afectada por varios factores, como la congestión de la red, problemas con el enrutador o cables dañados. Te recomendaría realizar una prueba de velocidad en diferentes momentos del día y, si la velocidad es consistentemente baja, contactar a nuestro servicio de atención al cliente para que podamos investigar más a fondo.",
    "la conexión es lenta": "La velocidad de internet puede verse afectada por varios factores, como la congestión de la red, problemas con el enrutador o cables dañados. Te recomendaría realizar una prueba de velocidad en diferentes momentos del día y, si la velocidad es consistentemente baja, contactar a nuestro servicio de atención al cliente para que podamos investigar más a fondo.",
    "bloquear ciertos sitios web en mi red": "Puedes bloquear ciertos sitios web en tu red Wi-Fi utilizando la función de control parental en tu enrutador o utilizando software de filtrado de contenido. Consulta la documentación de tu enrutador para obtener instrucciones específicas.",
    "se cayó el servicio": "Sentimos ese fallo, puede reiniciar su modem desenchufándolo por unos segundos y dejando que las luces enciendan, estaremos chequeando que nuestro sistema no tenga problemas, si ya reinicio el modem aguarde",
    "internet fallando": "Sentimos ese fallo, puede reiniciar su modem desenchufándolo por unos segundos y dejando que las luces enciendan, estaremos chequeando que nuestro sistema no tenga problemas, si ya reinicio el modem aguarde",
    "no funciona el servicio": "Sentimos ese fallo, puede reiniciar su modem desenchufándolo por unos segundos y dejando que las luces enciendan, estaremos chequeando que nuestro sistema no tenga problemas, si ya reinicio el modem aguarde",
    "ya reinicie mi modem y sigo sin internet": "A continuación, indique su domicilio para poder chequear que todo esté en orden, de no ser así nos estaremos contactando por su teléfono celular para brindarle mejor atención ",
    "colocar Wi-Fi en hogar": "Para colocar Wi-Fi en su hogar contacta con atención al cliente que le indicara un plan adecuado a sus necesidades 0800-555-2323 ",
    "mi plan": "Para conocer las caracteristicas de su plan contacta con atención al cliente 0800-555-2323",
    "mi servicio": "Para conocer el servicio que posee contacta con atención al cliente 0800-555-2323",
    "ampliar el servicio": "Para ampliar el servicio contacta con atención al cliente 0800-555-2323",
    "mejorar plan": "Para ampliar el servicio contacta con atención al cliente 0800-555-2323",
    "soporte tecnico": "Para contactarse con soporte tecnico marque 0800-555-2020",
    "atencion al cliente": "Para contactarse con atención al cliente marque 0800-555-2323",
    "pagar la factura":"Hay que pagarla el día 15 de cada mes por cualquier método de pago, o una vez por año si elegiste el servicio anual, también puede adherirla al débito automático",
    "disculpa": "Estoy aquí para ayudarte, no para perdonarte",
    "perdon": "Estoy aquí para ayudarte, no para perdonarte",
    "hola": "Hola, ¿en qué puedo ayudarte?",
    "hey": "Hola, ¿en qué puedo ayudarte?",
    "buenas": "Hola, ¿en qué puedo ayudarte?",
    "que onda": "Hola, ¿en qué puedo ayudarte?",
    "que quieres?": "Nada, estoy bien, solo quiero ayudarte, gracias",
    "gracias":" Por nada estoy para ayudarte.",
    "como estas?": "Nada, estoy bien, solo quiero ayudarte, gracias",
    "nada": "No dijiste nada, ¿podrías volver a intentarlo?",
    "cuando fuiste creado?": "Fui creado luego del Big Bang pero mi código fuente fue descubierto en 2024",    
    "adios": "Chau, espero haberte ayudado, recuerda que para salir del chat debes escribir 'EXIT'",
    "chau": "Chau, espero haberte ayudado, recuerda que para salir del chat debes escribir 'EXIT'",
    "Juan María Gutiérrez 1150":" Gracias, hemos detectado fallas tecnicas por la zona que menciona. Informare a servicio tecnico para que se esten comunicando.",    
}
arrayOneWord = ['hola','hey','buenas','nada','salir','chau','adios','exit','perdon','disculpa','gracias']

def process_fingerprint_images(image_path):
    # Ruta del directorio de huellas registradas
    registered_images_directory = os.path.join('staticfiles', 'img', 'huella_registrada')
    
    # Cargar la imagen de huella digital para comparar
    print("Cargando la imagen de huella digital...")
    try:
        fingerprint_image = skio.imread(image_path)
        if fingerprint_image.ndim != 3 or fingerprint_image.shape[2] != 3:
            fingerprint_image = color.gray2rgb(fingerprint_image)
        print("Imagen de huella digital cargada correctamente.")
    except Exception as e:
        print("Error al cargar la imagen de huella digital:", e)
        return {'error': 'Error al cargar la imagen de huella digital.'}
    
    # Convertir la imagen de huella digital a escala de grises
    fingerprint_image_gray = color.rgb2gray(fingerprint_image)
    
    # Definir un umbral de similitud
    threshold = 0.95  # Umbral de similitud del 95%
    
    # Iterar sobre los archivos en el directorio de huellas registradas
    for filename in os.listdir(registered_images_directory):
        # Ignorar archivos que no son imágenes
        if not filename.endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff')):
            continue
        
        # Construir la ruta completa del archivo de huella registrada
        registered_image_path = os.path.join(registered_images_directory, filename)
        
        # Cargar la imagen de huella registrada
        print(f"Cargando la imagen de huella registrada: {filename}...")
        try:
            registered_image = skio.imread(registered_image_path)
            if registered_image.ndim != 3 or registered_image.shape[2] != 3:
                registered_image = color.gray2rgb(registered_image)
            print(f"Imagen de huella registrada '{filename}' cargada correctamente.")
        except Exception as e:
            print(f"Error al cargar la imagen de huella registrada '{filename}':", e)
            continue
        
        # Convertir la imagen de huella registrada a escala de grises
        registered_image_gray = color.rgb2gray(registered_image)
        
        # Calcular el índice de similitud estructural (SSIM) entre las imágenes
        try:
            similarity_index = ssim(registered_image_gray, fingerprint_image_gray, data_range=1.0)
            print(f"Índice de similitud estructural entre '{filename}' y la imagen de huella digital:", similarity_index)
        except Exception as e:
            print(f"Error al calcular el índice de similitud estructural entre '{filename}' y la imagen de huella digital:", e)
            continue
        
        # Comparar el índice de similitud con el umbral
        if similarity_index >= threshold:
            # Si la similitud es alta, las imágenes son consideradas iguales
            print(f"La huella digital es similar a la imagen registrada: {filename}")
            return {'message': f"La huella digital es similar a la imagen registrada: {filename}"}
    
    # Si ninguna imagen registrada coincide con la huella digital
    print("La huella digital no coincide con ninguna imagen registrada.")
    return {'message': 'La huella digital no coincide con ninguna imagen registrada.'}
    
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

# Entrenar un clasificador SVM lineal
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

#Función para chatear con el usuario
def chatear(respuesta_usuario):   
    if respuesta_usuario.lower() == 'exit':
         respuesta_bot = "exit"            
    elif respuesta_usuario.strip():  # Verificar si la entrada tiene sentido         
        if len(respuesta_usuario.split())>1 or respuesta_usuario.lower() in arrayOneWord: # Verificar si la entrada tiene sentido
            intencion = clasificar_intencion(respuesta_usuario) #devuelve la etiqueta con la intencion mas cercana
            respuesta_bot = generar_respuesta(intencion) #devuelve la respuesta mas cercana que debe dar el
        else:     
            respuesta_bot = "Lo siento, no logro comprender la pregunta. Por favor, intenta proporcionar más detalles."
    return respuesta_bot if respuesta_bot else "Lo siento, ha ocurrido un error inesperado."


