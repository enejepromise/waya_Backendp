# import uuid
# from decimal import Decimal
# from django.db import models
# from django.utils import timezone
# from django.core.exceptions import ValidationError
# from users.models import User
# from children.models import Child


# class FamilyWallet(models.Model):
#     """
#     Central family wallet that holds the main family funds.
#     Each family (parent) has one main wallet.
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     parent = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name='family_wallet',
#         limit_choices_to={'role': User.ROLE_PARENT}
#     )
#     balance = models.DecimalField(
#         max_digits=12, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         help_text="Main family wallet balance"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"Family Wallet - {self.parent.full_name} (${self.balance})"
    
#     def add_funds(self, amount, description="Funds added"):
#         """Add funds to family wallet"""
#         if amount <= 0:
#             raise ValidationError("Amount must be positive")
        
#         self.balance += amount
#         self.save()
        
#         # Create transaction record
#         Transaction.objects.create(
#             family_wallet=self,
#             transaction_type=Transaction.TYPE_DEPOSIT,
#             amount=amount,
#             description=description,
#             status=Transaction.STATUS_COMPLETED
#         )
    
#     def has_sufficient_funds(self, amount):
#         """Check if wallet has sufficient funds"""
#         return self.balance >= amount


# class ChildWallet(models.Model):
#     """
#     Individual wallet for each child to track their personal savings/rewards.
#     Separate from the main family wallet.
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     child = models.OneToOneField(
#         Child,
#         on_delete=models.CASCADE,
#         related_name='wallet'
#     )
#     balance = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         help_text="Child's personal wallet balance"
#     )
#     total_earned = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         help_text="Total amount earned by child"
#     )
#     total_spent = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         help_text="Total amount spent by child"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.child.username}'s Wallet (${self.balance})"
    
#     def add_reward(self, amount):
#         """Add reward to child's wallet"""
#         self.balance += amount
#         self.total_earned += amount
#         self.save()
    
#     def spend(self, amount):
#         """Spend from child's wallet"""
#         if amount > self.balance:
#             raise ValidationError("Insufficient funds")
        
#         self.balance -= amount
#         self.total_spent += amount
#         self.save()


# class Transaction(models.Model):
#     """
#     Records all financial transactions in the family wallet system.
#     Handles rewards, spending, deposits, and transfers.
#     """
    
#     # Transaction Types
#     TYPE_REWARD = 'reward'
#     TYPE_SPENDING = 'spending'
#     TYPE_DEPOSIT = 'deposit'
#     TYPE_TRANSFER = 'transfer'
#     TYPE_WITHDRAWAL = 'withdrawal'
    
#     TYPE_CHOICES = [
#         (TYPE_REWARD, 'Reward'),
#         (TYPE_SPENDING, 'Spending'),
#         (TYPE_DEPOSIT, 'Deposit'),
#         (TYPE_TRANSFER, 'Transfer'),
#         (TYPE_WITHDRAWAL, 'Withdrawal'),
#     ]
    
#     # Transaction Status
#     STATUS_PENDING = 'pending'
#     STATUS_COMPLETED = 'completed'
#     STATUS_CANCELLED = 'cancelled'
#     STATUS_FAILED = 'failed'
    
#     STATUS_CHOICES = [
#         (STATUS_PENDING, 'Pending'),
#         (STATUS_COMPLETED, 'Completed'),
#         (STATUS_CANCELLED, 'Cancelled'),
#         (STATUS_FAILED, 'Failed'),
#     ]
    
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
#     # Relationships
#     family_wallet = models.ForeignKey(
#         FamilyWallet,
#         on_delete=models.CASCADE,
#         related_name='transactions'
#     )
#     child = models.ForeignKey(
#         Child,
#         on_delete=models.CASCADE,
#         related_name='transactions',
#         null=True,
#         blank=True,
#         help_text="Child involved in the transaction (for rewards/spending)"
#     )
#     task = models.ForeignKey(
#         'tasks.Task',  # Assuming your Task model is in tasks app
#         on_delete=models.SET_NULL,
#         related_name='transactions',
#         null=True,
#         blank=True,
#         help_text="Task associated with reward transaction"
#     )
    
#     # Transaction Details
#     transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     description = models.TextField(blank=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
    
#     class Meta:
#         ordering = ['-created_at']
#         indexes = [
#             models.Index(fields=['transaction_type', 'status']),
#             models.Index(fields=['child', 'created_at']),
#             models.Index(fields=['family_wallet', 'created_at']),
#         ]
    
#     def __str__(self):
#         child_name = self.child.username if self.child else "Family"
#         return f"{self.get_transaction_type_display()} - {child_name} - ${self.amount} ({self.status})"
    
#     def complete_transaction(self):
#         """Mark transaction as completed and update wallets"""
#         if self.status != self.STATUS_PENDING:
#             raise ValidationError("Only pending transactions can be completed")
        
#         if self.transaction_type == self.TYPE_REWARD:
#             # Transfer from family wallet to child wallet
#             if not self.family_wallet.has_sufficient_funds(self.amount):
#                 raise ValidationError("Insufficient funds in family wallet")
            
#             self.family_wallet.balance -= self.amount
#             self.family_wallet.save()
            
#             if self.child:
#                 child_wallet, created = ChildWallet.objects.get_or_create(child=self.child)
#                 child_wallet.add_reward(self.amount)
        
#         elif self.transaction_type == self.TYPE_SPENDING:
#             # Spend from child wallet
#             if self.child:
#                 child_wallet = self.child.wallet
#                 child_wallet.spend(self.amount)
        
#         self.status = self.STATUS_COMPLETED
#         self.completed_at = timezone.now()
#         self.save()
    
#     def cancel_transaction(self):
#         """Cancel a pending transaction"""
#         if self.status != self.STATUS_PENDING:
#             raise ValidationError("Only pending transactions can be cancelled")
        
#         self.status = self.STATUS_CANCELLED
#         self.save()


# class TransactionCategory(models.Model):
#     """
#     Categories for organizing transactions (optional enhancement)
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=100, unique=True)
#     description = models.TextField(blank=True)
#     color = models.CharField(max_length=7, default='#000000', help_text="Hex color code")
#     parent = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='transaction_categories',
#         limit_choices_to={'role': User.ROLE_PARENT}
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         verbose_name_plural = "Transaction Categories"
#         unique_together = ['name', 'parent']
    
