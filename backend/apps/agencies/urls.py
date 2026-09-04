from django.urls import path

from .views import AgencyAnalyticsView, AgentDetailView

urlpatterns = [
    path("agents/<str:agent_id>", AgentDetailView.as_view(), name="agent-detail"),
    path("agency/<int:agency_id>/analytics", AgencyAnalyticsView.as_view(), name="agency-analytics"),
]
