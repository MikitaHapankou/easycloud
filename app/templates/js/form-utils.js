export function showError(fieldId, message) {
    const input = document.getElementById(fieldId);
    const errorMsg = document.getElementById(`${fieldId}-error`);

    if (input && errorMsg) {
        errorMsg.innerText = message;
        errorMsg.classList.remove("hidden");

        input.classList.remove("border-slate-300");
        input.classList.add("border-red-500", "text-red-600", "focus:border-red-500");
    }
}

export function clearErrors() {
    ["login", "password"].forEach(fieldId => {
        const input = document.getElementById(fieldId);
        const errorMsg = document.getElementById(`${fieldId}-error`);

        if (input && errorMsg) {
            errorMsg.classList.add("hidden");

            input.classList.remove("border-red-500", "text-red-600", "focus:border-red-500");
            input.classList.add("border-slate-300");
        }
    });
}

export function highlightInputError(fieldId) {
    const input = document.getElementById(fieldId);
    if (input) {
        input.classList.remove("border-slate-300");
        input.classList.add("border-red-500", "text-red-600", "focus:border-red-500");
    }
}