from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PerfilUsuario(models.Model):
    AREAS_CHOICES = [
        ('SISTEMAS', 'Sistemas'),
        ('ADMINISTRACION', 'Administración'),
        ('CONTABILIDAD', 'Contabilidad'),
        ('RECURSOS_HUMANOS', 'Recursos Humanos'),
        ('VENTAS', 'Ventas'),
        ('MARKETING', 'Marketing'),
        ('OPERACIONES', 'Operaciones'),
        ('MANTENIMIENTO', 'Mantenimiento'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    area = models.CharField(max_length=20, choices=AREAS_CHOICES, blank=True, null=True)
    puesto = models.CharField(max_length=100, blank=True, null=True)
    fecha_ingreso = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
        ordering = ['usuario__first_name', 'usuario__last_name']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.area}"
    
    @property
    def nombre_completo(self):
        return self.usuario.get_full_name() or self.usuario.username

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfilusuario'):
        instance.perfilusuario.save()