#     def __str__(self):
#         return self.name


# # Add category field to Transaction model (optional)
# # You can add this field to the Transaction model above:
# # category = models.ForeignKey(
# #     TransactionCategory,
# #     on_delete=models.SET_NULL,
# #     null=True,
# #     blank=True,
# #     related_name='transactions'
# # )

# # Signal to create child wallet when child is created
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# @receiver(post_save, sender=Child)
# def create_child_wallet(sender, instance, created, **kwargs):
#     """Automatically create a wallet when a child is created"""
#     if created:
#         ChildWallet.objects.create(child=instance)


# # Signal to create family wallet when parent user is created
# @receiver(post_save, sender=User)
# def create_family_wallet(sender, instance, created, **kwargs):
#     """Automatically create a family wallet when a parent user is created"""
#     if created and instance.role == User.ROLE_PARENT:
#         FamilyWallet.objects.create(parent=instance)

# import uuid
# from decimal import Decimal
# from django.db import models
# from django.utils import timezone
# from django.core.exceptions import ValidationError
# from django.core.validators import MinValueValidator
# from django.db.models import Sum, Q
# from django.contrib.auth import get_user_model
# from children.models import Child

# User = get_user_model()


# class FamilyWalletManager(models.Manager):
#     """Custom manager for FamilyWallet with common queries"""
    
#     def get_by_parent(self, parent):
#         """Get family wallet by parent user"""
#         return self.get(parent=parent)
    
