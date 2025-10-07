from django import template

register = template.Library()

@register.filter(name='replace_comma')
def replace_comma(value):
    return str(value).replace(',', '.')

@register.filter(name='format_date')
def format_date(value):
    return str(value).reverse().replace('-','/')

@register.filter(name='format_money')
def format_money(value):
    return "{:,}".format(value)