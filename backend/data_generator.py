import json
import random
import uuid
from datetime import datetime, timedelta
import numpy as np
from faker import Faker

fake = Faker()

# Constants
CURRENCIES = ["INR", "USD", "EUR", "GBP"]
CATEGORIES = ["dining", "groceries", "electronics", "travel", "entertainment", "utilities", "healthcare", "education", "investment", "shopping"]
PAYMENT_METHODS = ["credit card", "debit card", "UPI", "net banking", "cash", "wallet"]
CITIES = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad"]
MERCHANTS = {
    "dining": ["Zomato", "Swiggy", "FoodPanda", "Uber Eats", "Domino's", "Pizza Hut", "McDonald's", "KFC"],
    "groceries": ["BigBasket", "Grofers", "Amazon Fresh", "Reliance Fresh", "D-Mart", "More", "Spencer's"],
    "electronics": ["Amazon", "Flipkart", "Croma", "Reliance Digital", "Vijay Sales", "Poorvika"],
    "travel": ["IRCTC", "MakeMyTrip", "Goibibo", "Yatra", "Cleartrip", "Airbnb", "Booking.com"],
    "entertainment": ["Netflix", "Amazon Prime", "Hotstar", "BookMyShow", "PVR", "INOX"],
    "utilities": ["BSES", "Tata Power", "Airtel", "Jio", "Vodafone", "Idea", "MTNL"],
    "healthcare": ["Apollo", "Fortis", "Max", "MedPlus", "1mg", "Netmeds", "Pharmeasy"],
    "education": ["Coursera", "Udemy", "edX", "Unacademy", "Byju's", "WhiteHat Jr"],
    "investment": ["Zerodha", "Upstox", "Groww", "Paytm Money", "ICICI Direct", "HDFC Securities"],
    "shopping": ["Amazon", "Flipkart", "Myntra", "Ajio", "Nykaa", "Purplle", "FirstCry"]
}

def generate_user_details(num_users):
    users = {}
    for i in range(num_users):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        users[email] = "password123"  # Using a default password for all users
    return users

def generate_transaction(user_id, start_date, end_date):
    category = random.choice(CATEGORIES)
    merchant = random.choice(MERCHANTS[category])
    amount = round(random.uniform(100, 10000), 2)
    timestamp = fake.date_time_between(start_date=start_date, end_date=end_date)
    
    return {
        "transaction_id": str(uuid.uuid4()),
        "user_id": user_id,
        "timestamp": timestamp.isoformat(),
        "amount": amount,
        "currency": random.choice(CURRENCIES),
        "category": category,
        "merchant_name": merchant,
        "payment_method": random.choice(PAYMENT_METHODS),
        "location": {
            "geocoordinates": [
                round(random.uniform(8.0, 37.0), 6),  # Latitude for India
                round(random.uniform(68.0, 97.0), 6)   # Longitude for India
            ],
            "city": random.choice(CITIES),
            "country": "India"
        },
        "tags": random.sample(["personal", "business", "recurring", "urgent", "gift"], k=random.randint(0, 3)),
        "recurrence": {
            "is_recurring": random.random() < 0.2,
            "frequency": random.choice(["daily", "weekly", "monthly", "yearly"]) if random.random() < 0.2 else ""
        },
        "metadata": {
            "invoice_details": f"INV-{random.randint(1000, 9999)}",
            "itemized_breakdown": [
                {
                    "product": f"Item {chr(65 + i)}",
                    "quantity": random.randint(1, 5),
                    "price": round(amount / (i + 1), 2)
                } for i in range(random.randint(1, 3))
            ],
            "loyalty_points_earned": random.randint(10, 100)
        },
        "keywords": ["transaction", "finance", "payment"],
        "created_at": timestamp.isoformat(),
        "updated_at": timestamp.isoformat(),
        "expiry_date": "",
        "compatible_user_profiles": random.sample(["frequent_shopper", "tech_savvy", "budget_conscious", "luxury_shopper"], k=random.randint(1, 3)),
        "prerequisites": []
    }

