from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('coin_handler/', include('coin_handler.urls')),
    path('admin/', admin.site.urls),
]