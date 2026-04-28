import { useState, useEffect } from "react";

const API = "http://127.0.0.1:8000/api/v1";

function App() {
  const [balance, setBalance] = useState(0);
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(false);

  // Fetch balance
  const fetchBalance = async () => {
    try {
      const res = await fetch(`${API}/balance`);
      const data = await res.json();
      setBalance(data.balance);
    } catch (err) {
      alert("Cannot connect to backend");
    }
  };

  // Create payout
  const createPayout = async () => {
    if (!amount || Number(amount) <= 0) {
      alert("Enter a valid amount");
      return;
    }

    setLoading(true);

    try {
      const rupees = Number(amount);
      const paise = rupees * 100;

      const res = await fetch(`${API}/payouts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": crypto.randomUUID(),
        },
        body: JSON.stringify({
          amount_paise: paise,
          bank_account_id: "test_account_1",  // ✅ REQUIRED
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Request failed");
      }

      alert("Payout Success");

      setAmount("");
      fetchBalance();
    } catch (err) {
      alert(err.message || "Request Failed");
    }

    setLoading(false);
  };

  useEffect(() => {
    fetchBalance();
  }, []);

  return (
    <div style={{ fontFamily: "Arial", padding: "20px" }}>
      <h1>Playto Dashboard</h1>

      <h2>Balance: ₹{(balance / 100).toFixed(2)}</h2>

      <hr />

      <input
        type="number"
        placeholder="Enter amount in ₹"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        style={{ padding: "8px", marginRight: "10px" }}
      />

      <button
        onClick={createPayout}
        disabled={loading}
        style={{ padding: "8px 16px" }}
      >
        {loading ? "Processing..." : "Send Payout"}
      </button>
    </div>
  );
}

export default App;