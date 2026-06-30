import { getCsrfToken } from "./misc.js";
const MAX_IMAGE_PREVIEW_FILES = 5;
const MAX_IMAGE_PREVIEW_SIZE_MB = 5;
let previewObjectUrls = [];
let selectedImageFiles = [];
async function setError(message) {
    const errorArticle = document.getElementById("error-message-article");
    const errorHeader = document.getElementById("error-message-header");
    const errorMessage = document.getElementById("error-message-body");
    if (errorArticle == null || errorHeader == null || errorMessage == null) {
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
    const imageInput = document.getElementById("comment-images");
    let errors = [];
    if (addButton == null)
        errors.push("'button-submit' not found");
    if (messageInput == null)
        errors.push("'message' not found");
    if (targetIdInput == null)
        errors.push("'target-id' not found");
    if (targetTypeInput == null)
        errors.push("'target-type' not found");
    if (imageInput == null)
        errors.push("'comment-images' not found");
    if (errors.length > 0) {
        let errMsg = "Something weird happened, and you should never see this, please inform the developer haha (386bc7e6-d05c-40ad-8a27-6f3d4f842092)<br>The following error(s) occurred:";
        errMsg += "<ul>";
        errors.forEach((element) => {
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
    if (!imageInput)
        return;
    addButton.classList.add("is-loading");
    addButton.disabled = true;
    messageInput.disabled = true;
    imageInput.disabled = true;
    const body = new FormData();
    body.append("message", messageInput.value);
    body.append("target_id", targetIdInput.value);
    body.append("target_type", targetTypeInput.value);
    if (imageInput.files) {
        for (const image of imageInput.files) {
            body.append("images", image);
        }
    }
    let response;
    try {
        response = await fetch("/api/comment/add", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCsrfToken(),
            },
            body: body,
        });
    }
    catch (error) {
        // Network errors throw a TypeError in the fetch API
        if (error instanceof TypeError) {
            setError("Failed to create new comment: Couldn't reach server. Please reload the page and try again in a few minutes. If the issue persists, contact your website admin.");
            return;
        }
        else {
            // Catches any other unexpected errors (e.g., issues running getCsrfToken())
            console.error("An unexpected error occurred:", error);
            return;
        }
    }
    if (response.status != 201) {
        let responseBody = await response.json();
        if (responseBody.message)
            setError("Failed to create new comment: " + responseBody.message);
        else
            setError("Failed to create new comment, and server did not give a reason why");
        addButton.classList.remove("is-loading");
        addButton.disabled = false;
        messageInput.disabled = false;
        imageInput.disabled = false;
        return;
    }
    messageInput.value = "";
    imageInput.value = "";
    clearImagePreview();
    window.location.reload();
}
function clearImagePreview() {
    const previewWrapper = document.getElementById("comment-image-preview-wrapper");
    const previewContainer = document.getElementById("comment-image-preview");
    previewObjectUrls.forEach((url) => URL.revokeObjectURL(url));
    previewObjectUrls = [];
    selectedImageFiles = [];
    if (previewContainer) {
        previewContainer.innerHTML = "";
    }
    if (previewWrapper) {
        previewWrapper.classList.add("hidden");
    }
}
function syncImageInputFiles() {
    const imageInput = document.getElementById("comment-images");
    if (!imageInput) {
        return;
    }
    const dataTransfer = new DataTransfer();
    for (const file of selectedImageFiles) {
        dataTransfer.items.add(file);
    }
    imageInput.files = dataTransfer.files;
}
function removeImageFromPreview(index) {
    selectedImageFiles.splice(index, 1);
    syncImageInputFiles();
    renderSelectedImagePreview();
}
function renderSelectedImagePreview() {
    const previewWrapper = document.getElementById("comment-image-preview-wrapper");
    const previewContainer = document.getElementById("comment-image-preview");
    if (!previewWrapper || !previewContainer) {
        return;
    }
    previewObjectUrls.forEach((url) => URL.revokeObjectURL(url));
    previewObjectUrls = [];
    previewContainer.innerHTML = "";
    if (selectedImageFiles.length === 0) {
        previewWrapper.classList.add("hidden");
        return;
    }
    selectedImageFiles.forEach((file, index) => {
        const objectUrl = URL.createObjectURL(file);
        previewObjectUrls.push(objectUrl);
        const previewItem = document.createElement("div");
        previewItem.classList.add("comment-image-preview-item");
        const image = document.createElement("img");
        image.src = objectUrl;
        image.alt = file.name;
        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.classList.add("button", "is-small", "is-danger", "is-light", "mt-2", "is-fullwidth");
        removeButton.innerText = "Remove";
        removeButton.addEventListener("click", () => removeImageFromPreview(index));
        const caption = document.createElement("p");
        caption.classList.add("help");
        caption.innerText = file.name;
        previewItem.appendChild(image);
        previewItem.appendChild(removeButton);
        previewItem.appendChild(caption);
        previewContainer.appendChild(previewItem);
    });
    previewWrapper.classList.remove("hidden");
}
async function renderImagePreview() {
    const imageInput = document.getElementById("comment-images");
    if (!imageInput) {
        return;
    }
    previewObjectUrls.forEach((url) => URL.revokeObjectURL(url));
    previewObjectUrls = [];
    const files = Array.from(imageInput.files ?? []);
    if (files.length === 0) {
        clearImagePreview();
        return;
    }
    if (files.length > MAX_IMAGE_PREVIEW_FILES) {
        await setError(`You can upload at most ${MAX_IMAGE_PREVIEW_FILES} images per comment.`);
        imageInput.value = "";
        clearImagePreview();
        return;
    }
    const maxSizeBytes = MAX_IMAGE_PREVIEW_SIZE_MB * 1024 * 1024;
    for (const file of files) {
        if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
            await setError(`${file.name} is not an allowed image type. Allowed: JPG, PNG or WEBP.`);
            imageInput.value = "";
            clearImagePreview();
            return;
        }
        if (file.size > maxSizeBytes) {
            await setError(`${file.name} is too large. Maximum size is ${MAX_IMAGE_PREVIEW_SIZE_MB} MB.`);
            imageInput.value = "";
            clearImagePreview();
            return;
        }
    }
    selectedImageFiles = files;
    renderSelectedImagePreview();
}
document.addEventListener("DOMContentLoaded", () => {
    const addButton = document.getElementById("button-submit");
    const messageInput = document.getElementById("message");
    const imageInput = document.getElementById("comment-images");
    if (addButton)
        addButton.addEventListener("click", sendCommentPost);
    if (messageInput)
        messageInput.addEventListener("input", validateInputs);
    if (imageInput)
        imageInput.addEventListener("change", renderImagePreview);
});
