from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
import locale

register = template.Library()

@register.filter
def numero_grande(valor):
    """
    Convierte números grandes a formato más legible
    Ejemplo: 33958 -> 33.9K, 147154636 -> 147.2M
    """
    try:
        valor = float(valor) if valor else 0
        
        if valor >= 1_000_000_000:  # Billones
            return f"{valor/1_000_000_000:.1f}B"
        elif valor >= 1_000_000:  # Millones
            return f"{valor/1_000_000:.1f}M"
        elif valor >= 1_000:  # Miles
            return f"{valor/1_000:.1f}K"
        else:
            return f"{valor:.0f}"
    except (ValueError, TypeError):
        return "0"

@register.filter
def moneda_formato(valor):
    """
    Formato de moneda con comas y símbolo de dólar
    """
    try:
        valor = float(valor) if valor else 0
        return f"${intcomma(int(valor))}"
    except (ValueError, TypeError):
        return "$0"

@register.filter
def moneda_compacta(valor):
    """
    Formato de moneda compacto para números grandes
    Ejemplo: 147154636 -> $147.2M
    """
    try:
        valor = float(valor) if valor else 0
        
        if valor >= 1_000_000_000:
            return f"${valor/1_000_000_000:.1f}B"
        elif valor >= 1_000_000:
            return f"${valor/1_000_000:.1f}M"
        elif valor >= 1_000:
            return f"${valor/1_000:.1f}K"
        else:
            return f"${valor:.0f}"
    except (ValueError, TypeError):
        return "$0"

@register.filter
def porcentaje_formato(valor):
    """
    Formato de porcentaje con 1 decimal
    """
    try:
        valor = float(valor) if valor else 0
        return f"{valor:.1f}%"
    except (ValueError, TypeError):
        return "0.0%"

@register.filter
def unidades_formato(valor):
    """
    Formato para unidades con comas
    """
    try:
        valor = float(valor) if valor else 0
        return intcomma(int(valor))
    except (ValueError, TypeError):
        return "0" 