from nltk.chat.util import Chat, reflections
reflecciones = {
"ir": "fui",
"hola": "hey"
}

respuestas = [
    [
        r"se me ha caido el hosting (.*)",
        ["Sentimos ese fallo, para reiniciarlo, entra en CPANEL y selecciona reiniciar",]
    ],
     [
        r"cuando hay que pagar la factura (.*)",
        ["Hay que pagarla el dia 15 de cada mes por cualquier metodo de pago, o una vez por año si elegiste el servicio anual",]
    ],
    [
        r"(.*) ampliar el servicio",
        ["Para ampliar el servicio, contacta con atención al cliente",]
    ],
    [
        r"disculpa (.*)",
        ["No pasa nada",]
    ],
    [
        r"hola|hey|buenas",
        ["Hola", "Que tal",]
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
        r"finalizar",
        ["Chao","espero haberte ayudado"]
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
            bandera=False
            print("Hasta luego, que ande bien.") 
            exit()

if __name__ == "__main__":
    chatear()

chatear()

