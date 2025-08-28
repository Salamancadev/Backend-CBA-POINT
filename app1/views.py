from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from .models import User, QR, Evento, Asistencia
from .serializers import UserSerializer, EventoSerializer, AsistenciaSerializer, QRSerializer
import uuid

# --------------------------
# Vistas de Usuarios y Autenticación

class RegisterView(APIView):
    def post(self, request):
        # Recibir los datos de registro
        username = request.data.get("username")
        password = request.data.get("password")
        nombre = request.data.get("nombre")
        apellido = request.data.get("apellido")
        rol = request.data.get("rol")  # (aprendiz, docente, admin)
        documento = request.data.get("documento")
        email = request.data.get("email", "")

        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            return Response({"error": "El usuario ya existe"}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el usuario
        user = User.objects.create_user(username=username, password=password)

        # Asociar el perfil con los datos de usuario
        usuario = User.objects.create(
            user=user,
            nombre=nombre,
            apellido=apellido,
            rol=rol,
            documento=documento,
            email=email
        )

        # Crear el QR para el usuario
        QR.objects.create(usuario=usuario, codigo=str(uuid.uuid4()))

        return Response({"mensaje": "Usuario registrado correctamente"}, status=status.HTTP_201_CREATED)

class PerfilUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Obtener el perfil del usuario actual
            perfil = User.objects.get(user=request.user)
            serializer = UserSerializer(perfil)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'Perfil no encontrado'}, status=404)


# --------------------------
# Vistas de Eventos y Gestión de Asistencia

class CrearEventoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        nombre = request.data.get('nombre')
        tipo = request.data.get('tipo')  # 'inducción', 'clase', etc.
        fecha_inicio = request.data.get('fecha_inicio')
        fecha_fin = request.data.get('fecha_fin')
        jornada = request.data.get('jornada', None)
        docente_id = request.data.get('docente_id')

        evento = Evento.objects.create(
            nombre=nombre,
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            jornada=jornada,
            docente_id=docente_id
        )

        return Response({"mensaje": "Evento creado exitosamente"}, status=status.HTTP_201_CREATED)

class RegistrarAsistenciaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        evento_id = request.data.get('evento_id')
        metodo = request.data.get('metodo')  # 'qr', 'gps', 'manual'
        estado = request.data.get('estado')  # 'presente', 'ausente', 'tarde'

        # Verificar si el evento existe
        try:
            evento = Evento.objects.get(id=evento_id)
        except Evento.DoesNotExist:
            return Response({'error': 'Evento no encontrado'}, status=404)

        usuario = request.user  # Obtener usuario autenticado

        # Si es método QR, verificar el código
        if metodo == 'qr':
            codigo_qr = request.data.get('codigo_qr')
            try:
                qr = QR.objects.get(codigo=codigo_qr, evento=evento)
            except QR.DoesNotExist:
                return Response({'error': 'Código QR no válido para este evento'}, status=400)

        # Registrar la asistencia
        asistencia = Asistencia.objects.create(
            usuario=usuario,
            evento=evento,
            metodo=metodo,
            estado=estado
        )

        return Response({"mensaje": "Asistencia registrada correctamente"}, status=status.HTTP_201_CREATED)


# --------------------------
# Vistas de QR

class GenerarQRView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        usuario = request.user  # Usuario autenticado

        # Verificar si ya tiene un QR generado
        if QR.objects.filter(usuario=usuario).exists():
            return Response({'mensaje': 'QR ya generado previamente'}, status=400)

        # Generar un código QR único
        qr_codigo = str(uuid.uuid4())
        qr = QR.objects.create(usuario=usuario, codigo=qr_codigo)

        return Response({'mensaje': 'QR generado correctamente', 'codigo': qr.codigo}, status=201)


# --------------------------
# Historial de Asistencia

class HistorialAsistenciaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user  # Obtener el usuario autenticado
        historial = Asistencia.objects.filter(usuario=usuario)
        serializer = AsistenciaSerializer(historial, many=True)
        return Response(serializer.data)
