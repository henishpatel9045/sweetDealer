from django.urls import path

from core.views import DashboardView, DealerView, download_excel

urlpatterns = [
    path("dashboard", DashboardView.as_view(), name="dashboard"),
    path("dealer", DealerView.as_view(), name="dealer"),
    path("export-excel", download_excel, name="export-excel"),
]
