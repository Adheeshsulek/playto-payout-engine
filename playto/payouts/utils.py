from django.db.models import Sum
from .models import LedgerEntry


def get_balance(merchant):
    result = LedgerEntry.objects.filter(merchant=merchant)\
        .aggregate(total=Sum('amount'))

    return result['total'] or 0