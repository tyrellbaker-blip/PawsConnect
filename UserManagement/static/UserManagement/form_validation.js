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
document.addEventListener("DOMContentLoaded", function() {
    const emailField = document.getElementById("id_email");
    const passwordField = document.getElementById("id_password1"); // Assuming 'password1' is the field ID
    const passwordError = document.createElement("div");
    const emailError = document.createElement("div");

    passwordError.style.color = "red";
    emailError.style.color = "red";

    passwordField.parentNode.insertBefore(passwordError, passwordField.nextSibling);
    emailField.parentNode.insertBefore(emailError, emailField.nextSibling);

    passwordField.addEventListener("input", function() {
        if (passwordField.value.length < 8) {
            passwordError.textContent = "Password doesn't meet requirements";
        } else {
            passwordError.textContent = "";
        }
    });

    emailField.addEventListener("input", function() {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailField.value)) {
            emailError.textContent = "Invalid email address";
        } else {
            emailError.textContent = "";
        }
    });
});
