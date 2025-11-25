from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from qrmuseum.models import QRCode, ContenidoQR, Comentario, UsuarioMuseo, MuseoConfig


class RegistroUsuarioForm(forms.ModelForm):
    """Formulario de registro para usuarios"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'required': True,
            'minlength': 6
        }),
        min_length=6,
        help_text='Mínimo 6 caracteres'
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
            'required': True
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com',
                'required': True
            })
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está registrado')
        if len(username) < 3:
            raise ValidationError('El nombre de usuario debe tener al menos 3 caracteres')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo ya está registrado')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')
        
        if password and confirmar_password:
            if password != confirmar_password:
                raise ValidationError('Las contraseñas no coinciden')
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password'))
        if commit:
            user.save()
            # Crear perfil de museo automáticamente
            UsuarioMuseo.objects.get_or_create(usuario=user)
        return user


class QRCodeForm(forms.ModelForm):
    """Formulario para crear/editar códigos QR"""
    class Meta:
        model = QRCode
        fields = ['titulo', 'descripcion', 'ubicacion', 'numero_secuencial', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del punto QR',
                'required': True
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción breve',
                'rows': 3
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación en el museo'
            }),
            'numero_secuencial': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1, 2, 3, ...',
                'required': True
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class ContenidoQRForm(forms.ModelForm):
    """Formulario para crear/editar contenido de QR"""
    class Meta:
        model = ContenidoQR
        fields = ['tipo_contenido', 'titulo', 'descripcion_detallada', 'imagen', 
                 'video', 'video_url_externa', 'audio', 'archivo_descarga', 
                 'datos_historicos', 'datos_cientificos', 'curiosidades', 'activo',
                 'mostrar_imagen', 'mostrar_video', 'mostrar_audio', 'mostrar_archivo',
                 'mostrar_historico', 'mostrar_cientifico', 'mostrar_curiosidades']
        widgets = {
            'tipo_contenido': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del contenido',
                'required': True
            }),
            'descripcion_detallada': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción detallada del contenido',
                'rows': 4
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/mp4,video/webm'
            }),
            'video_url_externa': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... o URL de Google Drive, Vimeo, etc.'
            }),
            'audio': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/mpeg,audio/wav,video/mp4'
            }),
            'archivo_descarga': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'datos_historicos': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Información histórica...',
                'rows': 3
            }),
            'datos_cientificos': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Información científica...',
                'rows': 3
            }),
            'curiosidades': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Curiosidades...',
                'rows': 3
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_imagen': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_video': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_audio': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_archivo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_historico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_cientifico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_curiosidades': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class ComentarioForm(forms.ModelForm):
    """Formulario para agregar comentarios"""
    class Meta:
        model = Comentario
        fields = ['calificacion', 'texto']
        widgets = {
            'calificacion': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe tu comentario...',
                'rows': 4
            })
        }


class PerfilUsuarioMuseoForm(forms.ModelForm):
    """Formulario para editar perfil del usuario en el museo"""
    class Meta:
        model = UsuarioMuseo
        fields = ['apodo_juego', 'avatar']
        widgets = {
            'apodo_juego': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu apodo en el juego',
                'maxlength': 100
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }


class MuseoConfigForm(forms.ModelForm):
    """Formulario para configurar el museo (solo admin)"""
    class Meta:
        model = MuseoConfig
        fields = ['nombre', 'descripcion', 'ubicacion', 'imagen_logo', 'imagen_fondo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del museo',
                'required': True
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del museo',
                'rows': 4
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación geográfica'
            }),
            'imagen_logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'imagen_fondo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
