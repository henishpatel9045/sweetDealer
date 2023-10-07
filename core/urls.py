from django.urls import path

from core.views import DashboardView, DealerView

urlpatterns = [
    path("dashboard", DashboardView.as_view(), name="dashboard"),
    path("dealer", DealerView.as_view(), name="dealer"),
]
