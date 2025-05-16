from django import template
import calendar

register = template.Library()

@register.filter
def get_month_name(month_number):
    try:
        month_number = int(month_number)
        return calendar.month_name[month_number]
    except (ValueError, IndexError):
        return ""
