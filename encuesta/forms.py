from django import forms
from .models import (Encuestado, Encuesta, ItemEncuesta, ItemRespuesta, Fotografia, Respuesta, Configuracion, Perfil)
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
import re
import datetime

class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        exclude = ["responsable"]

class AdminUserChangeForm(UserChangeForm):
    username = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class AdminPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ingrese su contraseña actual',
            'required': True
        })
    )
    new_password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ingrese su nueva contraseña',
            'required': True
        })
    )
    new_password2 = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Confirme su nueva contraseña',
            'required': True
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mejorar los mensajes de error
        self.fields['old_password'].error_messages = {
            'required': 'La contraseña actual es obligatoria.',
            'invalid': 'La contraseña actual es incorrecta.'
        }
        self.fields['new_password1'].error_messages = {
            'required': 'La nueva contraseña es obligatoria.',
            'min_length': 'La contraseña debe tener al menos 8 caracteres.'
        }
        self.fields['new_password2'].error_messages = {
            'required': 'Debe confirmar la nueva contraseña.'
        }

class FormularioPerfil(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['usuario']

class FormularioActualizarPerfil(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class FormularioResgistrarUsuario(UserCreationForm):
    username = forms.CharField(label='Nombre de usuario')
    password1 = forms.CharField(label='Contraseña')
    password2 = forms.CharField(label='Confirmar Contraseña')
    first_name = forms.CharField(label='Nombre')
    last_name = forms.CharField(label='Apellido')
    email = forms.CharField(label='Correo Electrónico')
    grupo = forms.CharField(label='Tipo de usuario')

class FormularioEditarUsuario(forms.ModelForm):
    grupo = forms.CharField(label='Tipo de usuario', required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class FormularioCambiarPassword(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password']

# ----------------- NUEVOS FORMULARIOS PARA ENCUESTAS -----------------

class EncuestadoForm(forms.ModelForm):
    # ... tus campos de teléfono se mantienen igual ...
    telefono_prefijo = forms.ChoiceField(
        choices=[('', 'Prefijo'), ('0412', '0412'), ('0414', '0414'), ('0416', '0416'), ('0424', '0424'), ('0426', '0426')],
        required=False, label="Prefijo", widget=forms.Select(attrs={'class': 'form-select', 'style': 'max-width: 90px;'})
    )
    telefono_numero = forms.CharField(
        min_length=7, max_length=7, required=False, label="Número",
        widget=forms.TextInput(attrs={'class': 'form-control', 'pattern': r'\d{7}', 'inputmode': 'numeric', 'placeholder': '1234567'})
    )

    class Meta:
        model = Encuestado
        fields = [
            'nombre', 'apellido', 'tipo_cedula', 'cedula_numero', 'genero', 
            'telefono', 'direccion', 'cargo', 'ubicacion_administrativa',
        ]
        widgets = { 'telefono': forms.HiddenInput() }

    def clean_cedula_numero(self):
        """
        Versión final y robusta de la validación de cédula:
        1. Limpia espacios en blanco al inicio y al final.
        2. Verifica duplicados solo contra encuestados 'activos' (no en papelera).
        3. Se auto-excluye al editar para no chocar consigo mismo.
        """
        # Paso 1: Limpiar los datos
        cedula = self.cleaned_data.get('cedula_numero')
        if cedula:
            cedula = cedula.strip() # ¡Esta es la línea clave que limpia los espacios!

        # Construimos la consulta para buscar duplicados
        queryset = Encuestado.objects.filter(
            cedula_numero=cedula, 
            papelera=False
        )

        # Si el formulario es para editar (ya tiene una instancia), excluimos ese mismo objeto
        # de la búsqueda. self.instance.pk se asegura que esto solo se ejecute al editar.
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        # Paso 2: Ejecutar la validación
        if queryset.exists():
            raise forms.ValidationError("Ya existe un encuestado activo con este número de cédula.")
        
        return cedula # Devolvemos la cédula ya limpia

    def clean(self):
        cleaned_data = super().clean()
        # ... tu lógica para limpiar y unir el teléfono se mantiene igual ...
        prefijo = cleaned_data.get('telefono_prefijo')
        numero = cleaned_data.get('telefono_numero')
        if prefijo and numero:
            cleaned_data['telefono'] = f"{prefijo}{numero}"
        elif prefijo and not numero:
            self.add_error('telefono_numero', 'Debe ingresar el número de teléfono si selecciona un prefijo.')
        elif not prefijo and numero:
            self.add_error('telefono_prefijo', 'Debe seleccionar un prefijo si ingresa un número.')
        
        return cleaned_data


    def save(self, commit=True):
        instance = super().save(commit=False)
        telefono = self.cleaned_data.get('telefono', '')
        instance.telefono = telefono
        if commit:
            instance.save()
        return instance

    def clean_direccion(self):
        direccion = (self.cleaned_data.get('direccion') or '').strip()
        if not direccion:
            raise forms.ValidationError("La dirección no puede estar en blanco.")
        return direccion

class EncuestaForm(forms.ModelForm):
    fecha_finalizacion = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    class Meta:
        model = Encuesta
        fields = ['titulo', 'descripcion', 'fecha_finalizacion']
        exclude = ['tipo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la encuesta'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Explicación detallada sobre qué consistirá la encuesta',
                'rows': 3
            }),
        }
        
    def clean_titulo(self):
        titulo = self.cleaned_data['titulo']
        if not re.match(r'^[\w\s\.\,\-\áéíóúÁÉÍÓÚñÑ]+$', titulo):
            raise forms.ValidationError(
                "El título solo puede contener letras, números, espacios y los caracteres . , - _"
            )
        if not titulo.strip():
            raise forms.ValidationError("El título no puede estar vacío.")
        return titulo

    def clean_descripcion(self):
        descripcion = self.cleaned_data['descripcion']
        if not re.match(r'^[\w\s\.\,\-\áéíóúÁÉÍÓÚñÑ]+$', descripcion):
            raise forms.ValidationError(
                "La descripción solo puede contener letras, números, espacios y los caracteres . , - _"
            )
        if not descripcion.strip():
            raise forms.ValidationError("La descripción no puede estar vacía.")
        return descripcion

class ItemEncuestaForm(forms.ModelForm):
    class Meta:
        model = ItemEncuesta
        fields = [
            'texto_pregunta', 'tipo_pregunta', 'tipo_respuesta', 'encuesta', 'orden', 'requerida', 'titulo_campo_texto'
        ]

class ItemRespuestaForm(forms.ModelForm):
    class Meta:
        model = ItemRespuesta
        fields = [
            'item_encuesta', 'encuestado', 'texto_respuesta', 'valor_respuesta'
        ]

class FotografiaForm(forms.ModelForm):
    class Meta:
        model = Fotografia
        fields = ['imagen']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = [
            'encuesta', 'encuestado', 'usuario', 'ubicacion_geografica'
        ]


    def clean_cantidad_habitantes(self):
        cantidad = self.cleaned_data.get('cantidad_habitantes')
        if cantidad is not None and cantidad < 0:
            raise forms.ValidationError("La cantidad de habitantes no puede ser negativa.")
        return cantidad



class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = (
            "<ul>"
            "<li>Su contraseña no debe contener información personal.</li>"
            "<li>Su contraseña debe contener por lo menos 8 caracteres.</li>"
            "<li>Su contraseña debe tener al menos una mayúscula, una minúscula y un caracter especial.</li>"
            "<li>Su contraseña no puede ser completamente numérica.</li>"
            "</ul>"
        )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("La contraseña debe tener al menos una letra mayúscula.")
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("La contraseña debe tener al menos una letra minúscula.")
        if not re.search(r'[^A-Za-z0-9]', password):
            raise forms.ValidationError("La contraseña debe tener al menos un caracter especial.")
        return password
    
class LoginForm(forms.Form):
    username = forms.CharField(label='Usuario')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    captcha = CaptchaField(
        label='Captcha',
        help_text='Ingrese el texto de la imagen para verificar que no es un robot.'
    )

