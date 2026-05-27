from django.urls import path

from . import views

app_name = "chamados"

urlpatterns = [
    path("", views.TicketListView.as_view(), name="list"),
    path("novo/", views.TicketCreateView.as_view(), name="create"),
    path("<int:pk>/", views.TicketDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.TicketUpdateView.as_view(), name="edit"),
]
