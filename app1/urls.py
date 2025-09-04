from django.urls import path
from .views import (
    RegisterView, LoginView, PerfilUsuarioView,
    CrearEventoView, GetEventosView,
    RegistrarAsistenciaView, GetAsistenciasView, HistorialAsistenciaView,
    GenerarQRView, GetQRsView,
    GetUsersView, GetUserByDocumentoView
)

urlpatterns = [
    # Autenticación
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil'),

    # Eventos
    path('eventos/crear/', CrearEventoView.as_view(), name='crear_evento'),
    path('eventos/listar/', GetEventosView.as_view(), name='listar_eventos'),

    # Asistencias
    path('asistencias/registrar/', RegistrarAsistenciaView.as_view(), name='registrar_asistencia'),
    path('asistencias/listar/', GetAsistenciasView.as_view(), name='listar_asistencias'),
    path('asistencias/historial/', HistorialAsistenciaView.as_view(), name='historial_asistencia'),

    # QR
    path('qr/crear/', GenerarQRView.as_view(), name='generar_qr'),
    path('qr/listar/', GetQRsView.as_view(), name='listar_qr'),

    # Usuarios
    path('usuarios/', GetUsersView.as_view(), name='listar_usuarios'),
    path('usuarios/<str:documento>/', GetUserByDocumentoView.as_view(), name='usuario_por_documento'),
]
