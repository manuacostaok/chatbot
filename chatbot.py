from nltk.chat.util import Chat, reflections
reflecciones = {
"ir": "fui",
"hola": "hey"
}

respuestas = [
    [
        r"se cayó el servicio de hosting (.*)",
        ["Sentimos ese fallo, para reiniciarlo, entra en 'Panel de control' y selecciona 'Reiniciar'",]
    ],
     [
        r"cuando hay que pagar la factura (.*)",
        ["Hay que pagarla el dia 15 de cada mes por cualquier metodo de pago, o una vez por año si elegiste el servicio anual",]
    ],
    [
        r"(.*) ampliar el servicio",
        ["Para ampliar el servicio contacta con atención al cliente",]
    ],
    [
        r"disculpa (.*)",
        ["Estoy aquí para ayudarte, no para perdonarte",]
    ],
    [
        r"hola|hey|buenas",
        ["Hola, en que puedo ayudarte?",]
    ],
    [
        r"que (.*) quieres ?",
        ["Nada, gracias",]
        
    ],
    [
        r"(.*) creado ?",
        ["Fui creado luego del bigbang pero mi codigo fuente fue descubierto en 2024",]
    ],
    [
        r"exit|salir|chau",
        ["Chau,espero haberte ayudado"]
],
]
def chatear():
    bandera=True
    print("Hola, soy el bot de servicio de hosting, mi nombre es Cosme Fulanito. En que puedo ayudarte? Si quieres salir tipee Exit") #mensaje por defecto
    while(bandera==True):
        respuesta_usuario = input()
        respuesta_usuario=respuesta_usuario.lower()
        if(respuesta_usuario!='exit'):        
            chat = Chat(respuestas, reflecciones)
            chat.converse()
        else:
            print("Hasta luego, que ande bien.") 
            bandera=False
            exit()

if __name__ == "__main__":
    chatear()

chatear()

