from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FamilyWalletViewSet, ChildWalletViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'family-wallet', FamilyWalletViewSet, basename='family-wallet')
router.register(r'child-wallets', ChildWalletViewSet, basename='child-wallets')
router.register(r'transactions', TransactionViewSet, basename='transactions')

urlpatterns = [
    path('', include(router.urls)),
]
