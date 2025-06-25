from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import Articulo, Fabrica, EstatusPMO, Categoria, ImportacionDatos
import pandas as pd
from decimal import Decimal

class ImportacionArchivosForm(forms.Form):
    """Formulario para importar archivos Excel/CSV"""
    archivo = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv'
        }),
        help_text='Formatos soportados: Excel (.xlsx, .xls) y CSV (.csv)'
    )
    
    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        
        # Validar tamaño
        if archivo.size > 50 * 1024 * 1024:  # 50MB
            raise ValidationError('El archivo no puede ser mayor a 50MB')
        
        # Validar extensión
        extension = archivo.name.split('.')[-1].lower()
        if extension not in ['xlsx', 'xls', 'csv']:
            raise ValidationError('Formato no soportado. Use Excel o CSV.')
        
        return archivo

class FiltroArticulosForm(forms.Form):
    """Formulario simplificado para filtrar artículos"""
    año = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '2024'
        })
    )
    
    id_pmo = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por ID de PMO...'
        })
    )
    
    nombre_proyecto = forms.CharField(
        required=False,
        max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de proyecto...'
        })
    )
    
    estatus = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Estatus PMO...'
        })
    )
    
    fabrica = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Fábrica...'
        })
    )

class ArticuloForm(ModelForm):
    """Formulario simplificado para crear/editar artículos"""
    
    class Meta:
        model = Articulo
        fields = [
            'año', 'articulo', 'descripcion', 'proveedor', 'nombre_proyecto_recibo',
            'orden_compra', 'id_pmo', 'nombre_proyecto', 'program_manager',
            'estatus_pmo_texto', 'fecha_implementacion', 'historial', 'observaciones',
            'retrasos_salida', 'avp', 'tipo', 'fabrica_texto',
            'costo_unitario_distribucion', 'cantidad_embarcada', 'costo_salida_mxn',
            'existencia_actual', 'costo_mxn_existencias', 'costo_usd_existencias'
        ]
        widgets = {
            'año': forms.NumberInput(attrs={'class': 'form-control'}),
            'articulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_proyecto_recibo': forms.TextInput(attrs={'class': 'form-control'}),
            'orden_compra': forms.TextInput(attrs={'class': 'form-control'}),
            'id_pmo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_proyecto': forms.TextInput(attrs={'class': 'form-control'}),
            'program_manager': forms.TextInput(attrs={'class': 'form-control'}),
            'estatus_pmo_texto': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_implementacion': forms.TextInput(attrs={'class': 'form-control'}),
            'historial': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'retrasos_salida': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avp': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'fabrica_texto': forms.TextInput(attrs={'class': 'form-control'}),
            'costo_unitario_distribucion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cantidad_embarcada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'costo_salida_mxn': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'existencia_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'costo_mxn_existencias': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'costo_usd_existencias': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class CambioEstatusForm(forms.Form):
    """Formulario simplificado para cambiar estatus"""
    nuevo_estatus = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nuevo estatus...'
        })
    )
    
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones del cambio...'
        })
    ) 