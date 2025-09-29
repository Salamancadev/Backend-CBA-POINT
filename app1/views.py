from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, QR, Evento, Asistencia
from .serializers import UserSerializer, EventoSerializer, AsistenciaSerializer, QRSerializer
import uuid


# --------------------------
# Usuarios y Autenticación

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            QR.objects.create(usuario=user, codigo=str(uuid.uuid4()))
            return Response({"mensaje": "Usuario registrado correctamente"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        documento = request.data.get("documento")
        password = request.data.get("password")

        try:
            user = User.objects.get(documento=documento)
            if not user.check_password(password):
                raise ValueError("Contraseña incorrecta")
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=400)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        refresh = RefreshToken.for_user(user)
        serializer = UserSerializer(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.rol,
            "user": serializer.data
        }, status=status.HTTP_200_OK)


class PerfilUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --------------------------
# Admin stats para Dashboard

class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_aprendices = User.objects.filter(rol='Aprendiz').count()
        active_events = Evento.objects.filter(activo=True).count()
        today = timezone.now().date()
        today_attendance = Asistencia.objects.filter(fecha_registro__date=today).count()
        total_asistencias = Asistencia.objects.count()

        attendance_percentage = 0
        total_usuarios = User.objects.count()
        total_eventos = Evento.objects.count()
        if total_eventos > 0 and total_usuarios > 0:
            attendance_percentage = round((total_asistencias / (total_eventos * total_usuarios)) * 100, 2)

        return Response({
            "totalAprendices": total_aprendices,
            "activeEvents": active_events,
            "todayAttendance": today_attendance,
            "attendancePercentage": attendance_percentage
        })


# --------------------------
# Gestión de usuarios (CRUD para admin)

class GetUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuarios = User.objects.all()
        serializer = UserSerializer(usuarios, many=True)
        return Response(serializer.data, status=200)


class CreateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        # Si no envían password, usar documento como contraseña
        if not data.get('password'):
            data['password'] = data['documento']
        if not data.get('confirm'):
            data['confirm'] = data['documento']

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            QR.objects.create(usuario=user, codigo=str(uuid.uuid4()))
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response({'mensaje': 'Usuario eliminado correctamente'}, status=200)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)


# --------------------------
# Eventos

class CrearEventoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        nombre = request.data.get('nombre')
        tipo = request.data.get('tipo')
        fecha_inicio = parse_datetime(request.data.get('fecha_inicio'))
        fecha_fin = parse_datetime(request.data.get('fecha_fin'))
        jornada = request.data.get('jornada', None)
        docente_id = request.data.get('docente_id')

        try:
            docente = User.objects.get(id=docente_id)
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
        serializer = EventoSerializer(evento)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetEventosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        eventos = Evento.objects.all()
        serializer = EventoSerializer(eventos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --------------------------
# Asistencias

class RegistrarAsistenciaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        evento_id = request.data.get('evento_id')
        metodo = request.data.get('metodo')
        estado = request.data.get('estado')

        try:
            evento = Evento.objects.get(id=evento_id)
        except Evento.DoesNotExist:
            return Response({'error': 'Evento no encontrado'}, status=404)

        usuario = request.user

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
        serializer = AsistenciaSerializer(asistencia)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetAsistenciasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        asistencias = Asistencia.objects.filter(usuario=request.user)
        serializer = AsistenciaSerializer(asistencias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HistorialAsistenciaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        asistencias = Asistencia.objects.filter(usuario=request.user)
        serializer = AsistenciaSerializer(asistencias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --------------------------
# QR

class GenerarQRView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        usuario = request.user
        evento_id = request.data.get('evento_id')

        try:
            evento = Evento.objects.get(id=evento_id)
        except Evento.DoesNotExist:
            return Response({'error': 'Evento no encontrado'}, status=404)

        if QR.objects.filter(usuario=usuario, evento=evento).exists():
            return Response({'mensaje': 'QR ya generado para este evento'}, status=400)

        qr = QR.objects.create(
            usuario=usuario,
            evento=evento,
            codigo=str(uuid.uuid4())
        )
        serializer = QRSerializer(qr)
        return Response(serializer.data, status=201)


class GetQRsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qrs = QR.objects.filter(usuario=request.user)
        serializer = QRSerializer(qrs, many=True)
        return Response(serializer.data, status=200)


# --------------------------
# Usuarios

class GetUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuarios = User.objects.all()
        serializer = UserSerializer(usuarios, many=True)
        return Response(serializer.data, status=200)


class GetUserByDocumentoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, documento):
        try:
            usuario = User.objects.get(documento=documento)
            serializer = UserSerializer(usuario)
            return Response(serializer.data, status=200)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)