from payouts.models import Merchant, LedgerEntry


def run():
    # Clear existing data (optional but useful)
    Merchant.objects.all().delete()

    # Create merchants
    m1 = Merchant.objects.create(name="Agency Alpha")
    m2 = Merchant.objects.create(name="Agency Beta")
    m3 = Merchant.objects.create(name="Agency Gamma")

    # Add credits (paise)
    LedgerEntry.objects.create(merchant=m1, amount=100000, type='credit')  # ₹1000
    LedgerEntry.objects.create(merchant=m1, amount=50000, type='credit')   # ₹500

    LedgerEntry.objects.create(merchant=m2, amount=200000, type='credit')  # ₹2000

    LedgerEntry.objects.create(merchant=m3, amount=75000, type='credit')   # ₹750

    print("Seed data created successfully")