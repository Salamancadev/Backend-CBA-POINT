from rest_framework import serializers
from .models import User, Evento, PuntoDeControl, Asistencia, QR
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'rol', 'tipo_documento', 'documento', 'email', 'password', 'confirm', 'acepta_terminos']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm')
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ['id', 'nombre', 'tipo', 'fecha_inicio', 'fecha_fin', 'docente', 'activo']

class PuntoDeControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuntoDeControl
        fields = ['id', 'nombre', 'descripcion', 'latitud', 'longitud', 'evento']
        
    def validate_latitud(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitud inválida")
        return value

class AsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistencia
        fields = ['id', 'usuario', 'evento', 'punto', 'fecha_registro', 'metodo', 'estado']

    def validate_evento(self, value):
        if not value.activo:
            raise serializers.ValidationError("El evento no está activo")
        return value

class QRSerializer(serializers.ModelSerializer):
    class Meta:
        model = QR
        fields = ['id', 'codigo', 'evento', 'punto', 'fecha_creacion', 'fecha_expiracion']

    def validate_fecha_expiracion(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("La fecha de expiración debe ser futura")
        return value