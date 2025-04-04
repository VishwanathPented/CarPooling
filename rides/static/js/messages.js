// Example JavaScript for sending messages with AJAX
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('message-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const messageText = document.querySelector('[name=message]').value;
            const recipientId = form.getAttribute('data-recipient-id') || window.location.pathname.split('/').pop();
            
            // Your JavaScript code is correctly using recipientId in the fetch URL:
            // Make sure your JavaScript is using the correct URL parameter name
            fetch(`/send_message/${recipientId}/`, {
                method: 'POST',  // Make sure this is POST
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: new URLSearchParams({
                    'message': messageText
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Clear the form and update the conversation
                    document.querySelector('[name=message]').value = '';
                    // You might want to add the message to the conversation here
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});