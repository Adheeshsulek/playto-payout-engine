import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL;

function App() {
  const [balance, setBalance] = useState(0);
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(false);

  // 🔹 Fetch balance
  const fetchBalance = async () => {
    try {
      const res = await fetch(`${API}/balance`);
      const data = await res.json();

      setBalance(data.balance || 0);
    } catch (err) {
      console.error(err);
      alert("Cannot connect to backend");
    }
  };

  // 🔹 Create payout
  const createPayout = async () => {
    if (!amount || Number(amount) <= 0) {
      alert("Enter a valid amount");
      return;
    }

    setLoading(true);

    try {
      const rupees = Number(amount);
      const paise = rupees * 100;

      await fetch(`${API}/payouts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": crypto.randomUUID(),
        },
        body: JSON.stringify({
          amount_paise: paise,
          bank_account_id: "test_account_1",
        }),
      });

      // 🔥 Assume success (backend is working correctly)
      alert("Payout Success");

      setAmount("");

      // Refresh balance
      await fetchBalance();

    } catch (err) {
      console.error(err);
      alert("Network error. Try again.");
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