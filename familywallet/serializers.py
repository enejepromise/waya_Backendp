from rest_framework import serializers
from decimal import Decimal
from django.db.models import Sum
from .models import FamilyWallet, ChildWallet, Transaction
from children.models import Child
from users.models import User


# --- BASIC SERIALIZERS ---

class ChildBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for Child model."""
    
    class Meta:
        model = Child
        fields = ['id', 'username', 'avatar']
        read_only_fields = ['id']


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'avatar']
        read_only_fields = ['id']


# --- TRANSACTION SERIALIZER (CRUD SUPPORTED) ---

class TransactionSerializer(serializers.ModelSerializer):
    """Handles create/read/update for Transaction model."""
    
    child = ChildBasicSerializer(read_only=True)
    child_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    created_by = UserBasicSerializer(read_only=True)

    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display', 'amount',
            'description', 'status', 'status_display', 'child', 'child_id',
            'created_by', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at', 'created_by']

    def validate_amount(self, value):
        """Ensure amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def validate(self, attrs):
        """Cross-field validation to ensure child is linked when needed."""
        transaction_type = attrs.get('transaction_type')
        child_id = attrs.get('child_id')

        if transaction_type in [Transaction.TYPE_REWARD, Transaction.TYPE_SPENDING] and not child_id:
            raise serializers.ValidationError(f"{transaction_type.title()} transactions require a child.")
        
        return attrs

    def create(self, validated_data):
        """Create a Transaction with relationships to child and creator."""
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['family_wallet'] = getattr(user, 'family_wallet', None)

        child_id = validated_data.pop('child_id', None)
        if child_id:
            try:
                validated_data['child'] = Child.objects.get(id=child_id)
            except Child.DoesNotExist:
                raise serializers.ValidationError("Child not found.")

        return super().create(validated_data)


# --- CHILD WALLET SERIALIZER ---

class ChildWalletSerializer(serializers.ModelSerializer):
    """Serializer for a child's wallet."""
    
    child = ChildBasicSerializer(read_only=True)
    savings_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    recent_transactions = serializers.SerializerMethodField()

    class Meta:
        model = ChildWallet
        fields = [
            'id', 'child', 'balance', 'total_earned', 'total_spent',
            'savings_rate', 'is_active', 'created_at', 'updated_at',
            'recent_transactions'
        ]
        read_only_fields = [
            'id', 'balance', 'total_earned', 'total_spent',
            'created_at', 'updated_at'
        ]

    def get_recent_transactions(self, obj):
        """Return last 5 transactions."""
        recent = obj.child.transactions.all()[:5]
        return TransactionSerializer(recent, many=True, context=self.context).data


# --- FAMILY WALLET SERIALIZER ---

class FamilyWalletSerializer(serializers.ModelSerializer):
    """Serializer for the family wallet overview."""

    parent = UserBasicSerializer(read_only=True)
    total_rewards_sent = serializers.SerializerMethodField()
    total_rewards_pending = serializers.SerializerMethodField()
    children_wallets = serializers.SerializerMethodField()
    recent_transactions = serializers.SerializerMethodField()

    class Meta:
        model = FamilyWallet
        fields = [
            'id', 'parent', 'balance', 'is_active', 'created_at', 'updated_at',
            'total_rewards_sent', 'total_rewards_pending', 'children_wallets',
            'recent_transactions'
        ]
        read_only_fields = ['id', 'parent', 'created_at', 'updated_at']

    def get_total_rewards_sent(self, obj):
        return obj.get_total_rewards_sent()

    def get_total_rewards_pending(self, obj):
        return obj.get_total_rewards_pending()

    def get_children_wallets(self, obj):
        wallets = ChildWallet.objects.for_parent(obj.parent)
        return ChildWalletSerializer(wallets, many=True, context=self.context).data

    def get_recent_transactions(self, obj):
        transactions = obj.transactions.all()[:10]
        return TransactionSerializer(transactions, many=True, context=self.context).data


# --- DASHBOARD STATS SERIALIZER ---

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for summarizing dashboard metrics."""
    
    family_wallet_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_rewards_sent = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_rewards_pending = serializers.DecimalField(max_digits=12, decimal_places=2)
    children_count = serializers.IntegerField()
    total_children_balance = serializers.DecimalField(max_digits=12, decimal_places=2)


# --- ADD FUNDS ---

class AddFundsSerializer(serializers.Serializer):
    """Serializer for adding funds to a wallet."""
    
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(max_length=255, required=False, default="Funds added")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value


# --- COMPLETE TRANSACTIONS ---

class CompleteTransactionSerializer(serializers.Serializer):
    """Mark one or more transactions as complete."""
    
    transaction_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=50
    )


# --- CREATE REWARD ---

class CreateRewardTransactionSerializer(serializers.Serializer):
    """Create a reward transaction for a child."""
    
    child_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    description = serializers.CharField(max_length=255)
    task_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_child_id(self, value):
        user = self.context['request'].user
        if not Child.objects.filter(id=value, parent=user).exists():
            raise serializers.ValidationError("Child not found or does not belong to you.")
        return value

    def validate_task_id(self, value):
        # Placeholder for Task validation logic
        return value


# --- CREATE SPENDING ---

class CreateSpendingTransactionSerializer(serializers.Serializer):
    """Create a spending request from a child."""
    
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    description = serializers.CharField(max_length=255)

    def validate(self, data):
        user = self.context['request'].user
        child_wallet = getattr(user, 'child_profile', None).wallet
        if not child_wallet:
            raise serializers.ValidationError("Wallet not found for this child.")
        if data['amount'] > child_wallet.balance:
            raise serializers.ValidationError("Insufficient funds in your wallet.")
        return data