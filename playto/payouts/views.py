from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction

from .tasks import process_payout
from .models import Merchant, LedgerEntry, Payout, IdempotencyKey
from .utils import get_balance


def get_merchant():
    # Temporary: always return first merchant
    return Merchant.objects.first()


# 🔍 BALANCE
@api_view(['GET'])
def balance_view(request):
    merchant = get_merchant()

    if not merchant:
        return Response({"error": "No merchant found"}, status=400)

    balance = get_balance(merchant)
    return Response({"balance": balance})


# 💸 CREATE PAYOUT
@api_view(['POST'])
def create_payout(request):
    merchant = get_merchant()

    if not merchant:
        return Response({"error": "No merchant found"}, status=400)

    idempotency_key = request.headers.get("Idempotency-Key")
    amount = request.data.get("amount_paise")
    bank_account_id = request.data.get("bank_account_id")

    # Validate input
    if not idempotency_key:
        return Response({"error": "Missing Idempotency-Key"}, status=400)

    if amount is None:
        return Response({"error": "Missing amount"}, status=400)

    if not bank_account_id:
        return Response({"error": "Missing bank_account_id"}, status=400)

    try:
        amount = int(amount)
    except:
        return Response({"error": "Invalid amount"}, status=400)

    if amount <= 0:
        return Response({"error": "Amount must be greater than 0"}, status=400)

    # Idempotency (24-hour window)
    existing = IdempotencyKey.objects.filter(
        key=idempotency_key,
        merchant=merchant,
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).first()

    if existing:
        return Response(existing.response)

    with transaction.atomic():

        # Lock merchant row
        merchant = Merchant.objects.select_for_update().get(id=merchant.id)

        balance = get_balance(merchant)

        if balance < amount:
            return Response({"error": "Insufficient balance"}, status=400)

        # Create payout
        payout = Payout.objects.create(
            merchant=merchant,
            amount=amount,
            status='pending',
            bank_account_id=bank_account_id
        )

        # Hold funds
        LedgerEntry.objects.create(
            merchant=merchant,
            amount=-amount,
            type='payout_hold',
            reference_id=payout.id
        )

        response_data = {
            "payout_id": str(payout.id),
            "status": payout.status
        }

        # Save idempotency response
        IdempotencyKey.objects.create(
            key=idempotency_key,
            merchant=merchant,
            response=response_data
        )

    # Trigger async task AFTER commit
    process_payout.delay(str(payout.id))

    return Response(response_data)


#  SEED DATA (FOR FREE PLAN — NO SHELL)
@api_view(['GET'])
def seed_data(request):
    merchant, _ = Merchant.objects.get_or_create(name="Test Merchant")

    # Add ₹1000 (100000 paise)
    LedgerEntry.objects.create(
        merchant=merchant,
        amount=100000,
        type='credit'
    )

    return Response({"message": "Seed data added"})