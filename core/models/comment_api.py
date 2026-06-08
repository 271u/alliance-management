from __future__ import annotations

from pydantic import BaseModel

class ApiCommentModel(BaseModel):
  message: str
  target_type: str
  target_id: int
