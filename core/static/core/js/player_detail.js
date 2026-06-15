import { getCsrfToken } from "./misc.js";
async function setError(message) {
    const errorArticle = document.getElementById("error-message-article");
    const errorHeader = document.getElementById("error-message-header");
    const errorMessage = document.getElementById("error-message-body");
    if (errorArticle == null ||
        errorHeader == null ||
        errorMessage == null) {
        return;
    }
    errorArticle.classList.remove("hidden");
    errorMessage.innerHTML = message;
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}
function validateInputs() {
    const addButton = document.getElementById("button-submit");
    const messageInput = document.getElementById("message");
    if (!addButton)
        return;
    if (messageInput && messageInput.value.length >= 3)
        addButton.disabled = false;
    else
        addButton.disabled = true;
}
async function sendCommentPost() {
    const addButton = document.getElementById("button-submit");
    const messageInput = document.getElementById("message");
    const targetIdInput = document.getElementById("target-id");
    const targetTypeInput = document.getElementById("target-type");
    let errors = [];
    if (addButton == null)
        errors.push("'button-submit' not found");
    if (messageInput == null)
        errors.push("'message' not found");
    if (targetIdInput == null)
        errors.push("'target-id' not found");
    if (targetTypeInput == null)
        errors.push("'target-type' not found");
    if (errors.length > 0) {
        // Initialize errMsg with let so we can append to it
        let errMsg = "Something weird happened, and you should never see this, please inform the developer haha (386bc7e6-d05c-40ad-8a27-6f3d4f842092)<br>The following error(s) occurred:";
        errMsg += "<ul>";
        errors.forEach(element => {
            errMsg += "<li>" + element + "</li>";
        });
        errMsg += "</ul>";
        await setError(errMsg);
        return;
    }
    if (!addButton)
        return;
    if (!messageInput)
        return;
    if (!targetIdInput)
        return;
    if (!targetTypeInput)
        return;
    addButton.classList.add("is-loading");
    addButton.disabled = true;
    messageInput.disabled = true;
    let body = {
        message: messageInput.value,
        target_id: Number(targetIdInput.value),
        target_type: targetTypeInput.value
    };
    const response = await fetch("/api/comment/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify(body),
    });
    if (response.status != 201) {
        let responseBody = await response.json();
        if (responseBody.message)
            setError("Failed to create new comment: " + responseBody.message);
        else
            setError("Failed to create new comment, and server did not give a reason why");
        addButton.classList.remove("is-loading");
        addButton.disabled = false;
        messageInput.disabled = false;
        return;
    }
    messageInput.value = "";
    window.location.reload();
}
// Wait for the DOM to be ready, then hook up the click event
document.addEventListener("DOMContentLoaded", () => {
    const addButton = document.getElementById("button-submit");
    const messageInput = document.getElementById("message");
    if (addButton)
        addButton.addEventListener("click", sendCommentPost);
    if (messageInput)
        messageInput.addEventListener("input", validateInputs);
});
