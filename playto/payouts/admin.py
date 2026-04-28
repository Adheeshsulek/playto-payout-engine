from django.contrib import admin
from .models import Merchant, LedgerEntry, Payout, IdempotencyKey

admin.site.register(Merchant)
admin.site.register(LedgerEntry)
admin.site.register(Payout)
admin.site.register(IdempotencyKey)