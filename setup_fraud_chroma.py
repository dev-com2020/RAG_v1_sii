import chromadb
from chromadb.config import Settings
import os
import json
from datetime import datetime

# Initialize ChromaDB client with persistent storage
db_path = "/chroma_db"
os.makedirs(db_path, exist_ok=True)

client = chromadb.PersistentClient(path=db_path)

# Create or get collections
fraud_patterns_collection = client.get_or_create_collection(
    name="fraud_patterns",
    metadata={"description": "Known financial fraud patterns and indicators"}
)

financial_docs_collection = client.get_or_create_collection(
    name="financial_documents",
    metadata={"description": "Financial documents and transactions for analysis"}
)

# Financial Fraud Patterns Knowledge Base
fraud_patterns = [
    {
        "id": "fp_001",
        "pattern": "Unusual Transaction Amounts",
        "description": "Transactions significantly higher or lower than historical average for the account",
        "indicators": ["Amount deviation > 300%", "Sudden large transfers", "Micro-transactions before large transfer"],
        "risk_level": "HIGH",
        "detection_method": "Statistical anomaly detection"
    },
    {
        "id": "fp_002",
        "pattern": "Round Number Transactions",
        "description": "Suspicious round number transactions that may indicate money laundering or fraud",
        "indicators": ["Exactly round amounts (1000, 5000, 10000)", "Multiple round transactions in sequence"],
        "risk_level": "MEDIUM",
        "detection_method": "Pattern matching"
    },
    {
        "id": "fp_003",
        "pattern": "Rapid Account Draining",
        "description": "Multiple transactions in short time period that drain account significantly",
        "indicators": ["5+ transactions within 24 hours", "Total amount > 50% of account balance"],
        "risk_level": "CRITICAL",
        "detection_method": "Time-series analysis"
    },
    {
        "id": "fp_004",
        "pattern": "Unusual Geographic Patterns",
        "description": "Transactions from unusual locations or rapid location changes",
        "indicators": ["Transactions from multiple countries in hours", "Unusual country for account holder"],
        "risk_level": "HIGH",
        "detection_method": "Geolocation analysis"
    },
    {
        "id": "fp_005",
        "pattern": "Structuring (Smurfing)",
        "description": "Multiple transactions just below reporting threshold to avoid detection",
        "indicators": ["Transactions just under 10,000", "Multiple similar amounts", "Frequent deposits/withdrawals"],
        "risk_level": "HIGH",
        "detection_method": "Threshold analysis"
    },
    {
        "id": "fp_006",
        "pattern": "Account Takeover",
        "description": "Unauthorized access and control of legitimate account",
        "indicators": ["New device login", "Password change before transactions", "Unusual transaction patterns"],
        "risk_level": "CRITICAL",
        "detection_method": "Behavioral analysis"
    },
    {
        "id": "fp_007",
        "pattern": "Duplicate Transactions",
        "description": "Same transaction processed multiple times (billing fraud)",
        "indicators": ["Identical amount and recipient within short time", "Multiple charges same merchant"],
        "risk_level": "MEDIUM",
        "detection_method": "Duplicate detection"
    },
    {
        "id": "fp_008",
        "pattern": "Layering",
        "description": "Complex series of transactions to obscure money origin (money laundering)",
        "indicators": ["Multiple transfers between accounts", "Cross-border transfers", "Frequent account changes"],
        "risk_level": "HIGH",
        "detection_method": "Transaction graph analysis"
    },
    {
        "id": "fp_009",
        "pattern": "Velocity Fraud",
        "description": "Multiple transactions from same card/account in impossible timeframe",
        "indicators": ["Transactions from different locations simultaneously", "Multiple transactions within minutes"],
        "risk_level": "CRITICAL",
        "detection_method": "Velocity checking"
    },
    {
        "id": "fp_010",
        "pattern": "Unusual Merchant Categories",
        "description": "Transactions with merchants inconsistent with account holder profile",
        "indicators": ["Gambling/adult content for conservative account", "Luxury purchases for low-income account"],
        "risk_level": "MEDIUM",
        "detection_method": "Profile analysis"
    },
    {
        "id": "fp_011",
        "pattern": "Benign Account Behavior Change",
        "description": "Sudden change in account behavior patterns",
        "indicators": ["New merchant categories", "Different transaction times", "Changed spending patterns"],
        "risk_level": "MEDIUM",
        "detection_method": "Behavioral baseline comparison"
    },
    {
        "id": "fp_012",
        "pattern": "Prepaid Card Fraud",
        "description": "Fraudulent use of prepaid cards or gift cards",
        "indicators": ["Rapid card activation and use", "Multiple small transactions", "Card never used before"],
        "risk_level": "MEDIUM",
        "detection_method": "Prepaid card analysis"
    },
    {
        "id": "fp_013",
        "pattern": "Phishing and Social Engineering",
        "description": "Account compromise through deceptive practices",
        "indicators": ["Credential change from unusual IP", "Unauthorized transfers after phishing",
                       "Account recovery attempts"],
        "risk_level": "CRITICAL",
        "detection_method": "Security event correlation"
    },
    {
        "id": "fp_014",
        "pattern": "Insider Fraud",
        "description": "Fraud committed by employees or insiders with system access",
        "indicators": ["Transactions outside business hours", "Unauthorized access", "Data exfiltration"],
        "risk_level": "CRITICAL",
        "detection_method": "Access log analysis"
    },
    {
        "id": "fp_015",
        "pattern": "Synthetic Identity Fraud",
        "description": "Fraudulent identity created using mix of real and fake information",
        "indicators": ["New account with immediate high activity", "Inconsistent personal information",
                       "Multiple credit applications"],
        "risk_level": "HIGH",
        "detection_method": "Identity verification"
    },
]