def generate_financial_asset(user_id=None):
    asset_types = ["mutual_fund", "FD", "bond", "equity", "ETF"]
    asset_type = random.choice(asset_types)
    
    return {
        "asset_id": str(uuid.uuid4()),
        "user_id": user_id,  # Added user_id field
        "type": asset_type,
        "name": f"{fake.company()} {asset_type.replace('_', ' ').title()}",
        "issuer": fake.company(),
        "risk_rating": random.randint(1, 5),
        "expected_return": round(random.uniform(5, 15), 2),
        "liquidity": random.choice(["low", "medium", "high"]),
        "minimum_investment_amount": random.choice([1000, 5000, 10000, 50000, 100000]),
        "tenure": f"{random.randint(1, 10)} years",
        "financial_details": {
            "historical_performance": {
                str(year): f"{round(random.uniform(5, 20), 1)}%" 
                for year in range(2020, datetime.now().year)
            },
            "tax_implications": {
                "short_term": f"{random.randint(10, 30)}%",
                "long_term": f"{random.randint(5, 20)}% after 1 year"
            },
            "key_features": random.sample([
                "dividend-paying", "tax-saving", "growth-oriented", 
                "income-focused", "index-tracking", "sector-specific"
            ], k=random.randint(2, 4))
        },
        "metadata": {
            "regulatory_documents": [f"https://example.com/prospectus_{random.randint(1000, 9999)}.pdf"],
            "tags": random.sample(["ESG", "high-growth", "stable", "aggressive", "conservative"], k=random.randint(1, 3))
        },
        "keywords": ["investment", asset_type, "finance"],
        "created_at": fake.date_time_this_year().isoformat(),
        "updated_at": fake.date_time_this_year().isoformat(),
        "expiry_date": "",
        "compatible_user_profiles": random.sample(["investors", "retirees", "young_professionals", "risk_averse"], k=random.randint(1, 3)),
        "prerequisites": random.sample(["Demat account", "KYC", "Bank account"], k=random.randint(1, 2))
    }

def generate_investment_strategy():
    return {
        "strategy_id": str(uuid.uuid4()),
        "name": f"{fake.company()} {random.choice(['Retirement', 'Growth', 'Income', 'Balanced'])} Plan",
        "risk_profile": random.choice(["conservative", "moderate", "aggressive"]),
        "time_horizon": random.choice(["short-term", "medium-term", "long-term"]),
        "target_annual_return": round(random.uniform(5, 15), 1),
        "allocation_blueprint": {
            asset_type: random.randint(10, 40)
            for asset_type in ["FD", "mutual_funds", "bonds", "equity", "gold"]
        },
        "performance_metrics": {
            "backtested_results": f"{round(random.uniform(5, 15), 1)}% CAGR over {random.randint(5, 15)} years",
            "volatility_score": round(random.uniform(1, 5), 1),
            "tax_efficiency_rating": random.choice(["low", "medium", "high"])
        },
        "user_requirements": {
            "minimum_capital": random.choice([10000, 50000, 100000, 500000, 1000000]),
            "recommended_account_types": random.sample(["Demat", "Savings", "NPS", "PPF"], k=random.randint(1, 3))
        },
        "keywords": ["investment", "strategy", "portfolio"],
        "created_at": fake.date_time_this_year().isoformat(),
        "updated_at": fake.date_time_this_year().isoformat(),
        "expiry_date": "",
        "compatible_user_profiles": random.sample(["retirees", "risk_averse", "young_professionals", "high_net_worth"], k=random.randint(1, 3)),
        "prerequisites": random.sample(["KYC", "Demat account", "Bank account"], k=random.randint(1, 2))
    }

def generate_dataset(num_users=100, transactions_per_user=50, assets_per_user=5, num_strategies=20):
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    
    # Generate user details
    users = generate_user_details(num_users)
    
    # Generate transactions and assets for each user
    transactions = []
    financial_assets = []
    
    for user_id in users.keys():
        # Generate transactions
        transactions.extend([
            generate_transaction(user_id, start_date, end_date)
            for _ in range(transactions_per_user)
        ])
        
        # Generate assets for this user
        financial_assets.extend([
            generate_financial_asset(user_id)
            for _ in range(assets_per_user)
        ])
    
    # Generate investment strategies (not user-specific)
    investment_strategies = [
        generate_investment_strategy()
        for _ in range(num_strategies)
    ]
    
    return {
        "users": users,
        "transactions": transactions,
        "financial_assets": financial_assets,
        "investment_strategies": investment_strategies
    }

if __name__ == "__main__":
    # Generate a large dataset
    dataset = generate_dataset(
        num_users=10,          # 1000 users
        transactions_per_user=10,  # 100 transactions per user
        assets_per_user=5,       # 5 assets per user
        num_strategies=50        # 50 investment strategies
    )
    
    # Save users to users.json
    with open("backend/users.json", "w") as f:
        json.dump(dataset["users"], f, indent=2)
    
    # Save other data to large_financial_data.json
    financial_data = {
        "transactions": dataset["transactions"],
        "financial_assets": dataset["financial_assets"],
        "investment_strategies": dataset["investment_strategies"]
    }
    with open("data/large_financial_data.json", "w") as f:
        json.dump(financial_data, f, indent=2)
    
    print(f"Generated dataset with:")
    print(f"- {len(dataset['users'])} users")
    print(f"- {len(dataset['transactions'])} transactions")
    print(f"- {len(dataset['financial_assets'])} financial assets")
    print(f"- {len(dataset['investment_strategies'])} investment strategies") 