// Obtener referencia al contenedor del chat y al cuadro de mensajes
var chatBox = document.getElementById("chat-box");

// Función para enviar un mensaje y recibir una respuesta del servidor
function sendMessage() {
    var userInput = document.getElementById("user-input").value;
    chatBox.innerHTML += "<p><strong>Tú:</strong> " + userInput + "</p>";

    fetch('/get_response/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ message: userInput })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.log(data.error);  // Imprime el error en la consola
                // Maneja el error aquí, por ejemplo, mostrando un mensaje de advertencia
                chatBox.innerHTML += "<p><strong>Bot:</strong> " + data.error + "</p>";
            } else {
                console.log(data.response);  // Imprime la respuesta del servidor en la consola
                chatBox.innerHTML += "<p><strong>Bot:</strong> " + data.response + "</p>";
            }
        });

    // Limpiar campo de entrada después de enviar el mensaje
    document.getElementById("user-input").value = "";
}

// Función para manejar la pulsación de tecla en el campo de entrada de texto
function handleKeyPress(event) {
    // Verificar si la tecla presionada es "Enter" (código 13)
    if (event.keyCode === 13) {
        // Evitar el comportamiento predeterminado del evento (evitar enviar el formulario)
        event.preventDefault();
        // Llamar a la función sendMessage cuando se presione "Enter"
        sendMessage();
    }
}

// Función para obtener la respuesta inicial del bot al cargar la página
document.addEventListener("DOMContentLoaded", function () {
    fetch('/get_response/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ message: "" })  // Envía un mensaje vacío para obtener la respuesta inicial del bot
    })
        .then(response => response.text())  // Cambia de response.json() a response.text()
        .then(data => {
            chatBox.innerHTML += "<p><strong>Bot:</strong> " + data + "</p>";  // Muestra la respuesta como texto
        });
});