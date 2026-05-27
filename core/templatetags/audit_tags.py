import json
from typing import Any

from django import template

register = template.Library()


@register.filter
def audit_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)
