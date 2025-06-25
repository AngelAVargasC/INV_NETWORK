from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import PerfilUsuario
from .forms import PerfilUsuarioForm, CustomUserForm, RegistroForm

# Create your views here.

class PerfilUsuarioView(LoginRequiredMixin, UpdateView):
    model = PerfilUsuario
    form_class = PerfilUsuarioForm
    template_name = 'usuarios/perfil.html'
    success_url = reverse_lazy('usuarios:perfil')
    
    def get_object(self):
        perfil, created = PerfilUsuario.objects.get_or_create(usuario=self.request.user)
        return perfil
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = CustomUserForm(instance=self.request.user)
        return context
    
    def form_valid(self, form):
        user_form = CustomUserForm(self.request.POST, instance=self.request.user)
        if user_form.is_valid():
            user_form.save()
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # El perfil se crea automáticamente por la señal post_save
            messages.success(request, f'¡Cuenta creada exitosamente para {user.username}! Ya puedes iniciar sesión.')
            return redirect('usuarios:login')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.get_full_name() or user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('usuarios:login')
