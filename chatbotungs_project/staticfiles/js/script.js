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
                console.log(data.error);
                chatBox.innerHTML += "<p><strong>Bot:</strong> " + data.error + "</p>";
            } else if (data.response === 'exit') {
                chatBox.innerHTML += "<p><strong>Bot:</strong> Hasta luego, espero haberte ayudado, saludos.</p>"
                window.close();
            } else {
                console.log(data.response);
                chatBox.innerHTML += "<p><strong>Bot:</strong> " + data.response + " <button class='like-button' onclick='likeResponse(this)'>Me gusta</button></p>";
            }
        });

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


function likeResponse(button) {
    // Obtener la respuesta del bot
    var botResponse = button.parentNode.innerText.replace('Me gusta', '').trim();
    
    // Realizar una solicitud AJAX para enviar la retroalimentación al servidor
    fetch('/feedback/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Obtener el token CSRF de las cookies
        },
        body: JSON.stringify({ 
            response: botResponse,
            liked: true  // Indicar que se dio like a la respuesta
        })
    })
    .then(response => {
        if (response.ok) {
            // La retroalimentación se envió correctamente
            alert('¡Gracias por tu retroalimentación!');
        } else {
            // Hubo un error al enviar la retroalimentación
            alert('Error al enviar la retroalimentación');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al enviar la retroalimentación');
    });
}


// Función para obtener el valor de una cookie por su nombre
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Buscar la cookie por su nombre
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}