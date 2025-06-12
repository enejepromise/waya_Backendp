from django.urls import path
from .views import InsightListCreateView

urlpatterns = [
    path('', InsightListCreateView.as_view(), name='insight-list-create'),
]