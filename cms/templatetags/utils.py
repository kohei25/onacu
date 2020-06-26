from django import template
 
register = template.Library()
 
@register.filter()
def remains(total, purchaced):
    return total - purchaced