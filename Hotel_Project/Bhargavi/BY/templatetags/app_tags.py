from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter
def percentage(value, total):
    if total == 0:
        return 0
    return round(value / total * 100)

@register.simple_tag
def todays_date():
    return date.today()

@register.simple_tag
def max_date():
    return date.today() + timedelta(days=30)

@register.simple_tag
def tomorrow():
    return date.today() + timedelta(days=1)