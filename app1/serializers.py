from rest_framework import serializers
from .models import User, Evento, PuntoDeControl, Asistencia, QR

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'documento', 'nombre', 'apellido', 'email', 'rol', 'jornada', 'fecha_registro']

class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ['id', 'nombre', 'tipo', 'fecha_inicio', 'fecha_fin', 'docente', 'activo']

class PuntoDeControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuntoDeControl
        fields = ['id', 'nombre', 'descripcion', 'latitud', 'longitud', 'evento']

class AsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistencia
        fields = ['id', 'usuario', 'evento', 'punto', 'fecha_registro', 'metodo', 'estado']

class QRSerializer(serializers.ModelSerializer):
    class Meta:
        model = QR
        fields = ['id', 'codigo', 'evento', 'punto', 'fecha_creacion', 'fecha_expiracion']