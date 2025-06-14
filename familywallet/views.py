from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.db import transaction as db_transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import FamilyWallet, ChildWallet, Transaction
from .serializers import (
    FamilyWalletSerializer,
    ChildWalletSerializer,
    TransactionSerializer,
    DashboardStatsSerializer,
    AddFundsSerializer,
    CompleteTransactionSerializer
)
from children.models import Child


class IsParentPermission(permissions.BasePermission):
    """Allow access only to authenticated parents."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == request.user.ROLE_PARENT
        )


class FamilyWalletViewSet(viewsets.ModelViewSet):
    """Family wallet operations (only for parent users)."""

    serializer_class = FamilyWalletSerializer
    permission_classes = [IsParentPermission]

    def get_queryset(self):
        """Return the family wallet associated with the current parent."""
        return FamilyWallet.objects.filter(parent=self.request.user)

    def get_object(self):
        """Return the specific family wallet for the authenticated parent."""
        return self.request.user.family_wallet

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Return dashboard stats such as balances and reward info."""
        try:
            family_wallet = request.user.family_wallet
            children_wallets = ChildWallet.objects.for_parent(request.user)

            stats = {
                'family_wallet_balance': family_wallet.balance,
                'total_rewards_sent': family_wallet.get_total_rewards_sent(),
                'total_rewards_pending': family_wallet.get_total_rewards_pending(),
                'children_count': children_wallets.count(),
                'total_children_balance': (
                    children_wallets.aggregate(total=Sum('balance'))['total']
                    or Decimal('0.00')
                )
            }

            serializer = DashboardStatsSerializer(stats)
            return Response(serializer.data)

        except FamilyWallet.DoesNotExist:
            return Response(
                {'error': 'Family wallet not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def add_funds(self, request):
        """Add funds to the family wallet."""
        serializer = AddFundsSerializer(data=request.data)

        if serializer.is_valid():
            try:
                family_wallet = request.user.family_wallet
                transaction_obj = family_wallet.add_funds(
                    amount=serializer.validated_data['amount'],
                    description=serializer.validated_data['description'],
                    created_by=request.user
                )

                return Response({
                    'message': 'Funds added successfully',
                    'new_balance': family_wallet.balance,
                    'transaction_id': transaction_obj.id
                })

            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def earnings_chart_data(self, request):
        """Return reward transaction data for chart visualization."""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        transactions = Transaction.objects.filter(
            family_wallet__parent=request.user,
            transaction_type=Transaction.TYPE_REWARD,
            status=Transaction.STATUS_COMPLETED,
            created_at__gte=start_date
        ).select_related('child')

        chart_data = {}

        for tx in transactions:
            date_key = tx.created_at.date().isoformat()
            child_name = tx.child.username if tx.child else 'Unknown'

            chart_data.setdefault(date_key, {})
            chart_data[date_key].setdefault(child_name, Decimal('0.00'))
            chart_data[date_key][child_name] += tx.amount

        return Response(chart_data)

    @action(detail=False, methods=['get'])
    def savings_breakdown(self, request):
        """Return savings breakdown for all children (for donut chart)."""
        children_wallets = ChildWallet.objects.for_parent(request.user)

        breakdown_data = [
            {
                'child_name': wallet.child.username,
                'reward_saved': wallet.balance,
                'reward_spent': wallet.total_spent,
                'total_earned': wallet.total_earned,
                'savings_rate': wallet.savings_rate
            }
            for wallet in children_wallets
        ]

        return Response(breakdown_data)


class ChildWalletViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to children's wallets for the parent."""

    serializer_class = ChildWalletSerializer
    permission_classes = [IsParentPermission]

    def get_queryset(self):
        """Return wallets of children linked to the current parent."""
        return ChildWallet.objects.for_parent(self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    """Transaction operations for a parent's family wallet."""

    serializer_class = TransactionSerializer
    permission_classes = [IsParentPermission]

    def get_queryset(self):
        """Return all transactions for the current parent's family wallet."""
        queryset = Transaction.objects.filter(
            family_wallet__parent=self.request.user
        ).select_related('child', 'created_by')

        # Optional filters
        status_filter = self.request.query_params.get('status')
        type_filter = self.request.query_params.get('type')
        child_id = self.request.query_params.get('child_id')

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if type_filter:
            queryset = queryset.filter(transaction_type=type_filter)

        if child_id:
            queryset = queryset.filter(child_id=child_id)

        return queryset

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a single pending transaction."""
        transaction_obj = self.get_object()

        try:
            with db_transaction.atomic():
                transaction_obj.complete_transaction()

            serializer = self.get_serializer(transaction_obj)
            return Response({
                'message': 'Transaction completed successfully',
                'transaction': serializer.data
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a single pending transaction."""
        transaction_obj = self.get_object()

        try:
            transaction_obj.cancel_transaction()

            serializer = self.get_serializer(transaction_obj)
            return Response({
                'message': 'Transaction cancelled successfully',
                'transaction': serializer.data
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def complete_multiple(self, request):
        """Complete multiple pending transactions at once."""
        serializer = CompleteTransactionSerializer(data=request.data)

        if serializer.is_valid():
            transaction_ids = serializer.validated_data['transaction_ids']

            try:
                with db_transaction.atomic():
                    transactions = Transaction.objects.filter(
                        id__in=transaction_ids,
                        family_wallet__parent=request.user,
                        status=Transaction.STATUS_PENDING
                    )

                    completed_count = 0
                    for tx in transactions:
                        tx.complete_transaction()
                        completed_count += 1

                return Response({
                    'message': f'{completed_count} transactions completed successfully',
                    'completed_count': completed_count
                })

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        """Return the most recent transactions (limited)."""
        limit = int(request.query_params.get('limit', 10))
        transactions = self.get_queryset()[:limit]
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
