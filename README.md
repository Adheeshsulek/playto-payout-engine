# Playto Payout Engine

A minimal payout processing system that simulates how platforms like Stripe or Razorpay manage merchant balances and withdrawals.

---

## Overview

This system allows merchants to:
- View their balance
- Request payouts
- Track payout status

It focuses on solving real-world backend challenges such as:
- Ledger-based accounting
- Concurrency control
- Idempotent API design
- Reliable payout processing

---

## Tech Stack

- Backend: Django, Django REST Framework
- Database: PostgreSQL
- Background Jobs: Celery
- Frontend: React (Vite)
- Deployment:
  - Backend: Render
  - Frontend: Vercel

---

## Live URLs

- Backend API:  
  https://playto-payout-engine-fi43.onrender.com

- Frontend Dashboard:  
  https://playto-payout-engine-green.vercel.app/

---

## API Endpoints

### Get Balance

GET /api/v1/balance

### Create Payout

POST /api/v1/payouts
Headers:
Idempotency-Key: <unique-key>

Body:
{
"amount_paise": 10000,
"bank_account_id": "test_account_1"
}


### Seed Data

GET /api/v1/seed

---

## Key Design Decisions

### Ledger System
- Balance is derived from ledger entries (credits and debits)
- Stored as integer paise (no floats)
- Ensures auditability and consistency

### Concurrency Handling
- Uses database row locking (`select_for_update`)
- Prevents race conditions during payout creation

### Idempotency
- Prevents duplicate payouts using idempotency keys
- Same request returns same response

### State Management
- Strict payout lifecycle:
  - pending → processing → completed
  - pending → processing → failed

---

## Local Setup

### Backend

```bash
git clone <your-repo-url>
cd playto-payout-engine

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver

Frontend
cd frontend
npm install
npm run dev

Notes
This project focuses on backend correctness over UI design
Handles real-world payment system challenges such as concurrency and idempotency
Designed to simulate production-grade payout flows in a simplified environment


---

# AFTER THIS

Run:

```bash
git add README.md
git commit -m "add readme"
git push