from celery import shared_task
from django.db import transaction
import random

from .models import Payout, LedgerEntry


@shared_task(bind=True, max_retries=3)
def process_payout(self, payout_id):
    try:
        payout = Payout.objects.get(id=payout_id)

        #  Block illegal states
        if payout.status not in ['pending', 'processing']:
            return

        #  Move to processing (only once ideally)
        if payout.status == 'pending':
            payout.status = 'processing'

        payout.attempts += 1
        payout.save()

        outcome = random.random()

        #  70% success
        if outcome < 0.7:
            complete_payout(payout)

        #  20% failure
        elif outcome < 0.9:
            fail_payout(payout)

        #  10% hang → retry
        else:
            raise Exception("Simulated processing delay")

    except Exception:
        #  Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=2 ** self.request.retries)

        #  Final failure after max retries
        payout = Payout.objects.get(id=payout_id)
        fail_payout(payout)


@transaction.atomic
def complete_payout(payout):
    #  Strict state machine
    if payout.status != 'processing':
        return  # silently ignore invalid transition

    payout.status = 'completed'
    payout.save()

    #  Final success entry (no money movement, just record)
    LedgerEntry.objects.create(
        merchant=payout.merchant,
        amount=0,
        type='payout_success',
        reference_id=payout.id
    )


@transaction.atomic
def fail_payout(payout):
    #  Strict state machine
    if payout.status != 'processing':
        return

    payout.status = 'failed'
    payout.save()

    #  Return held funds
    LedgerEntry.objects.create(
        merchant=payout.merchant,
        amount=payout.amount,
        type='payout_release',
        reference_id=payout.id
    )