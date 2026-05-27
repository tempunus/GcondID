from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("", views.UserListView.as_view(), name="list"),
    path("novo/", views.UserCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.UserUpdateView.as_view(), name="edit"),
    path("<int:pk>/excluir/", views.UserDeleteView.as_view(), name="delete"),
]
