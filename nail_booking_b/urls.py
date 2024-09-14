from django.contrib import admin
from django.urls import path, include

urlpatterns: list[path] = [
	path('admin/', admin.site.urls),
	path('api/', include('app.views.routing')),
]
