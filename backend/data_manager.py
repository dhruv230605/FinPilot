# backend/data_manager.py

import streamlit as st
import json
import os
import pandas as pd

DATA_PATH = "data/large_financial_data.json"

def load_user_data():
    if not os.path.exists(DATA_PATH):
        return {"transactions": [], "financial_assets": []}
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
        # Filter transactions and assets for current user
        if 'current_user_email' in st.session_state and st.session_state.current_user_email:
            data["transactions"] = [tx for tx in data.get("transactions", []) 
                                  if tx.get("user_id") == st.session_state.current_user_email]
            data["financial_assets"] = [asset for asset in data.get("financial_assets", [])
                                      if asset.get("user_id") == st.session_state.current_user_email]
    return data

def save_user_data(data):
    # Load all data first
    all_data = {}
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            all_data = json.load(f)
    
    # Update transactions for current user
    if st.session_state.current_user_email:
        # Remove old transactions for this user
        all_data["transactions"] = [tx for tx in all_data.get("transactions", [])
                                  if tx.get("user_id") != st.session_state.current_user_email]
        # Add new transactions
        all_data["transactions"].extend(data.get("transactions", []))
    
    with open(DATA_PATH, "w") as f:
        json.dump(all_data, f, indent=2)

def export_data_as_json(data):
    json_str = json.dumps(data, indent=2)
    st.download_button("⬇️ Export Data as JSON", json_str, file_name="user_data_export.json")

def delete_transaction_by_id(data, tx_id):
    txs = data.get("transactions", [])
    updated = [t for t in txs if t.get("transaction_id") != tx_id]
    data["transactions"] = updated
    return data

def delete_asset_by_id(data, asset_id):
    assets = data.get("financial_assets", [])
    updated = [a for a in assets if a.get("asset_id") != asset_id]
    data["financial_assets"] = updated
    return data

def show_data_dashboard():
    st.header("📁 Your Data Records")
    data = load_user_data()

    # ─── Transactions Section ───
    st.subheader("🧾 Transactions")
    transactions = data.get("transactions", [])
    if transactions:
        # Create a DataFrame for better display
        tx_data = []
        for tx in transactions:
            tx_data.append({
                "Date": tx["timestamp"].split("T")[0],
                "Merchant": tx["merchant_name"],
                "Amount": f"{tx['amount']} {tx['currency']}",
                "Category": tx["category"].title(),
                "Payment Method": tx["payment_method"].title(),
                "Location": f"{tx['location']['city']}, {tx['location']['country']}"
                # "Tags": ", ".join(tx.get("tags", [])),
                # "Recurring": "Yes" if tx["recurrence"]["is_recurring"] else "No"
            })
        
        # Display as a table with styling
        df_tx = pd.DataFrame(tx_data)
        st.dataframe(
            df_tx,
            column_config={
                "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "Amount": st.column_config.TextColumn("Amount", width="medium"),
                "Merchant": st.column_config.TextColumn("Merchant", width="medium"),
                "Category": st.column_config.TextColumn("Category", width="small"),
                "Payment Method": st.column_config.TextColumn("Payment Method", width="medium"),
                "Location": st.column_config.TextColumn("Location", width="medium")
                # "Tags": st.column_config.TextColumn("Tags", width="large"),
                # "Recurring": st.column_config.TextColumn("Recurring", width="small")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No transactions found.")

    # ─── Financial Assets Section ───
    st.subheader("📈 Financial Assets")
    assets = data.get("financial_assets", [])
    if assets:
        # Create a DataFrame for better display
        asset_data = []
        for asset in assets:
            asset_data.append({
                "Name": asset["name"],
                "Type": asset["type"].title(),
                "Issuer": asset.get("issuer", "N/A"),
                "Tenure": f"{asset.get('tenure', 'N/A')}",
                "Return": f"{asset.get('expected_return', 'N/A')}%",
                "Risk": asset.get("risk_rating", "N/A")
            })
        
        # Display as a table with styling
        df_assets = pd.DataFrame(asset_data)
        st.dataframe(
            df_assets,
            column_config={
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Type": st.column_config.TextColumn("Type", width="medium"),
                "Issuer": st.column_config.TextColumn("Issuer", width="medium"),
                "Tenure": st.column_config.TextColumn("Tenure", width="small"),
                "Return": st.column_config.TextColumn("Return", width="small"),
                "Risk": st.column_config.TextColumn("Risk Rating", width="small")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No financial assets found.")

    # ─── Export Option ───
    st.markdown("---")
    export_data_as_json(data)
