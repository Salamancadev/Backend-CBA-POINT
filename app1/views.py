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
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

# --------------------------
# Vistas de Usuarios y Autenticación

class RegisterView(APIView):
    permission_classes = [AllowAny]  # Permitir acceso sin autenticación

    def post(self, request):
        # Recibir los datos de registro
        documento = request.data.get("documento")
        password = request.data.get("password")
        nombre = request.data.get("nombre")
        apellido = request.data.get("apellido")
        rol = request.data.get("rol")  # (aprendiz, docente, admin)
        email = request.data.get("email", "")

        # Verificar si el usuario ya existe por documento
        if User.objects.filter(documento=documento).exists():
            return Response({"error": "El usuario ya existe"}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el usuario utilizando el CustomUserManager
        user = User.objects.create_user(documento=documento, nombre=nombre, apellido=apellido, email=email, password=password)

        # Crear el QR para el usuario
        QR.objects.create(usuario=user, codigo=str(uuid.uuid4()))

        return Response({"mensaje": "Usuario registrado correctamente"}, status=status.HTTP_201_CREATED)

class PerfilUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Obtener el perfil del usuario actual
            perfil = User.objects.get(id=request.user.id)  # No es necesario usar "request.user.perfil"
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

        try:
            docente = User.objects.get(id=docente_id)  # Asegurarse de que el docente existe
        except User.DoesNotExist:
            return Response({'error': 'Docente no encontrado'}, status=404)

        evento = Evento.objects.create(
            nombre=nombre,
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            jornada=jornada,
            docente=docente
        )

        return Response({"mensaje": "Evento creado exitosamente"}, status=status.HTTP_201_CREATED)
        
class RegistrarAsistenciaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        evento_id = request.data.get('evento_id')
        metodo = request.data.get('metodo')  # 'qr', 'gps', 'manual'
        estado = request.data.get('estado')  # 'presente', 'ausente', 'tarde'

        try:
            evento = Evento.objects.get(id=evento_id)
        except Evento.DoesNotExist:
            return Response({'error': 'Evento no encontrado'}, status=404)

        usuario = request.user  # Obtener usuario autenticado

        if metodo == 'qr':
            codigo_qr = request.data.get('codigo_qr')
            try:
                qr = QR.objects.get(codigo=codigo_qr, evento=evento)
            except QR.DoesNotExist:
                return Response({'error': 'Código QR no válido para este evento'}, status=400)

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

        if QR.objects.filter(usuario=usuario).exists():
            return Response({'mensaje': 'QR ya generado previamente'}, status=400)

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
    

# --------------------------
# Consultar datos
class GetUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtener todos los usuarios
        usuarios = User.objects.all()  # O también puedes filtrar por parámetros como 'documento' si es necesario.
        serializer = UserSerializer(usuarios, many=True)
        return Response(serializer.data)
    
class GetUserByDocumentoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, documento, format=None):
        try:
            # Buscar el usuario por documento
            usuario = User.objects.get(documento=documento)
            serializer = UserSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
class GetEventosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtener todos los eventos
        eventos = Evento.objects.all()
        serializer = EventoSerializer(eventos, many=True)
        return Response(serializer.data)
    
class GetAsistenciasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtener las asistencias del usuario autenticado
        asistencias = Asistencia.objects.filter(usuario=request.user)
        serializer = AsistenciaSerializer(asistencias, many=True)
        return Response(serializer.data)

class GetQRsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtener los códigos QR generados para el usuario autenticado
        qrs = QR.objects.filter(usuario=request.user)
        serializer = QRSerializer(qrs, many=True)
        return Response(serializer.data)
    

# ---------------------------
# Vista para obtener el token JWT
class LoginView(APIView):
    permission_classes = [AllowAny]  # Permitir el acceso sin autenticación previa

    def post(self, request):
        # Obtener los datos de inicio de sesión
        documento = request.data.get("documento")
        password = request.data.get("password")

        # Autenticar al usuario
        user = authenticate(request, username=documento, password=password)

        if user is not None:
            # Si el usuario existe, generar los tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),  # Token de acceso
                'refresh': str(refresh),  # Token de refresco
            })
        else:
            # Si el usuario no existe o las credenciales son incorrectas
            return Response({"error": "Credenciales incorrectas"}, status=400)