import { showError, clearErrors, highlightInputError } from './form-utils.js'

document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    clearErrors();

    const loginInput = document.getElementById("login");
    const passwordInput = document.getElementById("password");

    const login = loginInput.value.trim();
    const password = passwordInput.value.trim();

    let hasError = false;
    if (!login) {
        showError("login", "Login cannot be empty");
        hasError = true;
    }
    if (!password) {
        showError("password", "Password cannot be empty");
        hasError = true;
    }
    if (hasError) return;

    try {
        const res = await fetch("/users/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ login, password })
        });

        if (res.ok) {
            window.location.href = "/dashboard";
        } else {
            const data = await res.json();
            const errorCode = data.detail;

            switch (errorCode) {
                case "invalid_credentials":
                case "user_not_found":
                    showError("login", "Invalid login or password");
                    highlightInputError("password");
                    break;

                case "email_not_confirmed":
                    showError("login", "Please confirm your email first");
                    break;

                case "user_banned":
                    showError("login", "This account has been banned");
                    break;

                case "weak_password":
                    console.log("Triggered");
                    showError("password", "Password is too weak");
                    break;

                case "email_address_invalid":
                case "validation_failed":
                    showError("login", "Invalid login format");
                    break;

                case "over_request_rate_limit":
                    showError("login", "Too many attempts. Please try again later.");
                    break;

                case "unexpected_failure":
                case "request_timeout":
                    showError("login", "Server error. Please try again later.");
                    break;

                default:
                    showError("login", `Authentication error: ${errorCode || 'unknown'}`);
            }
        }
    }
    catch (err) {
        showError("login", "Network error. Please try again.");
    }
});
