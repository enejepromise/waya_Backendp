# from django.db import models
# from children.models import Child
# import uuid

# # Create your models here.

# class InsightTracker(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='insights')
#     activity_type = models.CharField(max_length=100)  # e.g., "task", "reward", "wallet"
#     description = models.TextField()
#     value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Optional
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.child.username} - {self.activity_type} - {self.created_at.strftime('%Y-%m-%d')}"