# Add fraud patterns to ChromaDB
print("Adding fraud patterns to ChromaDB...")
for pattern in fraud_patterns:
    pattern_text = f"""
Pattern: {pattern['pattern']}
Description: {pattern['description']}
Risk Level: {pattern['risk_level']}
Indicators: {', '.join(pattern['indicators'])}
Detection Method: {pattern['detection_method']}
"""

    fraud_patterns_collection.add(
        ids=[pattern['id']],
        documents=[pattern_text],
        metadatas=[{
            "pattern_name": pattern['pattern'],
            "risk_level": pattern['risk_level'],
            "indicators_count": len(pattern['indicators'])
        }]
    )

print(f"✓ Added {len(fraud_patterns)} fraud patterns")

# Financial Compliance and Regulatory Knowledge
compliance_docs = [
    {
        "id": "comp_001",
        "title": "Anti-Money Laundering (AML) Regulations",
        "content": """
AML regulations require financial institutions to:
1. Know Your Customer (KYC) - Verify customer identity
2. Monitor transactions for suspicious activity
3. Report suspicious transactions to authorities
4. Maintain transaction records for 5+ years
5. Implement customer risk assessment

Red flags for AML:
- Structuring (multiple transactions below reporting threshold)
- Rapid movement of funds
- Transactions inconsistent with customer profile
- Use of shell companies
- Trade-based money laundering
"""
    },
    {
        "id": "comp_002",
        "title": "Know Your Customer (KYC) Requirements",
        "content": """
KYC procedures must include:
1. Customer identification and verification
2. Beneficial ownership identification
3. Purpose and nature of business relationship
4. Risk assessment of customer
5. Ongoing monitoring and updating

Enhanced Due Diligence (EDD) required for:
- High-risk jurisdictions
- Politically exposed persons (PEPs)
- High-value customers
- Unusual transaction patterns
"""
    },
    {
        "id": "comp_003",
        "title": "Suspicious Activity Report (SAR) Triggers",
        "content": """
SARs must be filed when:
1. Transaction amount exceeds $5,000 (or equivalent)
2. Suspicious activity is detected
3. Pattern suggests money laundering
4. Fraud indicators are present
5. Customer behavior is unusual

SAR Filing Requirements:
- File within 30 days of detection
- Include transaction details
- Document suspicious indicators
- Maintain confidentiality
- Keep records for 5 years
"""
    },
    {
        "id": "comp_004",
        "title": "Transaction Monitoring Best Practices",
        "content": """
Effective transaction monitoring includes:
1. Real-time anomaly detection
2. Historical baseline comparison
3. Peer group analysis
4. Geographic risk assessment
5. Merchant category analysis
6. Velocity checking
7. Network analysis

Monitoring should cover:
- Transaction amount and frequency
- Customer location and behavior
- Merchant information
- Device and IP changes
- Cross-border transactions
"""
    },
    {
        "id": "comp_005",
        "title": "Data Security and Privacy",
        "content": """
Financial data security requirements:
1. Encryption in transit and at rest
2. Access controls and authentication
3. Audit logging and monitoring
4. Regular security assessments
5. Incident response procedures
6. Data retention policies
7. GDPR and privacy compliance

Security measures:
- Multi-factor authentication
- Role-based access control
- Data masking for sensitive information
- Regular penetration testing
- Employee training and awareness
"""
    }
]

# Add compliance documents to ChromaDB
print("Adding compliance and regulatory documents...")
for doc in compliance_docs:
    financial_docs_collection.add(
        ids=[doc['id']],
        documents=[doc['content']],
        metadatas=[{
            "title": doc['title'],
            "type": "compliance",
            "date_added": datetime.now().isoformat()
        }]
    )

print(f"✓ Added {len(compliance_docs)} compliance documents")

# Verify collections
print("\nChromaDB Collections Summary:")
print(f"Fraud Patterns Collection: {fraud_patterns_collection.count()} items")
print(f"Financial Documents Collection: {financial_docs_collection.count()} items")

print("\n✓ ChromaDB setup completed successfully!")
print(f"Database location: {db_path}")