from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.geo.urls")),
    path("api/", include("apps.agencies.urls")),
    path("api/", include("apps.listings.urls")),
    path("api/", include("apps.favorites.urls")),
    path("api/", include("apps.mortgage.urls")),
    path("api/", include("apps.telegrambot.urls")),
    path("api/", include("apps.payments.urls")),
    path("api/", include("apps.developers.urls")),
    path("api/", include("apps.bootstrap.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
