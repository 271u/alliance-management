import { getCsrfToken } from "./misc.js";
function showError(message) {
    const errorArticle = document.getElementById("error-message-article");
    const errorMessage = document.getElementById("error-message-body");
    if (!errorArticle || !errorMessage) {
        return;
    }
    errorArticle.classList.remove("hidden");
    errorMessage.innerText = message;
}
function handleNext(next) {
    if (!next || next === "") {
        document.location.href = "/";
        return;
    }
    document.location.href = next;
}
async function deleteComment(event) {
    event.preventDefault();
    const idInput = document.getElementById("id-input");
    const nextUrlInput = document.getElementById("next-url-input");
    const deleteButton = document.getElementById("delete-button");
    if (!idInput || !deleteButton) {
        showError("Cannot delete comment because the page is missing required fields.");
        return;
    }
    deleteButton.classList.add("is-loading");
    deleteButton.disabled = true;
    const response = await fetch(`/api/comment/delete/${idInput.value}`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": getCsrfToken(),
        },
    });
    if (response.status !== 204) {
        let errMsg = "Failed to delete comment.";
        try {
            const responseBody = await response.json();
            if (responseBody.message) {
                errMsg = `Failed to delete comment: ${responseBody.message}`;
            }
        }
        catch {
            errMsg = "Failed to delete comment, and the server did not return a JSON error message.";
        }
        deleteButton.classList.remove("is-loading");
        deleteButton.disabled = false;
        showError(errMsg);
        return;
    }
    handleNext(nextUrlInput?.value ?? null);
}
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("delete-comment-form");
    if (form) {
        form.addEventListener("submit", deleteComment);
    }
});
