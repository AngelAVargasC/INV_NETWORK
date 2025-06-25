from .models import PerfilUsuario

def perfil_usuario(request):
    """
    Context processor para hacer disponible el perfil del usuario en todos los templates
    """
    if request.user.is_authenticated:
        try:
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
            return {
                'user_profile': perfil,
                'user_has_photo': bool(perfil.foto_perfil)
            }
        except Exception:
            return {
                'user_profile': None,
                'user_has_photo': False
            }
    return {
        'user_profile': None,
        'user_has_photo': False
    } 