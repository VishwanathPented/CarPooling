// Example of how to include CSRF token in AJAX requests
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

fetch('/send_message/5/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrftoken
    },
    body: 'message=Hello'
})