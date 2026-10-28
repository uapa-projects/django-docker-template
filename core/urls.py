from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def hello_world_view(request):
    return HttpResponse("<h1>¡Hello World desde Django en Docker! 🚀</h1>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', hello_world_view),  # Ruta raíz
]

# Media en local con runserver (solo con DEBUG=True; en producción los sirve nginx).
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
