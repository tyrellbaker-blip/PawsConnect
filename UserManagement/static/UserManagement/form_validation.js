document.addEventListener('DOMContentLoaded', function() {
    const passwordField = document.getElementById('id_password1');  // Adjust the ID if necessary
    const messageBox = document.createElement('div');
    messageBox.style.color = 'red';
    passwordField.parentNode.insertBefore(messageBox, passwordField.nextSibling);

    passwordField.onkeyup = function() {
        const password = passwordField.value;
        let messages = [];
        if (password.length < 8) {
            messages.push('Password must be at least 8 characters long.');
        }
        // Add more conditions as needed

        if (messages.length > 0) {
            messageBox.innerHTML = messages.join('<br>');
        } else {
            messageBox.innerHTML = '';
        }
    };
});