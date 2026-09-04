from django.urls import path

from .views import DeveloperListView, ProjectListView

urlpatterns = [
    path("developers", DeveloperListView.as_view(), name="developers"),
    path("projects", ProjectListView.as_view(), name="projects"),
]
