import chromadb
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import statistics

import requests
from openai import OpenAI

# --- 1. Konfiguracja ---
# Sprawdź, który serwer jest aktywny i ustaw odpowiedni URL
OLLAMA_URL = "http://localhost:11434"
LM_STUDIO_URL = "http://localhost:1234"

api_url = ""
api_key = "ollama"
model_name = "gemma3:1b"

OLLAMA_AVAILABLE = False
LM_STUDIO_AVAILABLE = False

try:
    requests.get(OLLAMA_URL)
    api_url = f"{OLLAMA_URL}/v1"
    OLLAMA_AVAILABLE = True
    print("✓ Wykryto serwer Ollama.")
except requests.exceptions.ConnectionError:
    try:
        requests.get(LM_STUDIO_URL)
        api_url = f"{LM_STUDIO_URL}/v1"
        LM_STUDIO_AVAILABLE = True
        print("✓ Wykryto serwer LM Studio.")
    except requests.exceptions.ConnectionError:
        print("❌ Nie wykryto aktywnego serwera Ollama ani LM Studio.")
        exit()

# Inicjalizacja klienta OpenAI, który będzie komunikował się z lokalnym serwerem
client = OpenAI(base_url=api_url, api_key=api_key)
# ============================================================================
# FRAUD DETECTION ENGINE
# ============================================================================

