from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include([
        path('users/', include('users.urls')),
        path('children/', include('children.urls')),
        path('taskmaster/', include('taskmaster.urls')),
        #path('api/familywallet/', include('wallet.urls')),
       # path('api/insights/', include('insights.urls')),
    ])),

    # Redirect base URL to /api/
    path('', RedirectView.as_view(url='/api/', permanent=False)),
]
