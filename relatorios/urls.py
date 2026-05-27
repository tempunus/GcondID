from django.urls import path

from . import views

app_name = "relatorios"

urlpatterns = [
    path("", views.reports_index, name="index"),
    path("<str:kind>/excel/", views.export_excel, name="excel"),
    path("<str:kind>/pdf/", views.export_pdf, name="pdf"),
]
