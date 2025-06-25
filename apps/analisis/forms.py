from django import forms
from django.core.validators import FileExtensionValidator
from .diccionario import ARCHIVO_CONFIGS

class AnalisisArchivosForm(forms.Form):
    """
    Formulario para cargar los tres archivos necesarios para el análisis
    """
    
    archivo_aging = forms.FileField(
        label="Archivo Detalle Aging",
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls',
            'data-tipo': 'aging'
        }),
        help_text="📊 Archivo principal con datos de inventario aging"
    )
    
    archivo_pipeline = forms.FileField(
        label="Archivo Pipeline",
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls',
            'data-tipo': 'pipeline'
        }),
        help_text="🔄 Archivo con información de proyectos y PMO"
    )
    
    archivo_oracle = forms.FileField(
        label="Archivo PO Oracle",
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls',
            'data-tipo': 'oracle'
        }),
        help_text="🏢 Archivo con datos complementarios de Oracle"
    )
    
    def clean(self):
        """Validación adicional del formulario"""
        cleaned_data = super().clean()
        
        # Verificar que todos los archivos están presentes
        required_files = ['archivo_aging', 'archivo_pipeline', 'archivo_oracle']
        for field_name in required_files:
            if not cleaned_data.get(field_name):
                raise forms.ValidationError(f"El archivo {field_name.replace('archivo_', '')} es obligatorio.")
        
        return cleaned_data
    
    def clean_archivo_aging(self):
        """Validación específica para el archivo aging"""
        archivo = self.cleaned_data.get('archivo_aging')
        if archivo:
            # Verificar tamaño (máximo 50MB)
            if archivo.size > 50 * 1024 * 1024:
                raise forms.ValidationError("El archivo aging no debe exceder 50MB.")
            
            # Verificar que el nombre sugiere que es el archivo correcto
            nombre = archivo.name.lower()
            if 'aging' not in nombre and 'detalle' not in nombre:
                raise forms.ValidationError(
                    "Este no parece ser el archivo de aging. "
                    "Asegúrate de que el nombre contenga 'aging' o 'detalle'."
                )
        
        return archivo
    
    def clean_archivo_pipeline(self):
        """Validación específica para el archivo pipeline"""
        archivo = self.cleaned_data.get('archivo_pipeline')
        if archivo:
            # Verificar tamaño (máximo 20MB)
            if archivo.size > 20 * 1024 * 1024:
                raise forms.ValidationError("El archivo pipeline no debe exceder 20MB.")
            
            # Verificar nombre
            nombre = archivo.name.lower()
            if 'pipeline' not in nombre:
                raise forms.ValidationError(
                    "Este no parece ser el archivo de pipeline. "
                    "Asegúrate de que el nombre contenga 'pipeline'."
                )
        
        return archivo
    
    def clean_archivo_oracle(self):
        """Validación específica para el archivo oracle"""
        archivo = self.cleaned_data.get('archivo_oracle')
        if archivo:
            # Verificar tamaño (máximo 30MB)
            if archivo.size > 30 * 1024 * 1024:
                raise forms.ValidationError("El archivo Oracle no debe exceder 30MB.")
            
            # Verificar nombre
            nombre = archivo.name.lower()
            if 'oracle' not in nombre and 'po_' not in nombre:
                raise forms.ValidationError(
                    "Este no parece ser el archivo de Oracle. "
                    "Asegúrate de que el nombre contenga 'oracle' o 'PO_'."
                )
        
        return archivo 