# EXPLAINER.md

## 1. The Ledger

**Balance Calculation**

The merchant balance is derived from a ledger-based model using database aggregation:

```sql
SUM(amount)

All transactions are stored in a single LedgerEntry table where:

Positive values represent credits (incoming funds)
Negative values represent debits (payout holds, releases, etc.)

The balance is calculated using database-level aggregation instead of application-level computation to ensure consistency under concurrent operations.

Why this design

Avoids storing a mutable balance field, preventing drift or corruption
Ensures all financial movements are traceable and auditable
Aligns with real-world payment system architectures
Guarantees correctness under concurrent transactions

2. The Lock (Concurrency Control)

To prevent race conditions during payout creation, row-level locking is used:

merchant = Merchant.objects.select_for_update().get(id=merchant.id)

This ensures that:

Only one transaction can modify a merchant’s balance at a time
Concurrent payout requests are serialized at the database level
Balance validation and deduction occur atomically

Underlying mechanism

This relies on database-level row locks provided by PostgreSQL. It eliminates the classic "check-then-update" race condition by locking the merchant row within a transaction.


3. The Idempotency

Each payout request includes an Idempotency-Key header. The system stores the response for each unique key:

existing = IdempotencyKey.objects.filter(
    key=idempotency_key,
    merchant=merchant,
    created_at__gte=timezone.now() - timedelta(hours=24)
).first()

If a matching key exists:

The stored response is returned
No new payout is created

Edge case handling

If two requests with the same key arrive simultaneously:

The database constraint and transaction handling ensure that only one payout is created
The second request retrieves the stored response

4. The State Machine

The payout lifecycle follows a strict state transition model:

Valid transitions:

pending → processing → completed
pending → processing → failed

Invalid transitions are rejected by design:

Completed payouts cannot revert to pending
Failed payouts cannot transition to completed
No backward transitions are allowed

These constraints are enforced within the payout processing logic.


5. Retry Logic

Payouts that remain in the processing state beyond a defined threshold are retried:

Retry delay follows an exponential backoff strategy
Maximum of 3 retry attempts
If all retries fail, the payout is marked as failed
Held funds are returned to the merchant via a compensating ledger entry


6. AI Audit

Issue identified

Initial AI-generated code suggested checking balance using a direct field:

if merchant.balance >= amount:

This approach is unsafe because:

It depends on a potentially stale value
It does not account for concurrent transactions
It introduces race conditions

Correction implemented

The logic was replaced with:

A ledger-based balance calculation using database aggregation
Row-level locking using select_for_update()

This ensures:

Accurate balance validation
Atomic execution of payout logic
Protection against concurrent overdrafts


Summary

This system ensures:

Strong financial integrity through a ledger-based design
Safe concurrency using database-level locking
Reliable API behavior via idempotency handling
Controlled payout lifecycle through a strict state machine
Robust failure handling with retry mechanisms


---

# What to do next

1. Create `EXPLAINER.md` in your root folder  
2. Paste this content  
3. Run:
   ```bash
   git add EXPLAINER.md
   git commit -m "add explainer"
   git push