class FraudDetectionEngine:
    """Main fraud detection engine using RAG and LLM"""

    def __init__(self, chroma_db_path="/chroma_db"):
        """Initialize the fraud detection engine"""
        self.client = chromadb.PersistentClient(path=chroma_db_path)
        self.fraud_patterns_collection = self.client.get_collection(name="fraud_patterns")
        self.financial_docs_collection = self.client.get_collection(name="financial_documents")
        self.model = "gemma3:1b"  # Primary model
        self.analysis_results = []

    def query_fraud_patterns(self, query: str, n_results: int = 5) -> List[Dict]:
        """Query RAG database for relevant fraud patterns"""
        try:
            results = self.fraud_patterns_collection.query(
                query_texts=[query],
                n_results=n_results
            )

            patterns = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    patterns.append({
                        'pattern': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            return patterns
        except Exception as e:
            print(f"Error querying fraud patterns: {e}")
            return []

    def query_compliance_docs(self, query: str, n_results: int = 3) -> List[Dict]:
        """Query compliance and regulatory documents"""
        try:
            results = self.financial_docs_collection.query(
                query_texts=[query],
                n_results=n_results
            )

            docs = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    docs.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            return docs
        except Exception as e:
            print(f"Error querying compliance docs: {e}")
            return []

    def analyze_with_ollama(self, prompt: str, model: str = None) -> str:
        if model is None:
            model = self.model

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message["content"]
        except Exception as e:
            print(f"Error calling Ollama via OpenAI API-compatible endpoint: {e}")
            return self._generate_mock_analysis(prompt)

    def _generate_mock_analysis(self, prompt: str) -> str:
        """Generate mock analysis when Ollama is not available"""
        # This provides reasonable responses for testing
        if "unusual amount" in prompt.lower():
            return """
FRAUD ANALYSIS RESULT:
- Risk Level: HIGH
- Confidence: 85%
- Pattern Match: Unusual Transaction Amounts detected
- Indicators Found:
  * Transaction amount significantly exceeds historical average (>300%)
  * Amount falls into high-risk category (>$5,000)
  * Merchant category unusual for account holder
- Recommendation: FLAG FOR REVIEW
- Next Steps: Contact account holder to verify transaction legitimacy
"""
        elif "rapid" in prompt.lower() or "draining" in prompt.lower():
            return """
FRAUD ANALYSIS RESULT:
- Risk Level: CRITICAL
- Confidence: 92%
- Pattern Match: Rapid Account Draining detected
- Indicators Found:
  * Multiple transactions within 24-hour period (8 transactions)
  * Total amount represents 40% of account balance
  * Transactions to high-risk destinations
  * Unusual transaction frequency
- Recommendation: IMMEDIATE ACTION REQUIRED
- Next Steps: Block account, contact account holder immediately, initiate investigation
"""
        elif "structuring" in prompt.lower():
            return """
FRAUD ANALYSIS RESULT:
- Risk Level: HIGH
- Confidence: 88%
- Pattern Match: Structuring (Smurfing) detected
- Indicators Found:
  * Multiple transactions just below $10,000 threshold
  * Consistent pattern over 14-day period
  * Amounts: $9,500-$9,999 (all just below reporting threshold)
  * Possible money laundering activity
- Recommendation: FILE SUSPICIOUS ACTIVITY REPORT (SAR)
- Next Steps: Document pattern, file SAR within 30 days, monitor account closely
"""
        else:
            return """
FRAUD ANALYSIS RESULT:
- Risk Level: MEDIUM
- Confidence: 75%
- Pattern Match: Anomaly detected
- Indicators Found:
  * Transaction deviates from normal account behavior
  * Geographic or merchant category unusual
  * Timing inconsistent with account history
- Recommendation: MONITOR AND VERIFY
- Next Steps: Request additional verification, monitor for related transactions
"""

    def statistical_analysis(self, transactions: pd.DataFrame) -> Dict:
        """Perform statistical analysis on transactions"""
        analysis = {
            'total_transactions': int(len(transactions)),
            'total_amount': float(transactions['amount'].sum()),
            'average_amount': float(transactions['amount'].mean()),
            'median_amount': float(transactions['amount'].median()),
            'std_deviation': float(transactions['amount'].std()),
            'min_amount': float(transactions['amount'].min()),
            'max_amount': float(transactions['amount'].max()),
            'amount_outliers': [float(x) for x in self._detect_outliers(transactions['amount'])],
            'frequency_analysis': self._analyze_frequency(transactions),
            'merchant_analysis': self._analyze_merchants(transactions),
            'geographic_analysis': self._analyze_locations(transactions)
        }
        return analysis

    def _detect_outliers(self, series: pd.Series, threshold: float = 3.0) -> List[float]:
        """Detect statistical outliers using z-score"""
        mean = series.mean()
        std = series.std()
        if std == 0:
            return []

        z_scores = [(x - mean) / std for x in series]
        outliers = [series.iloc[i] for i, z in enumerate(z_scores) if abs(z) > threshold]
        return outliers

    def _analyze_frequency(self, transactions: pd.DataFrame) -> Dict:
        """Analyze transaction frequency patterns"""
        trans_copy = transactions.copy()
        trans_copy['date'] = pd.to_datetime(trans_copy['date'])
        daily_counts = trans_copy.groupby('date').size()

        return {
            'transactions_per_day_avg': float(daily_counts.mean()),
            'max_transactions_per_day': int(daily_counts.max()),
            'days_with_activity': int(len(daily_counts)),
            'frequency_anomalies': int(len(daily_counts[daily_counts > daily_counts.mean() + 2 * daily_counts.std()]))
        }

    def _analyze_merchants(self, transactions: pd.DataFrame) -> Dict:
        """Analyze merchant patterns"""
        merchant_stats = transactions.groupby('merchant').agg({
            'amount': ['count', 'sum', 'mean'],
            'transaction_id': 'count'
        }).round(2)

        return {
            'unique_merchants': int(transactions['merchant'].nunique()),
            'top_merchants': transactions['merchant'].value_counts().head(5).to_dict(),
            'new_merchants': int(len(transactions[
                                         transactions['merchant'].str.contains('International|Transfer|ATM', case=False,
                                                                               na=False)]))
        }

    def _analyze_locations(self, transactions: pd.DataFrame) -> Dict:
        """Analyze geographic patterns"""
        location_stats = transactions['location'].value_counts()

        return {
            'unique_locations': int(transactions['location'].nunique()),
            'primary_location': str(location_stats.index[0]) if len(location_stats) > 0 else 'Unknown',
            'location_diversity': int(len(location_stats)),
            'international_transactions': int(
                len(transactions[transactions['location'].isin(['International', 'Unknown'])]))
        }

    def detect_fraud_patterns(self, transactions: pd.DataFrame) -> List[Dict]:
        """Detect fraud patterns in transaction data"""
        detections = []

        # Pattern 1: Unusual amounts
        unusual_amounts = transactions[transactions['amount'] > transactions['amount'].quantile(0.95)]
        if len(unusual_amounts) > 0:
            detections.append({
                'pattern': 'Unusual Transaction Amounts',
                'severity': 'HIGH',
                'count': len(unusual_amounts),
                'transactions': unusual_amounts.to_dict('records')[:3]
            })

        # Pattern 2: Rapid draining
        daily_txn = transactions.groupby('date').size()
        high_frequency_days = daily_txn[daily_txn > 5]
        if len(high_frequency_days) > 0:
            detections.append({
                'pattern': 'Rapid Account Draining',
                'severity': 'CRITICAL',
                'count': len(high_frequency_days),
                'days_affected': high_frequency_days.to_dict()
            })

        # Pattern 3: Structuring
        structuring_txns = transactions[
            (transactions['amount'] >= 9500) &
            (transactions['amount'] <= 9999)
            ]
        if len(structuring_txns) > 3:
            detections.append({
                'pattern': 'Structuring (Smurfing)',
                'severity': 'HIGH',
                'count': len(structuring_txns),
                'transactions': structuring_txns.to_dict('records')[:3]
            })

        # Pattern 4: Geographic anomalies
        international_txns = transactions[
            transactions['location'].isin(['International', 'Unknown'])
        ]
        if len(international_txns) > 2:
            detections.append({
                'pattern': 'Geographic Anomalies',
                'severity': 'MEDIUM',
                'count': len(international_txns),
                'transactions': international_txns.to_dict('records')[:3]
            })

        # Pattern 5: Duplicate transactions
        duplicate_txns = transactions[transactions['fraud_indicator'] == 'duplicate_transaction']
        if len(duplicate_txns) > 0:
            detections.append({
                'pattern': 'Duplicate Transactions',
                'severity': 'MEDIUM',
                'count': len(duplicate_txns),
                'transactions': duplicate_txns.to_dict('records')[:3]
            })

        return detections

    def generate_report(self, account_id: str, transactions: pd.DataFrame) -> Dict:
        """Generate comprehensive fraud analysis report"""
        print(f"\n{'=' * 70}")
        print(f"FRAUD DETECTION ANALYSIS REPORT")
        print(f"Account: {account_id}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 70}\n")

        # Statistical analysis
        print("1. STATISTICAL ANALYSIS")
        print("-" * 70)
        stats = self.statistical_analysis(transactions)
        print(f"Total Transactions: {stats['total_transactions']}")
        print(f"Total Amount: ${stats['total_amount']:,.2f}")
        print(f"Average Transaction: ${stats['average_amount']:,.2f}")
        print(f"Median Transaction: ${stats['median_amount']:,.2f}")
        print(f"Std Deviation: ${stats['std_deviation']:,.2f}")
        print(f"Amount Range: ${stats['min_amount']:,.2f} - ${stats['max_amount']:,.2f}")
        print(f"Outliers Detected: {len(stats['amount_outliers'])}")
        print(f"Unique Merchants: {stats['merchant_analysis']['unique_merchants']}")
        print(f"Unique Locations: {stats['geographic_analysis']['unique_locations']}")

        # Fraud pattern detection
        print("\n2. FRAUD PATTERN DETECTION")
        print("-" * 70)
        detections = self.detect_fraud_patterns(transactions)

        if detections:
            for detection in detections:
                print(f"\n  ⚠️  Pattern: {detection['pattern']}")
                print(f"     Severity: {detection['severity']}")
                print(f"     Occurrences: {detection['count']}")
        else:
            print("No suspicious patterns detected")

        # RAG-based analysis
        print("\n3. RAG-BASED FRAUD PATTERN MATCHING")
        print("-" * 70)

        for detection in detections[:3]:  # Analyze top 3 detections
            pattern_name = detection['pattern']
            print(f"\n  Analyzing: {pattern_name}")

            # Query RAG database
            relevant_patterns = self.query_fraud_patterns(pattern_name, n_results=3)
            if relevant_patterns:
                print(f"  Related patterns from knowledge base:")
                for rp in relevant_patterns:
                    metadata = rp.get('metadata', {})
                    risk = metadata.get('risk_level', 'UNKNOWN')
                    print(f"    - Risk Level: {risk}")

            # Query compliance documents
            compliance_docs = self.query_compliance_docs(pattern_name, n_results=2)
            if compliance_docs:
                print(f"  Relevant regulations:")
                for doc in compliance_docs:
                    metadata = doc.get('metadata', {})
                    title = metadata.get('title', 'Unknown')
                    print(f"    - {title}")

        # LLM Analysis
        print("\n4. DETAILED LLM ANALYSIS")
        print("-" * 70)

        for detection in detections[:2]:  # Analyze top 2 with LLM
            pattern_name = detection['pattern']
            severity = detection['severity']
            count = detection['count']

            prompt = f"""
Analyze the following financial fraud pattern:

Pattern: {pattern_name}
Severity Level: {severity}
Number of Occurrences: {count}
Account: {account_id}

Based on your knowledge of financial fraud detection and AML regulations:
1. What are the key risk indicators?
2. What regulatory requirements apply?
3. What immediate actions should be taken?
4. What is the recommended investigation approach?

Provide a concise, actionable analysis.
"""

            print(f"\n  Pattern: {pattern_name}")
            print("  " + "-" * 66)
            analysis = self.analyze_with_ollama(prompt)
            # Print first 500 chars of analysis
            print(analysis[:500] if len(analysis) > 500 else analysis)

        # Risk Score
        print("\n5. OVERALL RISK ASSESSMENT")
        print("-" * 70)
        risk_score = self._calculate_risk_score(detections, stats)
        print(f"Risk Score: {risk_score['score']:.1f}/100")
        print(f"Risk Level: {risk_score['level']}")
        print(f"Recommendation: {risk_score['recommendation']}")

        # Summary
        print("\n6. SUMMARY AND RECOMMENDATIONS")
        print("-" * 70)
        print(f"Total Fraud Patterns Detected: {len(detections)}")
        print(f"Critical Alerts: {len([d for d in detections if d['severity'] == 'CRITICAL'])}")
        print(f"High Risk Alerts: {len([d for d in detections if d['severity'] == 'HIGH'])}")
        print(f"Medium Risk Alerts: {len([d for d in detections if d['severity'] == 'MEDIUM'])}")

        print("\nRecommended Actions:")
        if risk_score['level'] == 'CRITICAL':
            print("  1. ⛔ IMMEDIATELY BLOCK ACCOUNT")
            print("  2. 📞 Contact account holder for verification")
            print("  3. 📋 File Suspicious Activity Report (SAR)")
            print("  4. 🔍 Initiate full fraud investigation")
        elif risk_score['level'] == 'HIGH':
            print("  1. 🚨 Flag account for review")
            print("  2. 📞 Contact account holder to verify transactions")
            print("  3. 📋 Prepare SAR documentation")
            print("  4. 📊 Monitor account closely for 30 days")
        else:
            print("  1. 👁️  Monitor account for additional anomalies")
            print("  2. 📊 Continue regular transaction monitoring")
            print("  3. 📝 Document findings for compliance records")

        print(f"\n{'=' * 70}\n")

        return {
            'account_id': account_id,
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'detections': detections,
            'risk_score': risk_score
        }

    def _calculate_risk_score(self, detections: List[Dict], stats: Dict) -> Dict:
        """Calculate overall risk score"""
        score = 0

        # Base score from detections
        for detection in detections:
            if detection['severity'] == 'CRITICAL':
                score += 40
            elif detection['severity'] == 'HIGH':
                score += 25
            elif detection['severity'] == 'MEDIUM':
                score += 10

        # Adjust based on outliers
        score += min(len(stats['amount_outliers']) * 5, 20)

        # Cap at 100
        score = min(score, 100)

        # Determine risk level
        if score >= 80:
            level = 'CRITICAL'
            recommendation = 'Immediate action required - block account and investigate'
        elif score >= 60:
            level = 'HIGH'
            recommendation = 'Flag for review and enhanced monitoring'
        elif score >= 40:
            level = 'MEDIUM'
            recommendation = 'Monitor closely and request verification'
        else:
            level = 'LOW'
            recommendation = 'Continue normal monitoring'

        return {
            'score': score,
            'level': level,
            'recommendation': recommendation
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "=" * 70)
    print("FINANCIAL FRAUD DETECTION SYSTEM")
    print("Using ChromaDB RAG + Ollama (Llama3/DeepSeek)")
    print("=" * 70)

    # Initialize engine
    engine = FraudDetectionEngine()

    # Load sample data
    data_path = "sample_data/transactions.csv"
    if not os.path.exists(data_path):
        print(f"Error: Sample data not found at {data_path}")
        return

    df = pd.read_csv(data_path)
    print(f"\nLoaded {len(df)} transactions from sample data")

    # Analyze each account
    accounts = df['account_id'].unique()
    all_reports = []

    for account_id in accounts:
        account_txns = df[df['account_id'] == account_id]
        report = engine.generate_report(account_id, account_txns)
        all_reports.append(report)

    # Save reports
    reports_path = "analysis_reports.json"
    with open(reports_path, 'w') as f:
        json.dump(all_reports, f, indent=2, default=str)

    print(f"\n✓ Analysis reports saved to {reports_path}")

    # Summary
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Accounts analyzed: {len(accounts)}")
    print(f"Reports generated: {len(all_reports)}")
    print(f"Total fraud patterns detected: {sum(len(r['detections']) for r in all_reports)}")


if __name__ == "__main__":
    main()