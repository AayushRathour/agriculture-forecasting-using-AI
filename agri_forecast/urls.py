"""
URL configuration for agri_forecast project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin disabled - using custom admin at /af-admin/
    # path("admin/", admin.site.urls),
    path("", include("forecast.urls")),  # Include forecast app URLs
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ==============================================================================
# Custom Error Handlers (for production)
# ==============================================================================
handler404 = 'forecast.views.custom_404'
handler500 = 'forecast.views.custom_500'
handler403 = 'forecast.views.custom_403'
handler400 = 'forecast.views.custom_400'
