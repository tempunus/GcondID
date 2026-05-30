"""
URL configuration for gcondid project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from django.views.generic import TemplateView

from users.views import CustomLoginView, SignUpView

urlpatterns = [
    path('service-worker.js', TemplateView.as_view(template_name='pwa/service-worker.js', content_type='application/javascript'), name='service_worker'),
    path('', include('dashboard.urls')),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('cadastro/', SignUpView.as_view(), name='signup'),
    path('usuarios/', include('users.urls')),
    path('estoque/', include('estoque.urls')),
    path('chamados/', include('chamados.urls')),
    path('relatorios/', include('relatorios.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
