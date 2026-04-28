from django.db import models
import uuid


class Merchant(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class LedgerEntry(models.Model):
    ENTRY_TYPES = [
        ('credit', 'Credit'),
        ('payout_hold', 'Payout Hold'),
        ('payout_release', 'Payout Release'),
        ('payout_success', 'Payout Success'),
    ]

    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    amount = models.BigIntegerField()  # stored in paise (IMPORTANT)
    type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    reference_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['merchant']),
        ]

    def __str__(self):
        return f"{self.merchant.name} - {self.type} - {self.amount}"


class Payout(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    amount = models.BigIntegerField()

    # ✅ REQUIRED FIELD (assignment spec)
    bank_account_id = models.CharField(max_length=255)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    # 🔥 Retry + tracking fields
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.status} - {self.amount}"


class IdempotencyKey(models.Model):
    key = models.CharField(max_length=255)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('key', 'merchant')
        indexes = [
            models.Index(fields=['key', 'merchant']),
        ]

    def __str__(self):
        return f"{self.key} - {self.merchant.name}"