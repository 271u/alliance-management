from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def rank_tag(rank: str) -> str:
    rank_classes = {
        "R5": "is-r5-tag",
        "R4": "is-r4-tag",
        "R3": "is-r3-tag",
        "R2": "is-r2-tag",
        "R1": "is-r1-tag",
    }

    css_class = rank_classes.get(rank, "is-light")

    return format_html(
        '<span class="tag {}">{}</span>',
        css_class,
        rank,
    )
