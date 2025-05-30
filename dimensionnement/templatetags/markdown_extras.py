from django import template
from django.template.defaultfilters import stringfilter
import markdown

register = template.Library()

@register.filter
@stringfilter
def render_markdown(value):
    return markdown.markdown(value, extensions=['fenced_code', 'tables']) 