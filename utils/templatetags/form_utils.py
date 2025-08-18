from django import template
from django.forms import TextInput, Textarea
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='add_placeholder')
def add_placeholder(field, placeholder=''):
    """
    Adds a placeholder attribute to form fields.
    Usage: {{ field|add_placeholder:"Enter text here" }}
    """
    if not field:
        return ''
        
    # Get the widget
    widget = field.field.widget
    
    # Handle both regular and bound fields
    if hasattr(field, 'field'):
        widget = field.field.widget
    
    # Set placeholder attribute
    attrs = widget.attrs or {}
    attrs['placeholder'] = placeholder
    widget.attrs = attrs
    
    # Return the field with updated attributes
    return field
