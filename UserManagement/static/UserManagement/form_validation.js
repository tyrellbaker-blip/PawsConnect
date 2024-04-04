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
    const hasPetsYes = document.getElementById('id_has_pets_0'); // Adjust the ID if necessary
    const hasPetsNo = document.getElementById('id_has_pets_1'); // Adjust the ID if necessary
    const petInfoSection = document.getElementById('pet-info-section'); // The section to show/hide

    // Initially hide the pet information section
    petInfoSection.style.display = hasPetsYes.checked ? 'block' : 'none';

    // Function to show/hide pet info section based on user selection
    function togglePetInfoDisplay() {
        petInfoSection.style.display = hasPetsYes.checked ? 'block' : 'none';
    }
    // Listen for changes in the has_pets field
    hasPetsYes.addEventListener('change', togglePetInfoDisplay);
    hasPetsNo.addEventListener('change', togglePetInfoDisplay);

    // Handle adding more pet forms
    const addPetFormButton = document.getElementById('add-pet-form');
if (addPetFormButton) {
    addPetFormButton.addEventListener('click', function() {
        const petFormsContainer = document.getElementById('pet-forms');
        const totalPetForms = petFormsContainer.getElementsByClassName('pet-form').length;
        const newFormIndex = totalPetForms; // The index for the new form

        // Clone the first pet form to use as a template for the new form
        const newPetForm = petFormsContainer.querySelector('.pet-form').cloneNode(true);

        // Prepare to update new form fields
        const newFieldInputs = newPetForm.querySelectorAll('input, select, textarea');
        newFieldInputs.forEach(function(input) {
            const nameAttr = input.getAttribute('name');
            if (nameAttr) {
                input.setAttribute('name', nameAttr.replace(/\d+/, String(newFormIndex)));
            }

            const idAttr = input.getAttribute('id');
            if (idAttr) {
                input.setAttribute('id', idAttr.replace(/\d+/, String(newFormIndex)));
            }

            // Reset the value of inputs to ensure the new form is empty
            if (input.tagName === 'INPUT' && input.type !== 'checkbox' && input.type !== 'radio') {
                input.value = '';
            } else if (input.tagName === 'SELECT') {
                input.selectedIndex = 0;
            }
        });

        // Append the new form to the container
        petFormsContainer.appendChild(newPetForm);

        // Update the management form to reflect the new total number of forms
        // This should be done outside and after the loop
        const totalFormsInput = document.getElementById('id_pets-TOTAL_FORMS');
        totalFormsInput.setAttribute('value', String(newFormIndex + 1));
    });
}


    });


