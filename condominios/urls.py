from django.urls import path

from . import views

app_name = "condominios"

urlpatterns = [
    path("", views.CondominiumListView.as_view(), name="list"),
    path("novo/", views.CondominiumCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.CondominiumUpdateView.as_view(), name="edit"),
    path("<int:pk>/excluir/", views.CondominiumDeleteView.as_view(), name="delete"),
]
