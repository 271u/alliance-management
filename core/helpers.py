
from django.http import JsonResponse


def JsonErrorMessage(message: str, http_code: int = 500):
  return JsonResponse(
    {
      "success": False,
      "message": message,
      },
    status=http_code,
  )
