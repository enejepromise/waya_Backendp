import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import User
from children.models import Child


class FamilyWallet(models.Model):
    """
    Central family wallet that holds the main family funds.
    Each family (parent) has one main wallet.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='family_wallet',
        limit_choices_to={'role': User.ROLE_PARENT}
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Main family wallet balance"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Family Wallet - {self.parent.full_name} (${self.balance})"

    def add_funds(self, amount, description="Funds added"):
        """Add funds to family wallet"""
        if amount <= 0:
            raise ValidationError("Amount must be positive")

        self.balance += amount
        self.save()

        Transaction.objects.create(
            family_wallet=self,
            transaction_type=Transaction.TYPE_DEPOSIT,
            amount=amount,
            description=description,
            status=Transaction.STATUS_COMPLETED
        )

    def has_sufficient_funds(self, amount):
        """Check if wallet has sufficient funds"""
        return self.balance >= amount


class ChildWallet(models.Model):
    """
    Individual wallet for each child to track their personal savings/rewards.
    Separate from the main family wallet.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.OneToOneField(
        Child,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Child's personal wallet balance"
    )
    total_earned = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total amount earned by child"
    )
    total_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total amount spent by child"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.child.username}'s Wallet (${self.balance})"

    def add_reward(self, amount):
        """Add reward to child's wallet"""
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        self.balance += amount
        self.total_earned += amount
        self.save()

    def spend(self, amount):
        """Spend from child's wallet"""
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        if amount > self.balance:
            raise ValidationError("Insufficient funds")

        self.balance -= amount
        self.total_spent += amount
        self.save()


class Transaction(models.Model):
    """
    Records all financial transactions in the family wallet system.
    Handles rewards, spending, deposits, and transfers.
    """

    # Transaction Types
    TYPE_REWARD = 'reward'
    TYPE_SPENDING = 'spending'
    TYPE_DEPOSIT = 'deposit'
    TYPE_TRANSFER = 'transfer'
    TYPE_WITHDRAWAL = 'withdrawal'

    TYPE_CHOICES = [
        (TYPE_REWARD, 'Reward'),
        (TYPE_SPENDING, 'Spending'),
        (TYPE_DEPOSIT, 'Deposit'),
        (TYPE_TRANSFER, 'Transfer'),
        (TYPE_WITHDRAWAL, 'Withdrawal'),
    ]

    # Transaction Status
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_FAILED, 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relationships
    family_wallet = models.ForeignKey(
        FamilyWallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='transactions',
        null=True,
        blank=True,
        help_text="Child involved in the transaction (for rewards/spending)"
    )
    task = models.ForeignKey(
        'taskmaster.Task',  # ✅ Updated from 'tasks.Task' to 'taskmaster.Task'
        on_delete=models.SET_NULL,
        related_name='transactions',
        null=True,
        blank=True,
        help_text="Task associated with reward transaction"
    )

    # Transaction Details
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['child', 'created_at']),
            models.Index(fields=['family_wallet', 'created_at']),
        ]

    def __str__(self):
        child_name = self.child.username if self.child else "Family"
        return f"{self.get_transaction_type_display()} - {child_name} - ${self.amount} ({self.status})"

    def complete_transaction(self):
        """Mark transaction as completed and update wallets"""
        if self.status != self.STATUS_PENDING:
            raise ValidationError("Only pending transactions can be completed")

        if self.transaction_type == self.TYPE_REWARD:
            if not self.family_wallet.has_sufficient_funds(self.amount):
                raise ValidationError("Insufficient funds in family wallet")

            self.family_wallet.balance -= self.amount
            self.family_wallet.save()

            if self.child:
                child_wallet, _ = ChildWallet.objects.get_or_create(child=self.child)
                child_wallet.add_reward(self.amount)

        elif self.transaction_type == self.TYPE_SPENDING:
            if self.child:
                child_wallet = self.child.wallet
                child_wallet.spend(self.amount)

        self.status = self.STATUS_COMPLETED
        self.completed_at = timezone.now()
        self.save()

    def cancel_transaction(self):
        """Cancel a pending transaction"""
        if self.status != self.STATUS_PENDING:
            raise ValidationError("Only pending transactions can be cancelled")

        self.status = self.STATUS_CANCELLED
        self.save()


class TransactionCategory(models.Model):
    """
    Categories for organizing transactions (optional enhancement)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#000000', help_text="Hex color code")
    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transaction_categories',
        limit_choices_to={'role': User.ROLE_PARENT}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Transaction Categories"
        unique_together = ['name', 'parent']

    def __str__(self):
        return self.name


# Uncomment if needed later:
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# @receiver(post_save, sender=Child)
# def create_child_wallet(sender, instance, created, **kwargs):
#     if created:
#         ChildWallet.objects.create(child=instance)

# @receiver(post_save, sender=User)
# def create_family_wallet(sender, instance, created, **kwargs):
#     if created and instance.role == User.ROLE_PARENT:
#         FamilyWallet.objects.create(parent=instance)
