import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Create output directory
output_dir = "sample_data"
os.makedirs(output_dir, exist_ok=True)


# ============================================================================
# NORMAL TRANSACTION PATTERNS
# ============================================================================

def generate_normal_transactions(account_id, num_transactions=50):
    """Generate normal, legitimate transactions"""
    transactions = []
    base_date = datetime.now() - timedelta(days=90)

    # Normal merchants
    merchants = [
        "Whole Foods Market", "Amazon", "Shell Gas Station", "Starbucks",
        "Netflix", "Spotify", "Gym Membership", "Electric Company",
        "Water Company", "Internet Provider", "Insurance Co", "Pharmacy",
        "Grocery Store", "Restaurant", "Movie Theater", "Hotel Chain"
    ]

    # Normal amounts by merchant
    merchant_amounts = {
        "Whole Foods Market": (50, 150),
        "Amazon": (20, 200),
        "Shell Gas Station": (40, 80),
        "Starbucks": (5, 15),
        "Netflix": (15, 15),
        "Spotify": (10, 10),
        "Gym Membership": (50, 100),
        "Electric Company": (100, 200),
        "Water Company": (50, 100),
        "Internet Provider": (50, 100),
        "Insurance Co": (100, 300),
        "Pharmacy": (20, 100),
        "Grocery Store": (50, 150),
        "Restaurant": (30, 100),
        "Movie Theater": (20, 50),
        "Hotel Chain": (100, 300)
    }

    for i in range(num_transactions):
        merchant = random.choice(merchants)
        min_amt, max_amt = merchant_amounts[merchant]
        amount = round(np.random.normal((min_amt + max_amt) / 2, (max_amt - min_amt) / 4), 2)
        amount = max(min_amt, min(max_amt, amount))  # Clamp to range

        transactions.append({
            "transaction_id": f"TXN_{account_id}_{i:05d}",
            "account_id": account_id,
            "date": (base_date + timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d"),
            "time": f"{random.randint(8, 23):02d}:{random.randint(0, 59):02d}:00",
            "merchant": merchant,
            "amount": amount,
            "currency": "USD",
            "location": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
            "transaction_type": "debit",
            "status": "completed",
            "fraud_indicator": "normal"
        })

    return transactions


# ============================================================================
# FRAUD SCENARIO 1: UNUSUAL TRANSACTION AMOUNTS
# ============================================================================

def generate_unusual_amounts_fraud(account_id, num_frauds=5):
    """Generate transactions with unusual amounts"""
    transactions = []
    base_date = datetime.now() - timedelta(days=30)

    for i in range(num_frauds):
        # Extremely high amounts (300%+ of normal)
        amount = round(np.random.uniform(5000, 15000), 2)

        transactions.append({
            "transaction_id": f"FRAUD_UA_{account_id}_{i:05d}",
            "account_id": account_id,
            "date": (base_date + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "time": f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00",
            "merchant": random.choice(["Luxury Retailer", "Electronics Store", "Jewelry Store"]),
            "amount": amount,
            "currency": "USD",
            "location": random.choice(["Miami", "Las Vegas", "Dubai"]),
            "transaction_type": "debit",
            "status": "completed",
            "fraud_indicator": "unusual_amount"
        })

    return transactions


# ============================================================================
# FRAUD SCENARIO 2: RAPID ACCOUNT DRAINING
# ============================================================================

def generate_account_draining_fraud(account_id):
    """Generate rapid account draining pattern"""
    transactions = []
    base_date = datetime.now() - timedelta(days=1)

    # Multiple transactions within 24 hours
    for i in range(8):
        amount = round(np.random.uniform(2000, 5000), 2)

        transactions.append({
            "transaction_id": f"FRAUD_RD_{account_id}_{i:05d}",
            "account_id": account_id,
            "date": base_date.strftime("%Y-%m-%d"),
            "time": f"{(i * 3) % 24:02d}:{random.randint(0, 59):02d}:00",
            "merchant": random.choice(["Wire Transfer", "International Transfer", "ATM Withdrawal"]),
            "amount": amount,
            "currency": "USD",
            "location": random.choice(["Unknown", "International"]),
            "transaction_type": "debit",
            "status": "completed",
            "fraud_indicator": "rapid_draining"
        })

    return transactions


# ============================================================================
# FRAUD SCENARIO 3: STRUCTURING (SMURFING)
# ============================================================================

def generate_structuring_fraud(account_id, num_frauds=10):
    """Generate structuring pattern - amounts just below reporting threshold"""
    transactions = []
    base_date = datetime.now() - timedelta(days=14)

    for i in range(num_frauds):
        # Just below $10,000 threshold
        amount = round(np.random.uniform(9500, 9999), 2)

        transactions.append({
            "transaction_id": f"FRAUD_ST_{account_id}_{i:05d}",
            "account_id": account_id,
            "date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
            "time": f"{random.randint(9, 17):02d}:{random.randint(0, 59):02d}:00",
            "merchant": random.choice(["Bank Deposit", "Wire Transfer", "Money Transfer Service"]),
            "amount": amount,
            "currency": "USD",
            "location": "Multiple Locations",
            "transaction_type": "debit",
            "status": "completed",
            "fraud_indicator": "structuring"
        })

    return transactions


# ============================================================================
# FRAUD SCENARIO 4: GEOGRAPHIC ANOMALY
# ============================================================================

def generate_geographic_fraud(account_id, num_frauds=3):
    """Generate transactions from impossible locations"""
    transactions = []
    base_date = datetime.now() - timedelta(days=7)

    locations = ["Tokyo", "London", "Sydney", "Dubai", "Hong Kong"]

    for i in range(num_frauds):
        amount = round(np.random.uniform(500, 3000), 2)

        transactions.append({
            "transaction_id": f"FRAUD_GEO_{account_id}_{i:05d}",
            "account_id": account_id,
            "date": (base_date + timedelta(hours=i * 2)).strftime("%Y-%m-%d"),
            "time": f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00",
            "merchant": f"International Merchant - {random.choice(locations)}",
            "amount": amount,
            "currency": random.choice(["JPY", "GBP", "AUD", "AED", "HKD"]),
            "location": random.choice(locations),
            "transaction_type": "debit",
            "status": "completed",
            "fraud_indicator": "geographic_anomaly"
        })

    return transactions


# ============================================================================
# FRAUD SCENARIO 5: DUPLICATE TRANSACTIONS
# ============================================================================

def generate_duplicate_fraud(account_id, num_frauds=3):
    """Generate duplicate transaction fraud"""
    transactions = []
    base_date = datetime.now() - timedelta(days=5)

    for i in range(num_frauds):
        amount = round(np.random.uniform(100, 500), 2)
        merchant = random.choice(["Online Retailer", "Subscription Service", "Utility Company"])

        # Create duplicate transactions
        for j in range(2):
            transactions.append({
                "transaction_id": f"FRAUD_DUP_{account_id}_{i:05d}_{j}",
                "account_id": account_id,
                "date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                "time": f"{random.randint(10, 15):02d}:{random.randint(0, 59):02d}:{j * 30:02d}",
                "merchant": merchant,
                "amount": amount,
                "currency": "USD",
                "location": random.choice(["New York", "Los Angeles"]),
                "transaction_type": "debit",
                "status": "completed",
                "fraud_indicator": "duplicate_transaction"
            })

    return transactions


# ============================================================================
# MAIN DATA GENERATION
# ============================================================================

print("Generating sample financial transaction data...")
print("=" * 70)

all_transactions = []

# Generate data for multiple accounts
accounts = ["ACC_001", "ACC_002", "ACC_003", "ACC_004", "ACC_005"]

for account_id in accounts:
    print(f"\nGenerating data for {account_id}...")

    # Normal transactions
    normal_txns = generate_normal_transactions(account_id, num_transactions=50)
    all_transactions.extend(normal_txns)
    print(f"  ✓ Added {len(normal_txns)} normal transactions")

    # Add fraud scenarios (not for all accounts)
    if account_id in ["ACC_001", "ACC_003", "ACC_005"]:
        # Unusual amounts
        fraud_txns = generate_unusual_amounts_fraud(account_id, num_frauds=5)
        all_transactions.extend(fraud_txns)
        print(f"  ✓ Added {len(fraud_txns)} unusual amount fraud transactions")

        # Rapid draining
        fraud_txns = generate_account_draining_fraud(account_id)
        all_transactions.extend(fraud_txns)
        print(f"  ✓ Added {len(fraud_txns)} rapid draining fraud transactions")

    if account_id in ["ACC_002", "ACC_004"]:
        # Structuring
        fraud_txns = generate_structuring_fraud(account_id, num_frauds=10)
        all_transactions.extend(fraud_txns)
        print(f"  ✓ Added {len(fraud_txns)} structuring fraud transactions")

        # Geographic anomaly
        fraud_txns = generate_geographic_fraud(account_id, num_frauds=3)
        all_transactions.extend(fraud_txns)
        print(f"  ✓ Added {len(fraud_txns)} geographic anomaly fraud transactions")

    if account_id == "ACC_003":
        # Duplicate transactions
        fraud_txns = generate_duplicate_fraud(account_id, num_frauds=3)
        all_transactions.extend(fraud_txns)
        print(f"  ✓ Added {len(fraud_txns)} duplicate fraud transactions")

# Create DataFrame
df = pd.DataFrame(all_transactions)

# Save to CSV
csv_path = os.path.join(output_dir, "transactions.csv")
df.to_csv(csv_path, index=False)
print(f"\n✓ Saved {len(df)} transactions to {csv_path}")

# Save to JSON
json_path = os.path.join(output_dir, "transactions.json")
with open(json_path, 'w') as f:
    json.dump(all_transactions, f, indent=2)
print(f"✓ Saved transactions to {json_path}")

# Generate summary statistics
print("\n" + "=" * 70)
print("SAMPLE DATA SUMMARY")
print("=" * 70)
print(f"Total transactions: {len(df)}")
print(f"Accounts: {df['account_id'].nunique()}")
print(f"Merchants: {df['merchant'].nunique()}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"\nFraud indicators distribution:")
print(df['fraud_indicator'].value_counts())
print(f"\nTransaction amounts statistics:")
print(df['amount'].describe())
print(f"\nTop merchants:")
print(df['merchant'].value_counts().head(10))

print("\n✓ Sample data generation completed successfully!")