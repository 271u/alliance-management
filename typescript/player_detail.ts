import { CommentBody } from "./models.js";
import { getCsrfToken } from "./misc.js";

async function setError(message:string) {
  const errorArticle = document.getElementById("error-message-article") as HTMLElement | null;
  const errorHeader = document.getElementById("error-message-header") as HTMLParagraphElement | null;
  const errorMessage = document.getElementById("error-message-body") as HTMLDivElement | null;

  if (
    errorArticle == null ||
    errorHeader  == null ||
    errorMessage == null
  ) {
    return
  }

  errorArticle.classList.remove("hidden")
  errorMessage.innerHTML = message
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}

function validateInputs() {
  const addButton = document.getElementById("button-submit") as HTMLButtonElement | null;
  const messageInput = document.getElementById("message") as HTMLInputElement | null;

  if (!addButton) return;

  if (messageInput && messageInput.value.length >= 3) 
    addButton.disabled = false
  else 
    addButton.disabled = true
}

async function sendCommentPost() {
  const addButton = document.getElementById("button-submit") as HTMLButtonElement | null;
  const messageInput = document.getElementById("message") as HTMLInputElement | null;
  const targetIdInput = document.getElementById("target-id") as HTMLInputElement | null;
  const targetTypeInput = document.getElementById("target-type") as HTMLInputElement | null;

  let errors: string[] = [];

  if (addButton == null) errors.push("'button-submit' not found")
  if (messageInput == null) errors.push("'message' not found")
  if (targetIdInput == null) errors.push("'target-id' not found")
  if (targetTypeInput == null) errors.push("'target-type' not found")

  if (errors.length > 0) {
    // Initialize errMsg with let so we can append to it
    let errMsg = "Something weird happened, and you should never see this, please inform the developer haha (386bc7e6-d05c-40ad-8a27-6f3d4f842092)<br>The following error(s) occurred:";
    errMsg += "<ul>";

    errors.forEach(element => {
      errMsg += "<li>" + element + "</li>";
    });

    errMsg += "</ul>";

    await setError(errMsg);
    return
  }
  if (!addButton) return;
  if (!messageInput) return;
  if (!targetIdInput) return;
  if (!targetTypeInput) return;

  addButton.classList.add("is-loading")
  addButton.disabled = true
  messageInput.disabled = true

  let body: CommentBody = {
    message: messageInput.value,
    target_id: Number(targetIdInput.value),
    target_type: targetTypeInput.value
  }

  const response = await fetch("/api/comment/add", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify(body),
  });


  if (response.status != 201) {
    let responseBody = await response.json()

    if (responseBody.message) 
      setError("Failed to create new comment: " + responseBody.message)
    else
      setError("Failed to create new comment, and server did not give a reason why")

    addButton.classList.remove("is-loading")
    addButton.disabled = false
    messageInput.disabled = false

    return;
  }

  window.location.reload();
}



// Wait for the DOM to be ready, then hook up the click event
document.addEventListener("DOMContentLoaded", () => {
  const addButton = document.getElementById("button-submit") as HTMLButtonElement | null;
  const messageInput = document.getElementById("message") as HTMLInputElement | null;

  if (addButton) addButton.addEventListener("click", sendCommentPost)
  if (messageInput) messageInput.addEventListener("input", validateInputs)
});
