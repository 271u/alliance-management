import json
from typing import Any

from django import template

register = template.Library()


@register.filter
def audit_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


@register.filter
def audit_field_label(value: str) -> str:
    return str(value).replace("_", " ").title()


@register.filter
def audit_action_class(action: str) -> str:
    match action:
        case "created":
            return "is-success"
        case "updated":
            return "is-info"
        case "deleted":
            return "is-danger"
        case _:
            return "is-light"


@register.filter
def audit_action_icon(action: str) -> str:
    match action:
        case "created":
            return "fa-plus"
        case "updated":
            return "fa-pen"
        case "deleted":
            return "fa-trash"
        case _:
            return "fa-circle-info"


@register.filter
def audit_is_structured(value: Any) -> bool:
    return isinstance(value, dict | list)


@register.filter
def audit_display_value(value: Any) -> str:
    if value is None:
        return "empty"

    if value is True:
        return "true"

    if value is False:
        return "false"

    if isinstance(value, dict | list):
        return audit_json(value)

    return str(value)

@register.filter
def audit_changed_items(changes: Any) -> list[dict[str, Any]]:
    if not isinstance(changes, dict):
        return []

    changed_items = []

    for field, change in changes.items():
        if not isinstance(change, dict):
            continue

        old_value = change.get("old")
        new_value = change.get("new")

        if old_value == new_value:
            continue

        changed_items.append(
            {
                "field": field,
                "old": old_value,
                "new": new_value,
            }
        )

    return changed_items
