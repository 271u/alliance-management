import { getCsrfToken } from "./misc.js";

function showError(message: string) {
  const errorArticle = document.getElementById("error-message-article") as HTMLElement | null;
  const errorMessage = document.getElementById("error-message-body") as HTMLDivElement | null;

  if (!errorArticle || !errorMessage) {
    return;
  }

  errorArticle.classList.remove("hidden");
  errorMessage.innerText = message;
}

function handleNext(next: string | null) {
  if (!next || next === "") {
    document.location.href = "/";
    return;
  }

  document.location.href = next;
}

async function deleteComment(event: Event) {
  event.preventDefault();

  const idInput = document.getElementById("id-input") as HTMLInputElement | null;
  const nextUrlInput = document.getElementById("next-url-input") as HTMLInputElement | null;
  const deleteButton = document.getElementById("delete-button") as HTMLButtonElement | null;

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
    } catch {
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
  const form = document.getElementById("delete-comment-form") as HTMLFormElement | null;

  if (form) {
    form.addEventListener("submit", deleteComment);
  }
});
