export function getCsrfToken(): string {
  const csrfInput = document.querySelector<HTMLInputElement>(
    "input[name='csrfmiddlewaretoken']",
  );

  return csrfInput?.value ?? "";
}