#     def with_balance_gte(self, amount):
#         """Get wallets with balance greater than or equal to amount"""
#         return self.filter(balance__gte=amount)


# class FamilyWallet(models.Model):
#     """
#     Central family wallet that holds the main family funds.
#     Each family (parent) has one main wallet.
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     parent = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name='family_wallet',
#         limit_choices_to={'role': User.ROLE_PARENT}
#     )
#     balance = models.DecimalField(
#         max_digits=12, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         validators=[MinValueValidator(Decimal('0.00'))],
#         help_text="Main family wallet balance"
#     )
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     objects = FamilyWalletManager()
    
#     class Meta:
#         db_table = 'family_wallets'
#         indexes = [
#             models.Index(fields=['parent', 'is_active']),
#             models.Index(fields=['balance']),
#         ]
#         constraints = [
#             models.CheckConstraint(
#                 check=Q(balance__gte=0),
#                 name='positive_balance'
#             )
#         ]
    
#     def __str__(self):
#         return f"Family Wallet - {self.parent.full_name} (${self.balance})"
    
#     def clean(self):
#         """Model validation"""
#         super().clean()
#         if self.balance < 0:
#             raise ValidationError("Balance cannot be negative")
    
#     def add_funds(self, amount, description="Funds added", created_by=None):
#         """Add funds to family wallet with transaction record"""
#         if amount <= 0:
#             raise ValidationError("Amount must be positive")
        
#         self.balance += amount
#         self.save(update_fields=['balance', 'updated_at'])
        
#         # Create transaction record
#         return Transaction.objects.create(
#             family_wallet=self,
#             transaction_type=Transaction.TYPE_DEPOSIT,
#             amount=amount,
#             description=description,
#             status=Transaction.STATUS_COMPLETED,
#             created_by=created_by or self.parent
#         )
    
#     def has_sufficient_funds(self, amount):
#         """Check if wallet has sufficient funds"""
#         return self.balance >= amount
    
#     def get_total_rewards_sent(self, start_date=None, end_date=None):
#         """Get total rewards sent in date range"""
#         queryset = self.transactions.filter(
#             transaction_type=Transaction.TYPE_REWARD,
#             status=Transaction.STATUS_COMPLETED
#         )
#         if start_date:
#             queryset = queryset.filter(created_at__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(created_at__lte=end_date)
        
#         return queryset.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
#     def get_total_rewards_pending(self):
#         """Get total pending rewards"""
#         return self.transactions.filter(
#             transaction_type=Transaction.TYPE_REWARD,
#             status=Transaction.STATUS_PENDING
#         ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')


# class ChildWalletManager(models.Manager):
#     """Custom manager for ChildWallet"""
    
#     def get_by_child(self, child):
#         """Get child wallet by child"""
#         return self.get(child=child)
    
#     def for_parent(self, parent):
#         """Get all child wallets for a parent"""
#         return self.filter(child__parent=parent)


