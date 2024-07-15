let users = [];
function escapeHTML(text) {
    return text.replace(/&/g, "&amp;")
               .replace(/</g, "&lt;")
               .replace(/>/g, "&gt;")
               .replace(/"/g, "&quot;")
               .replace(/'/g, "&#x27;");
}


function login() {
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    // Check if user exists in the array
    let user = users.find(u => u.username === username && u.password === password);

    if (user) {
        // Display welcome page
        document.body.innerHTML = `
            <div class="container">
                <h1>Welcome, ${user.name}!</h1>
                <p>Here is your user information:</p>
                <p>Username: ${user.username}</p>
                <p>Password: ${user.password}</p>
            </div>
        `;
    } else {
        // Show error message
        document.getElementById('error-message').innerText = "Invalid credentials. Please try again.";
    }
}

function register() {
    var name = document.getElementById('name').value;
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    var confirm_password = document.getElementById('confirm_password').value;

    if (password !== confirm_password) {
        document.getElementById('error-message').innerText = "Passwords do not match.";
        return;
    }

    // Check if username already exists
    if (users.some(u => u.username === username)) {
        document.getElementById('error-message').innerText = "Username already exists.";
        return;
    }

    // Add user to the array
    users.push({ name, username, password });
    document.getElementById('error-message').innerText = "Registration successful. Please login.";
}

$(document).ready(function() {
    $('.category-btn').click(function() {
        $(this).toggleClass('selected');
    });

    $('#save-btn').click(function() {
        var selectedCategories = $('.selected').map(function() {
            return $(this).data('category');
        }).get();

        // Send selectedCategories to the server to save to the user database
        console.log(selectedCategories);
    });
});