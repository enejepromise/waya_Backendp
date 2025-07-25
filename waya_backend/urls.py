from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include([
        path('users/', include('users.urls')),
        path('children/', include('children.urls')),
        path('taskmaster/', include('taskmaster.urls')),
        path('familywallet/', include('familywallet.urls')),
        path('insighttracker/', include('insighttracker.urls')),
        path('settings_waya/', include('settings_waya.urls')),
 ])),

    # Redirect base URL to /api/
    path('', RedirectView.as_view(url='/api/', permanent=False)),
]
