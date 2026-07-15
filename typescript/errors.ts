export type ErrorResponse = {
  error: string;
  detail: string;
};


export async function setError(message: string) {
  const errorArticle = document.getElementById(
    "error-message-article",
  ) as HTMLElement | null;
  const errorHeader = document.getElementById(
    "error-message-header",
  ) as HTMLParagraphElement | null;
  const errorMessage = document.getElementById(
    "error-message-body",
  ) as HTMLDivElement | null;

  if (errorArticle == null || errorHeader == null || errorMessage == null) {
    return;
  }

  errorArticle.classList.remove("hidden");
  errorMessage.innerHTML = message;
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}
