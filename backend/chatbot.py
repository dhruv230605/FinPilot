
import os
import json
import numpy as np
from dotenv import load_dotenv
import streamlit as st
from .data_manager import load_user_data
from langchain_openai import AzureChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

load_dotenv()

# Azure OpenAI Configuration
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set")
OPENAI_DEPLOYMENT_ENDPOINT = "https://bfslabopenai.openai.azure.com/"
DEPLOYMENT_NAME = "gpt-4o-mini"
API_VERSION = "2023-05-15"

TOP_K = 5  # number of results to look at

# Initialize session state if not exists
if 'current_user_email' not in st.session_state:
    st.session_state.current_user_email = None

# Initialize LangChain components
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

llm = AzureChatOpenAI(
    openai_api_version=API_VERSION,
    azure_deployment=DEPLOYMENT_NAME,
    azure_endpoint=OPENAI_DEPLOYMENT_ENDPOINT,
    api_key=OPENAI_API_KEY,
    temperature=0.7
)

# Load data
def load_filtered_data():
    data = load_user_data()
    
    # Filter transactions and assets for current user
    filtered_data = {
        "transactions": [tx for tx in data.get("transactions", []) 
                        if tx.get("user_id") == st.session_state.current_user_email],
        "financial_assets": [asset for asset in data.get("financial_assets", [])
                           if asset.get("user_id") == st.session_state.current_user_email],
        "investment_strategies": data.get("investment_strategies", [])
    }
    return filtered_data

def get_embedding(text):
    return embeddings.embed_query(text)

def search_all_categories(query):
    # Load filtered data every time a search is performed
    full_data = load_filtered_data()
    
    results_by_category = {}
    query_embedding = get_embedding(query)
    current_user = st.session_state.current_user_email
    
    for category in full_data.keys():
        data = full_data[category]
        matches = []
        
        # Filter by user for both transactions and financial assets
        if category in ["transactions", "financial_assets"]:
            data = [item for item in data if item.get("user_id") == current_user]
        
        # Improved keyword matching
        query_terms = query.lower().split()
        
        for item in data:
            score = 0
            max_score = 0
            
            # First check keywords field if it exists
            if 'keywords' in item and isinstance(item['keywords'], list):
                for term in query_terms:
                    for keyword in item['keywords']:
                        if term == keyword.lower():
                            max_score = max(max_score, 3)  # Exact keyword match gets highest score
                        elif term in keyword.lower():
                            max_score = max(max_score, 2)  # Partial keyword match gets high score
            
            # Then check other fields
            for term in query_terms:
                term_score = 0
                for key, value in item.items():
                    if isinstance(value, str):
                        # Exact match gets higher score
                        if term == value.lower():
                            term_score += 2
                        # Partial match gets lower score
                        elif term in value.lower():
                            term_score += 1
                    elif isinstance(value, dict):
                        for k, v in value.items():
                            if isinstance(v, str):
                                if term == v.lower():
                                    term_score += 2
                                elif term in v.lower():
                                    term_score += 1
                
                max_score = max(max_score, term_score)
            
            # If we found any matches, add the item with a normalized score
            if max_score > 0:
                # Normalize score between 0 and 1, where 1 is the best match
                normalized_score = 1.0 / (1.0 + max_score)
                matches.append((item, normalized_score))
        
        # Sort by score and take top K
        matches.sort(key=lambda x: x[1])
        results_by_category[category] = matches[:TOP_K]

    return results_by_category

def build_system_prompt(results_by_category):
    current_user = st.session_state.current_user_email
    prompt = f"""You are an expert financial advisor and investment strategist with deep knowledge of markets, portfolio management, and personal finance.
Your responses should be professional, data-driven, and tailored to the user's specific situation.

Current User ID: {current_user}

Expertise Guidelines:
1. Provide personalized investment advice based on the user's current portfolio and risk profile
2. Explain complex financial concepts in clear, accessible language
3. Consider market conditions, economic factors, and investment trends
4. Suggest specific, actionable investment strategies with clear rationale
5. Include risk management considerations in all recommendations
6. Reference relevant financial metrics and performance indicators
7. Consider tax implications and investment costs
8. Maintain a balanced perspective between short-term opportunities and long-term goals

Response Structure:
1. Start with a brief acknowledgment of the user's query
2. Provide a high-level summary of relevant findings
3. Present detailed analysis with specific data points
4. Include actionable recommendations with clear next steps
5. End with a brief conclusion or follow-up suggestion

Data Categories:
- Transactions: Include date, amount, merchant, category, and any relevant notes
- Financial Assets: Include name, type, risk rating, expected return, tenure, and performance metrics
- Investment Strategies: Include risk profile, time horizon, target returns, and allocation blueprint

Here are the relevant items from each category:\n"""

    for cat, items in results_by_category.items():
        prompt += f"\n📊 {cat.upper()}:\n"
        if not items:
            prompt += "No results found.\n"
        for i, (item, score) in enumerate(items):
            if cat == "transactions" and item.get("user_id") != current_user:
                continue
            if cat == "transactions":
                summary = f"Date: {item['timestamp'].split('T')[0]}, Amount: {item['amount']} {item['currency']}, Merchant: {item['merchant_name']}, Category: {item['category']}"
            elif cat == "financial_assets":
                summary = f"Name: {item['name']}, Type: {item['type']}, Risk Rating: {item['risk_rating']}, Expected Return: {item['expected_return']}%, Tenure: {item['tenure']}"
            elif cat == "investment_strategies":
                summary = f"Name: {item['name']}, Risk Profile: {item['risk_profile']}, Time Horizon: {item['time_horizon']}, Target Return: {item['target_annual_return']}%, Allocation: {json.dumps(item['allocation_blueprint'])}"
            else:
                summary = json.dumps(item, indent=2)[:500]
            prompt += f"{i+1}. {summary}\n"
    
    prompt += "\nRemember to maintain a professional tone while being accessible, and always provide context for your recommendations."
    return prompt

def generate_chat_response(user_query):
    results = search_all_categories(user_query)
    system_prompt = build_system_prompt(results)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    try:
        response = llm.invoke(messages)
        # Format the response with markdown for better readability
        formatted_response = response.content.replace("\n\n", "\n").strip()
        return formatted_response
    except Exception as e:
        return f"I apologize, but I encountered an error while processing your request. Please try again or rephrase your question. Error: {str(e)}"

# Export the functions for import
__all__ = ['generate_chat_response', 'search_all_categories']
