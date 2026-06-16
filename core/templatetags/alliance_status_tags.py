from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def alliance_status_tag(rank: str) -> str:
    status_classes = {
        "R5": "is-r5-tag",
        "R4": "is-r4-tag",
        "R3": "is-r3-tag",
        "R2": "is-r2-tag",
        "R1": "is-r1-tag",
        "Not Member": "is-not-member-tag"
    }

    css_class = status_classes.get(rank, "is-light")

    return format_html(
        '<span class="tag {}">{}</span>',
        css_class,
        rank,
    )
