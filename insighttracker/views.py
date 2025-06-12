from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import InsightTracker
from .serializers import InsightTrackerSerializer

class InsightListCreateView(generics.ListCreateAPIView):
    serializer_class = InsightTrackerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InsightTracker.objects.filter(child__parent=self.request.user)

    def perform_create(self, serializer):
        serializer.save()
