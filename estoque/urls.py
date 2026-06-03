from django.urls import path

from . import views

app_name = "estoque"

urlpatterns = [
    path("", views.StockItemListView.as_view(), name="list"),
    path("novo/", views.StockItemCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.StockItemUpdateView.as_view(), name="edit"),
    path("<int:pk>/excluir/", views.StockItemDeleteView.as_view(), name="delete"),
    path("<int:pk>/entrada/", views.StockEntryView.as_view(), name="entry"),
    path("<int:pk>/saida/", views.StockExitView.as_view(), name="exit"),
]
