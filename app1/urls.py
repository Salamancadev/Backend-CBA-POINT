from django.urls import path
from .views import RegisterView, PerfilUsuarioView, CrearEventoView, RegistrarAsistenciaView, GenerarQRView, HistorialAsistenciaView, GetUsersView, GetUserByDocumentoView, GetEventosView, GetAsistenciasView, GetQRsView, LoginView  # Importamos la vista de Login

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil'),
    path('eventos/', CrearEventoView.as_view(), name='crear_evento'),
    path('asistencias/', RegistrarAsistenciaView.as_view(), name='registrar_asistencia'),
    path('qr/', GenerarQRView.as_view(), name='generar_qr'),
    path('historial/', HistorialAsistenciaView.as_view(), name='historial_asistencia'),
    
    # Rutas para obtener datos
    path('usuarios/', GetUsersView.as_view(), name='get-users'),  # Consulta todos los usuarios
    path('usuarios/<str:documento>/', GetUserByDocumentoView.as_view(), name='get-user-by-documento'),  # Consulta usuario por documento
    path('eventos/', GetEventosView.as_view(), name='get-eventos'),  # Consulta todos los eventos
    path('asistencias/', GetAsistenciasView.as_view(), name='get-asistencias'),  # Consulta asistencias del usuario
    path('qrs/', GetQRsView.as_view(), name='get-qr'),  # Consulta códigos QR generados
    path('login/', LoginView.as_view(), name='login'),  # Ruta para el login y obtener el token
]