from rest_framework import serializers
from .models import User, Evento, PuntoDeControl, Asistencia, QR
from django.utils import timezone

# --------------------------
# SERIALIZADOR DE USUARIOS
class UserSerializer(serializers.ModelSerializer):
    confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'nombre',
            'apellido',
            'rol',
            'tipo_documento',
            'documento',
            'ficha',
            'email',
            'password',
            'confirm',
            'acepta_terminos',
            'jornada',
            'fecha_registro'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'fecha_registro': {'read_only': True},
        }

    def validate(self, data):
        if data.get('password') != data.get('confirm'):
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

    def update(self, instance, validated_data):
        validated_data.pop('confirm', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

# --------------------------
# SERIALIZADOR DE EVENTOS
class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ['id', 'nombre', 'tipo', 'fecha_inicio', 'fecha_fin', 'jornada', 'docente', 'activo']

# --------------------------
# SERIALIZADOR DE PUNTOS DE CONTROL
class PuntoDeControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuntoDeControl
        fields = ['id', 'nombre', 'descripcion', 'latitud', 'longitud', 'evento', 'activo']

    def validate_latitud(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitud inválida")
        return value

    def validate_longitud(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitud inválida")
        return value

# --------------------------
# SERIALIZADOR DE ASISTENCIAS
class AsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistencia
        fields = ['id', 'usuario', 'evento', 'punto', 'fecha_registro', 'metodo', 'estado']

    def validate_evento(self, value):
        if not value.activo:
            raise serializers.ValidationError("El evento no está activo")
        return value

# --------------------------
# SERIALIZADOR DE CÓDIGOS QR
class QRSerializer(serializers.ModelSerializer):
    class Meta:
        model = QR
        fields = ['id', 'usuario', 'codigo', 'evento', 'punto', 'fecha_creacion', 'fecha_expiracion', 'activo']

    def validate_fecha_expiracion(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("La fecha de expiración debe ser futura")
        return value