import { getCsrfToken } from "./misc.js";
async function deleteComment() {
    const idInput = document.getElementById("id-input");
    if (!idInput)
        return;
    const deleteButton = document.getElementById("delete-button");
    if (!deleteButton)
        return;
    deleteButton.classList.add("is-loading");
    deleteButton.disabled = true;
    const urlParams = new URLSearchParams(window.location.search);
    const next = urlParams.get('next');
    const url = "/api/comment/delete/" + idInput.value;
    console.log(url);
    const response = await fetch(url, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
        },
    });
    console.log(response.status);
    if (response.status != 204) {
        let responseBody = await response.json();
        let errMsg = "Failed to delete comment: ";
        if (responseBody.message)
            errMsg += responseBody.message;
        else
            errMsg += "Unknown error";
        deleteButton.classList.remove("is-loading");
        deleteButton.disabled = false;
        const errorArticle = document.getElementById("error-message-article");
        const errorHeader = document.getElementById("error-message-header");
        const errorMessage = document.getElementById("error-message-body");
        if (errorArticle == null ||
            errorHeader == null ||
            errorMessage == null) {
            return;
        }
        errorArticle.classList.remove("hidden");
        errorMessage.innerText = errMsg;
        return;
    }
    handleNext(next);
    return;
}
function handleNext(next) {
    console.log("Next: " + next);
    if (!next || next === "") {
        document.location.href = "/";
        return;
    }
    document.location.href = next;
}
// Wait for the DOM to be ready, then hook up the click event
document.addEventListener("DOMContentLoaded", () => {
    const deleteButton = document.getElementById("delete-button");
    if (deleteButton)
        deleteButton.addEventListener("click", deleteComment);
});