# class ChildWallet(models.Model):
#     """
#     Individual wallet for each child to track their personal savings/rewards.
#     Separate from the main family wallet.
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     child = models.OneToOneField(
#         Child,
#         on_delete=models.CASCADE,
#         related_name='wallet'
#     )
#     balance = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         validators=[MinValueValidator(Decimal('0.00'))],
#         help_text="Child's personal wallet balance"
#     )
#     total_earned = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         validators=[MinValueValidator(Decimal('0.00'))],
#         help_text="Total amount earned by child"
#     )
#     total_spent = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'),
#         validators=[MinValueValidator(Decimal('0.00'))],
#         help_text="Total amount spent by child"
#     )
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     objects = ChildWalletManager()
    
#     class Meta:
#         db_table = 'child_wallets'
#         indexes = [
#             models.Index(fields=['child', 'is_active']),
#             models.Index(fields=['balance']),
#         ]
#         constraints = [
#             models.CheckConstraint(
#                 check=Q(balance__gte=0),
#                 name='child_positive_balance'
#             ),
#             models.CheckConstraint(
#                 check=Q(total_earned__gte=0),
#                 name='child_positive_earned'
#             ),
#             models.CheckConstraint(
#                 check=Q(total_spent__gte=0),
#                 name='child_positive_spent'
#             )
#         ]
    
#     def __str__(self):
#         return f"{self.child.username}'s Wallet (${self.balance})"
    
#     @property
#     def savings_rate(self):
#         """Calculate savings rate as percentage"""
#         if self.total_earned == 0:
#             return Decimal('0.00')
#         return (self.balance / self.total_earned) * 100
    
#     def add_reward(self, amount):
#         """Add reward to child's wallet"""
#         if amount <= 0:
#             raise ValidationError("Amount must be positive")
        
#         self.balance += amount
#         self.total_earned += amount
#         self.save(update_fields=['balance', 'total_earned', 'updated_at'])
    
#     def spend(self, amount):
#         """Spend from child's wallet"""
#         if amount <= 0:
#             raise ValidationError("Amount must be positive")
#         if amount > self.balance:
#             raise ValidationError("Insufficient funds")
        
#         self.balance -= amount
#         self.total_spent += amount
#         self.save(update_fields=['balance', 'total_spent', 'updated_at'])


# class TransactionManager(models.Manager):
#     """Custom manager for Transaction with common queries"""
    
#     def completed(self):
#         """Get completed transactions"""
#         return self.filter(status=self.model.STATUS_COMPLETED)
    
#     def pending(self):
#         """Get pending transactions"""
#         return self.filter(status=self.model.STATUS_PENDING)
    
#     def for_child(self, child):
#         """Get transactions for specific child"""
#         return self.filter(child=child)
    
#     def rewards(self):
#         """Get reward transactions"""
#         return self.filter(transaction_type=self.model.TYPE_REWARD)
    
#     def spending(self):
#         """Get spending transactions"""
#         return self.filter(transaction_type=self.model.TYPE_SPENDING)


# class Transaction(models.Model):
#     """
#     Records all financial transactions in the family wallet system.
#     Handles rewards, spending, deposits, and transfers.
#     """
    
#     # Transaction Types
#     TYPE_REWARD = 'reward'
#     TYPE_SPENDING = 'spending'
#     TYPE_DEPOSIT = 'deposit'
#     TYPE_TRANSFER = 'transfer'
#     TYPE_WITHDRAWAL = 'withdrawal'
    
#     TYPE_CHOICES = [
#         (TYPE_REWARD, 'Reward'),
#         (TYPE_SPENDING, 'Spending'),
#         (TYPE_DEPOSIT, 'Deposit'),
#         (TYPE_TRANSFER, 'Transfer'),
#         (TYPE_WITHDRAWAL, 'Withdrawal'),
#     ]
    
#     # Transaction Status
#     STATUS_PENDING = 'pending'
#     STATUS_COMPLETED = 'completed'
#     STATUS_CANCELLED = 'cancelled'
#     STATUS_FAILED = 'failed'
    
#     STATUS_CHOICES = [
#         (STATUS_PENDING, 'Pending'),
#         (STATUS_COMPLETED, 'Completed'),
#         (STATUS_CANCELLED, 'Cancelled'),
#         (STATUS_FAILED, 'Failed'),
#     ]
    
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
#     # Relationships
#     family_wallet = models.ForeignKey(
#         FamilyWallet,
#         on_delete=models.CASCADE,
#         related_name='transactions'
#     )
#     child = models.ForeignKey(
#         Child,
#         on_delete=models.CASCADE,
#         related_name='transactions',
#         null=True,
#         blank=True,
#         help_text="Child involved in the transaction"
#     )
#     task = models.ForeignKey(
#         'tasks.Task',
#         on_delete=models.SET_NULL,
#         related_name='transactions',
#         null=True,
#         blank=True,
#         help_text="Task associated with reward transaction"
#     )
#     created_by = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         related_name='created_transactions',
#         null=True,
#         blank=True
#     )
    
#     # Transaction Details
#     transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
#     amount = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2,
#         validators=[MinValueValidator(Decimal('0.01'))]
#     )
#     description = models.TextField(blank=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
    
#     objects = TransactionManager()
    
#     class Meta:
#         db_table = 'transactions'
#         ordering = ['-created_at']
#         indexes = [
#             models.Index(fields=['transaction_type', 'status']),
#             models.Index(fields=['child', 'created_at']),
#             models.Index(fields=['family_wallet', 'created_at']),
#             models.Index(fields=['status', 'created_at']),
#         ]
#         constraints = [
#             models.CheckConstraint(
#                 check=Q(amount__gt=0),
#                 name='positive_amount'
#             )
#         ]
    
#     def __str__(self):
#         child_name = self.child.username if self.child else "Family"
#         return f"{self.get_transaction_type_display()} - {child_name} - ${self.amount} ({self.status})"
    
#     def clean(self):
#         """Model validation"""
#         super().clean()
#         if self.amount <= 0:
#             raise ValidationError("Amount must be positive")
        
#         if self.transaction_type in [self.TYPE_REWARD, self.TYPE_SPENDING] and not self.child:
#             raise ValidationError(f"{self.get_transaction_type_display()} transactions require a child")
    
#     def complete_transaction(self):
#         """Mark transaction as completed and update wallets"""
#         if self.status != self.STATUS_PENDING:
#             raise ValidationError("Only pending transactions can be completed")
        
#         try:
#             if self.transaction_type == self.TYPE_REWARD:
#                 self._process_reward()
#             elif self.transaction_type == self.TYPE_SPENDING:
#                 self._process_spending()
#             elif self.transaction_type == self.TYPE_WITHDRAWAL:
#                 self._process_withdrawal()
            
#             self.status = self.STATUS_COMPLETED
#             self.completed_at = timezone.now()
#             self.save(update_fields=['status', 'completed_at'])
            
#         except ValidationError as e:
#             self.status = self.STATUS_FAILED
#             self.save(update_fields=['status'])
#             raise e
    
#     def _process_reward(self):
#         """Process reward transaction"""
#         if not self.family_wallet.has_sufficient_funds(self.amount):
#             raise ValidationError("Insufficient funds in family wallet")
        
#         self.family_wallet.balance -= self.amount
#         self.family_wallet.save(update_fields=['balance', 'updated_at'])
        
#         if self.child:
#             child_wallet, created = ChildWallet.objects.get_or_create(child=self.child)
#             child_wallet.add_reward(self.amount)
    
#     def _process_spending(self):
#         """Process spending transaction"""
#         if self.child:
#             child_wallet = self.child.wallet
#             child_wallet.spend(self.amount)
    
#     def _process_withdrawal(self):
#         """Process withdrawal from family wallet"""
#         if not self.family_wallet.has_sufficient_funds(self.amount):
#             raise ValidationError("Insufficient funds in family wallet")
        
#         self.family_wallet.balance -= self.amount
#         self.family_wallet.save(update_fields=['balance', 'updated_at'])
    
#     def cancel_transaction(self):
#         """Cancel a pending transaction"""
#         if self.status != self.STATUS_PENDING:
#             raise ValidationError("Only pending transactions can be cancelled")
        
#         self.status = self.STATUS_CANCELLED
#         self.save(update_fields=['status'])


# # Signals
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# @receiver(post_save, sender=Child)
# def create_child_wallet(sender, instance, created, **kwargs):
#     """Automatically create a wallet when a child is created"""
#     if created:
#         ChildWallet.objects.create(child=instance)

# @receiver(post_save, sender=User)
# def create_family_wallet(sender, instance, created, **kwargs):
#     """Automatically create a family wallet when a parent user is created"""
#     if created and instance.role == User.ROLE_PARENT:
#         FamilyWallet.objects.create(parent=instance)
