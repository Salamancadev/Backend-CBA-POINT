from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

# TABLA DE USUARIOS
class CustomUserManager(BaseUserManager):
    def create_user(self, documento, nombre, apellido, email, password=None):
        if not email:
            raise ValueError('El email debe ser proporcionado')
        user = self.model(documento=documento, nombre=nombre, apellido=apellido, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, documento, nombre, apellido, email, password=None):
        user = self.create_user(documento, nombre, apellido, email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    documento = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=50, choices=[('aprendiz', 'Aprendiz'), ('docente', 'Docente'), ('admin', 'Admin')])
    jornada = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'documento'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'email']

    def __str__(self):
        return self.nombre
    
# TABLA DE EVENTOS
class Evento(models.Model):
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=50, choices=[('inducción', 'Inducción'), ('clase', 'Clase'), ('recorrido', 'Recorrido'), ('evento', 'Evento')])
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    docente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# TABLA DE PUNTOS DE CONTROL
class PuntoDeControl(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre
    
#TABLA DE ASISTENCIAS
class Asistencia(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    punto = models.ForeignKey(PuntoDeControl, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    metodo = models.CharField(max_length=50, choices=[('qr', 'QR'), ('gps', 'GPS'), ('manual', 'Manual')])
    estado = models.CharField(max_length=50, choices=[('presente', 'Presente'), ('ausente', 'Ausente'), ('tarde', 'Tarde')])

    def __str__(self):
        return f"{self.usuario.nombre} - {self.evento.nombre}"

#TABLA DE QR
class QR(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # default=1 asigna el primer usuario
    codigo = models.TextField(unique=True)
    evento = models.ForeignKey(Evento, on_delete=models.SET_NULL, null=True, blank=True)
    punto = models.ForeignKey(PuntoDeControl, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.codigo
