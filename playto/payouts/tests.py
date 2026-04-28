from django.test import TestCase
from .models import Merchant, LedgerEntry
from .utils import get_balance


class LedgerTest(TestCase):
    def test_balance_calculation(self):
        m = Merchant.objects.create(name="Test Merchant")

        LedgerEntry.objects.create(merchant=m, amount=10000, type='credit')
        LedgerEntry.objects.create(merchant=m, amount=-3000, type='payout_hold')

        balance = get_balance(m)

        self.assertEqual(balance, 7000)


class IdempotencyTest(TestCase):
    def test_same_key_not_duplicate(self):
        m = Merchant.objects.create(name="Test Merchant")

        LedgerEntry.objects.create(merchant=m, amount=10000, type='credit')

        balance1 = get_balance(m)
        balance2 = get_balance(m)

        self.assertEqual(balance1, balance2)