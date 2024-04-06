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
                chatBox.innerHTML += "<p><strong>Bot:</strong> Hasta luego, espero haberte ayudado, saludos.</p>";                        
                close();
            } else {
                console.log(data.response);
                chatBox.innerHTML += "<p><strong>Bot:</strong> " + data.response + " <button class='like-button' onclick='likeResponse(this)'>Me gusta</button></p>";
            }
        });

    document.getElementById("user-input").value = "";
}

//cierra la ventana
function close() {
    setTimeout(function () {
            window.close();                     
        },1800); // 1.8 segundos
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
/*
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#registro-form');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        fetch('/ruta/de/tu/vista/vista_registro/', {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const mensajeAlerta = document.querySelector('#mensaje-alerta');
                mensajeAlerta.innerText = data.mensaje_alerta;
                mensajeAlerta.classList.add('alert', 'alert-success');
            } else {
                // Mostrar errores en caso de que haya ocurrido algún problema en el formulario
                const errores = data.errors;
                // Aquí puedes mostrar los errores donde quieras en tu página
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
*/
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
// Función para enviar una imagen al servidor para su procesamiento
function uploadImage() {
    // Obtener el formulario y la imagen seleccionada por el usuario
    var form = document.getElementById('image-upload-form');
    var formData = new FormData(form);

    // Realizar una solicitud AJAX al servidor
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/process_fingerprint_images_web/', true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            // La solicitud fue exitosa, puedes hacer algo con la respuesta si es necesario
            console.log(xhr.responseText);
        } else {
            // Hubo un error en la solicitud
            console.error('Error al procesar la imagen:', xhr.statusText);
        }
    };
    xhr.onerror = function () {
        // Hubo un error de red
        console.error('Error de red al procesar la imagen.');
    };
    xhr.send(formData);
}
  
    
