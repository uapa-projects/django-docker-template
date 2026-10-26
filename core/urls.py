from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def hello_world_view(request):
    return HttpResponse("<h1>¡Hello World desde Django en Docker! 🚀</h1>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', hello_world_view),  # Ruta raíz
]
