from nltk.chat.util import Chat, reflections
mis_reflecciones = {
"ir": "fui",
"hola": "hey"
}

pares = [
    [
        r"se cayó el servicio de internet (.*)|mi internet no anda(.*)|no me anda internet(.*)|no tengo internet|(.*)",
        ["Sentimos ese fallo, puede reiniciar su modem desenchufandolo por unos segundos y dejando que las luces enciendan, estaremos checkeando que nuestro sistema no tenga problemas, si ya reinicio el modem aguarde"]
    ],
    [
        r"cuando hay que pagar la factura (.*)",
        ["Hay que pagarla el dia 15 de cada mes por cualquier método de pago, o una vez por año si elegiste el servicio anual, también puede adherirla al debito automático",]
    ],
    [
        r"ya reinicie mi modem y sigo sin internet (.*)",
        ["A continuacion, digite su numero de dni para poder chequear que todo esté en orden, de no ser así nos estaremos contactado por su telefono celular para brindarle mejor atención ",]
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
    print("Hola, soy el bot de servicio de hosting, mi nombre es Cosme Fulanito. En que puedo ayudarte? Si quieres salir escriba Exit") #mensaje por defecto
    while(bandera==True):
        respuesta_usuario = input()
        respuesta_usuario=respuesta_usuario.lower()
        if(respuesta_usuario!='exit'):        
            chat = Chat(pares, mis_reflecciones)
            chat.converse()
        else:
            print("Hasta luego, espero haberte ayudado, saludos.") 
            bandera=False
            exit()

if __name__ == "__main__":
    chatear()

chatear()

