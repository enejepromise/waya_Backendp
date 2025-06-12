# from rest_framework import serializers
# from decimal import Decimal
# from django.db.models import Sum
# from .models import FamilyWallet, ChildWallet, Transaction
# from children.models import Child
# from users.models import User


# class ChildBasicSerializer(serializers.ModelSerializer):
#     """Basic child serializer for nested use"""
    
#     class Meta:
#         model = Child
#         fields = ['id', 'username', 'avatar']
#         read_only_fields = ['id']


# class UserBasicSerializer(serializers.ModelSerializer):
#     """Basic user serializer for nested use"""
    
#     class Meta:
#         model = User
#         fields = ['id', 'full_name', 'avatar']
#         read_only_fields = ['id']


# class TransactionSerializer(serializers.ModelSerializer):
#     """Serializer for Transaction model"""
    
#     child = ChildBasicSerializer(read_only=True)
#     child_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
#     created_by = UserBasicSerializer(read_only=True)
#     transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
    
#     class Meta:
#         model = Transaction
#         fields = [
#             'id', 'transaction_type', 'transaction_type_display', 'amount', 
#             'description', 'status', 'status_display', 'child', 'child_id',
#             'created_by', 'created_at', 'completed_at'
#         ]
#         read_only_fields = ['id', 'created_at', 'completed_at', 'created_by']
    
#     def validate_amount(self, value):
#         """Validate transaction amount"""
#         if value <= 0:
#             raise serializers.ValidationError("Amount must be positive")
#         return value
    
#     def validate(self, attrs):
#         """Cross-field validation"""
#         transaction_type = attrs.get('transaction_type')
#         child_id = attrs.get('child_id')
        
#         if transaction_type in [Transaction.TYPE_REWARD, Transaction.TYPE_SPENDING]:
#             if not child_id:
#                 raise serializers.ValidationError(
#                     f"{transaction_type.title()} transactions require a child"
#                 )
        
#         return attrs
    
#     def create(self, validated_data):
#         """Create transaction with proper relationships"""
#         child_id = validated_data.pop('child_id', None)
        
#         if child_id:
#             try:
#                 child = Child.objects.get(id=child_id)
#                 validated_data['child'] = child
#             except Child.DoesNotExist:
#                 raise serializers.ValidationError("Child not found")
        
#         # Set family wallet based on current user
#         user = self.context['request'].user
#         validated_data['family_wallet'] = user.family_wallet
#         validated_data['created_by'] = user
        
#         return super().create(validated_data)


# class ChildWalletSerializer(serializers.ModelSerializer):
#     """Serializer for ChildWallet model"""
    
#     child = ChildBasicSerializer(read_only=True)
#     savings_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
#     recent_transactions = serializers.SerializerMethodField()
    
#     class Meta:
#         model = ChildWallet
#         fields = [
#             'id', 'child', 'balance', 'total_earned', 'total_spent', 
#             'savings_rate', 'is_active', 'created_at', 'updated_at',
#             'recent_transactions'
#         ]
#         read_only_fields = [
#             'id', 'balance', 'total_earned', 'total_spent', 
#             'created_at', 'updated_at'
#         ]
    
#     def get_recent_transactions(self, obj):
#         """Get recent transactions for this child"""
#         transactions = obj.child.transactions.all()[:5]
#         return TransactionSerializer(transactions, many=True, context=self.context).data


# class FamilyWalletSerializer(serializers.ModelSerializer):
#     """Serializer for FamilyWallet model"""
    
#     parent = UserBasicSerializer(read_only=True)
#     total_rewards_sent = serializers.SerializerMethodField()
#     total_rewards_pending = serializers.SerializerMethodField()
#     children_wallets = serializers.SerializerMethodField()
#     recent_transactions = serializers.SerializerMethodField()
    
#     class Meta:
#         model = FamilyWallet
#         fields = [
#             'id', 'parent', 'balance', 'is_active', 'created_at', 'updated_at',
#             'total_rewards_sent', 'total_rewards_pending', 'children_wallets',
#             'recent_transactions'
#         ]
#         read_only_fields = ['id', 'parent', 'created_at', 'updated_at']
    
#     def get_total_rewards_sent(self, obj):
#         """Get total rewards sent"""
#         return obj.get_total_rewards_sent()
    
#     def get_total_rewards_pending(self, obj):
#         """Get total pending rewards"""
#         return obj.get_total_rewards_pending()
    
#     def get_children_wallets(self, obj):
#         """Get all children wallets for this family"""
#         children_wallets = ChildWallet.objects.for_parent(obj.parent)
#         return ChildWalletSerializer(children_wallets, many=True, context=self.context).data
    
#     def get_recent_transactions(self, obj):
#         """Get recent transactions for this family wallet"""
#         transactions = obj.transactions.all()[:10]
#         return TransactionSerializer(transactions, many=True, context=self.context).data


# class DashboardStatsSerializer(serializers.Serializer):
#     """Serializer for dashboard statistics"""
    
#     family_wallet_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
#     total_rewards_sent = serializers.DecimalField(max_digits=12, decimal_places=2)
#     total_rewards_pending = serializers.DecimalField(max_digits=12, decimal_places=2)
#     children_count = serializers.IntegerField()
#     total_children_balance = serializers.DecimalField(max_digits=12, decimal_places=2)


# class AddFundsSerializer(serializers.Serializer):
#     """Serializer for adding funds to family wallet"""
    
#     amount = serializers.DecimalField(max_digits=10, decimal_places=2)
#     description = serializers.CharField(max_length=255, required=False, default="Funds added")
    
#     def validate_amount(self, value):
#         """Validate amount is positive"""
#         if value <= 0:
#             raise serializers.ValidationError("Amount must be positive")
#         return value


# class CompleteTransactionSerializer(serializers.Serializer):
#     """Serializer for completing transactions"""
    
#     transaction_ids = serializers.ListField(
#         child=serializers.UUIDField(),
#         min_length=1,
#         max_length=50
#     )
