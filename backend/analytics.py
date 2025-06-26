import streamlit as st
import json
import os
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.ticker import MaxNLocator
from .chatbot import llm  # Import the existing LLM
import numpy as np

DATA_PATH = "data/large_financial_data.json"

#this function loads the data from the json file and filters it for the current user and returns
def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
            # Filtering here
            if st.session_state.current_user_email:
                filtered_transactions = [tx for tx in data.get("transactions", []) 
                                      if tx.get("user_id") == st.session_state.current_user_email]
                filtered_assets = [asset for asset in data.get("financial_assets", [])
                                      if asset.get("user_id") == st.session_state.current_user_email]
                data["transactions"] = filtered_transactions
                data["financial_assets"] = filtered_assets
            return data
    return {}

# creates a dataframe for name, risk and return of user's financial assets
def get_return_risk_df(data):
    assets = data.get("financial_assets", [])
    if not assets:
        return pd.DataFrame(columns=["Name", "Return", "Risk"])
    return pd.DataFrame([{
        "Name": a["name"],
        "Return": a["expected_return"],
        "Risk": a["risk_rating"]
    } for a in assets])

#using Counter here to count frequency of each category from the categories list
def get_category_bar_data(data):
    txs = data.get("transactions", [])
    categories = [t["category"].replace('_', ' ').upper() for t in txs if "category" in t]
    return Counter(categories)

def _format_asset_type(asset_type):
    """Format asset type string to be more readable."""
    # Split by underscore and capitalize each word
    words = asset_type.split('_')
    formatted = ' '.join(word.upper() for word in words)
    return formatted

def get_asset_distribution_df(data):
    assets = data.get("financial_assets", [])
    if not assets:
        return pd.DataFrame(columns=["Type", "Count", "Avg Return", "Country"])
    
    # Group by asset type and calculate metrics
    asset_data = []
    for asset_type in set(a["type"] for a in assets):
        type_assets = [a for a in assets if a["type"] == asset_type]
        asset_data.append({
            "Type": _format_asset_type(asset_type),
            "Count": len(type_assets),
            "Avg Return": sum(a["expected_return"] for a in type_assets) / len(type_assets),
            "Country": type_assets[0].get("country", "N/A")
        })
    
    return pd.DataFrame(asset_data)

def _convert_to_native_types(obj):
    """Convert NumPy types to Python native types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: _convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_to_native_types(item) for item in obj]
    return obj

def get_ai_recommendations(data, df_assets=None, bar_data=None, recommendation_type="assets"):
    # Prepare context for the AI
    context = {}
    
    if recommendation_type == "assets":
        # For asset-based recommendations
        assets = data.get("financial_assets", [])
        if not assets:
            return ["No assets found to generate recommendations."]
            
        context = {
            "assets": assets,
            "asset_distribution": df_assets.to_dict('records') if df_assets is not None else [],
            "total_assets": len(assets),
            "asset_types": [a["type"] for a in assets],
            "risk_ratings": [a["risk_rating"] for a in assets],
            "expected_returns": [a["expected_return"] for a in assets],
            "countries": [a.get("country", "Unknown") for a in assets]
        }
        
        prompt = f"""As a financial advisor, analyze the following asset portfolio data and provide 2-3 specific, actionable recommendations.
Focus on portfolio optimization and risk management based on the user's current assets.

Portfolio Data:
{json.dumps(_convert_to_native_types(context))}

Provide recommendations that:
1. Are specific to the user's current asset mix and geographical distribution
2. Suggest concrete actions to improve portfolio balance
3. Consider the risk-return profile of existing assets
4. Are practical and implementable

Format each recommendation with an appropriate emoji and keep it under 2 sentences."""

    else:  # spending recommendations
        # For spending-based recommendations
        transactions = data.get("transactions", [])
        if not transactions:
            return ["No transaction data found to generate recommendations."]
            
        context = {
            "transactions": transactions,
            "spending_categories": dict(bar_data) if bar_data else {},
            "total_transactions": len(transactions),
            "categories": list(bar_data.keys()) if bar_data else [],
            "total_spend": sum(t.get("amount", 0) for t in transactions),
            "currencies": list(set(t.get("currency", "Unknown") for t in transactions))
        }
        
        prompt = f"""As a financial advisor, analyze the following spending data and provide 2-3 specific, actionable recommendations.
Focus on spending patterns and potential areas for optimization.

Spending Data:
{json.dumps(_convert_to_native_types(context))}

Provide recommendations that:
1. Are specific to the user's current spending patterns and categories
2. Suggest concrete actions to optimize spending
3. Consider the frequency and distribution of spending across categories
4. Take into account the currency distribution
5. Are practical and implementable

Format each recommendation with an appropriate emoji and keep it under 2 sentences."""

    # Get AI response
    messages = [
        {"role": "system", "content": "You are a professional financial advisor providing personalized recommendations based on user data."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = llm.invoke(messages)
        # Split the response into individual recommendations
        recommendations = [rec.strip() for rec in response.content.split('\n') if rec.strip()]
        return recommendations if recommendations else ["Unable to generate specific recommendations at this time."]
    except Exception as e:
        st.error(f"Error generating AI recommendations: {str(e)}")
        return ["Unable to generate AI recommendations at this time."]

def get_historical_performance_df(data, by_type=False):
    assets = data.get("financial_assets", [])
    if not assets:
        return pd.DataFrame()
    
    # Create a list to store all performance data
    performance_data = []
    
    for asset in assets:
        if "financial_details" in asset and "historical_performance" in asset["financial_details"]:
            hist_perf = asset["financial_details"]["historical_performance"]
            for year, return_str in hist_perf.items():
                # Convert percentage string to float
                return_value = float(return_str.strip('%'))
                performance_data.append({
                    "Asset": asset["name"] if not by_type else _format_asset_type(asset["type"]),
                    "Year": int(year),
                    "Return": return_value
                })
    
    df = pd.DataFrame(performance_data)
    
    if by_type:
        # Calculate average returns by type and year
        df = df.groupby(['Asset', 'Year'])['Return'].mean().reset_index()
    
    return df

def get_historical_performance_insight(data, hist_df, view_type):
    # Validate data
    if hist_df.empty:
        return "No historical performance data available to generate insights."
        
    # Prepare context for the AI
    context = {
        "view_type": view_type,
        "performance_data": hist_df.to_dict('records'),
        "assets": data.get("financial_assets", []),
        "years": sorted(hist_df["Year"].unique()),
        "assets_list": sorted(hist_df["Asset"].unique()),
        "avg_returns": hist_df.groupby("Year")["Return"].mean().to_dict()
    }
    
    # Create a prompt for the AI
    prompt = f"""As a financial advisor, analyze the following historical performance data and provide a brief, actionable insight.
Focus on identifying trends, risks, or opportunities based on the {view_type} view.

Performance Data:
{json.dumps(_convert_to_native_types(context))}

Provide a single, concise insight that:
1. Highlights the most important trend or observation from the actual data
2. Suggests a specific action or consideration based on the performance patterns
3. Is relevant to the current view (individual assets or asset types)
4. References specific numbers or trends from the data

Format the insight with an appropriate emoji and keep it under 2 sentences."""

    # Get AI response
    messages = [
        {"role": "system", "content": "You are a professional financial advisor providing personalized insights based on historical performance data."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = llm.invoke(messages)
        # Clean the response to remove any internal newlines that might break formatting
        cleaned_response = response.content.strip().replace('\n', ' ')
        return cleaned_response
    except Exception as e:
        st.error(f"Error generating AI insight: {str(e)}")
        return "Unable to generate AI insight at this time."

def get_country_distribution_df(data):
    assets = data.get("financial_assets", [])
    if not assets:
        return pd.DataFrame(columns=["Country", "Count", "Avg Return", "Total Value"])
    
    # Group by country and calculate metrics
    country_data = {}
    for asset in assets:
        country = asset.get("country", "Unknown")
        if country not in country_data:
            country_data[country] = {
                "Count": 0,
                "Total Return": 0,
                "Total Value": 0
            }
        country_data[country]["Count"] += 1
        country_data[country]["Total Return"] += asset.get("expected_return", 0)
        country_data[country]["Total Value"] += asset.get("minimum_investment_amount", 0)
    
    # Calculate averages and create DataFrame
    country_metrics = []
    for country, metrics in country_data.items():
        country_metrics.append({
            "Country": country,
            "Count": metrics["Count"],
            "Avg Return": metrics["Total Return"] / metrics["Count"],
            "Total Value": metrics["Total Value"]
        })
    
    return pd.DataFrame(country_metrics)

def get_country_insight(data, country_df):
    # Validate data
    if country_df.empty:
        return "No country distribution data available to generate insights."
        
    # Prepare context for the AI
    context = {
        "country_distribution": country_df.to_dict('records'),
        "assets": data.get("financial_assets", []),
        "total_assets": len(data.get("financial_assets", [])),
        "countries": country_df["Country"].tolist(),
        "asset_counts": country_df.set_index("Country")["Count"].to_dict(),
        "avg_returns": country_df["Avg Return"].to_dict()
    }
    
    # Create a prompt for the AI
    prompt = f"""As a financial advisor, analyze the following country-wise asset distribution by count and provide a brief, actionable insight.
Focus on identifying opportunities, risks, or diversification needs based on the geographical distribution.

Country Distribution Data:
{json.dumps(_convert_to_native_types(context))}

Provide a single, concise insight that:
1. Highlights the most important observation about the geographical distribution by asset count
2. Suggests a specific action or consideration regarding country allocation
3. References specific numbers or percentages from the data (e.g., 'X% of assets are in Country Y')
4. Considers the balance between domestic (India) and international investments

Format the insight with an appropriate emoji and keep it under 2 sentences."""

    # Get AI response
    messages = [
        {"role": "system", "content": "You are a professional financial advisor providing personalized insights based on geographical investment distribution."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = llm.invoke(messages)
        # Clean the response to remove any internal newlines that might break formatting
        cleaned_response = response.content.strip().replace('\n', ' ')
        return cleaned_response
    except Exception as e:
        st.error(f"Error generating country insight: {str(e)}")
        return "Unable to generate country insight at this time."

def display_analytics():
    st.header("📊 Investment Analytics Dashboard")
    data = load_data()

    # Define a consistent color palette with high contrast
    colors = {
        'primary': [
            '#A29BFE',  # Pastel Purple (from #6c5ce7)
            '#81ECEC',  # Pastel Teal (from #00b894)
            '#FDCB6E',  # Gold/Yellow (from website accent)
            '#74B9FF',  # Pastel Blue
            '#FD79A8',  # Pastel Pink
            '#55A3FF',  # Pastel Sky Blue
            '#00B894',  # Original Teal
            '#6C5CE7',  # Original Purple
            '#FF7675',  # Pastel Coral
            '#A8E6CF'   # Pastel Mint
        ],
        'secondary': [
            '#8B7FD8',  # Darker Pastel Purple
            '#6ED4D4',  # Darker Pastel Teal
            '#F39C12',  # Darker Gold
            '#5AA3E6',  # Darker Pastel Blue
            '#E84393',  # Darker Pastel Pink
            '#4A90E2',  # Darker Pastel Sky Blue
            '#00A085',  # Darker Teal
            '#5A4FCF',  # Darker Purple
            '#E17055',  # Darker Pastel Coral
            '#8FD3B6'   # Darker Pastel Mint
        ],
        'background': '#d761f1',  # Dark Navy background
        'text': 'black'
    }

    # ─── KPI Metrics ───
    st.subheader("📈 System Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", len(data.get("transactions", [])))
    col2.metric("Financial Assets", len(data.get("financial_assets", [])))
    
    # Calculate country distribution
    assets = data.get("financial_assets", [])
    country_distribution = {}
    for asset in assets:
        country = asset.get("country", "Unknown")
        country_distribution[country] = country_distribution.get(country, 0) + 1
    
    col3.metric("Countries", len(country_distribution))

    # ─── Country Distribution Section ───
    st.subheader("🌍 Asset Distribution by Country")
    country_df = get_country_distribution_df(data)
    if not country_df.empty:
        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Set dark background for the entire figure
        fig.patch.set_facecolor(colors['background'])
        ax1.set_facecolor(colors['background'])
        ax2.set_facecolor(colors['background'])
        
        # Asset Count by Country (Pie Chart)
        wedges, texts, autotexts = ax1.pie(
            country_df["Count"],
            labels=country_df["Country"],
            autopct='%1.1f%%',
            colors=colors['primary'][:len(country_df)],
            textprops={'color': 'black', 'weight': 'bold'}
        )
        ax1.set_title("Asset Distribution by Country", color=colors['text'], pad=20)
        
        # Average Returns by Country (Bar Chart)
        bars = ax2.bar(
            country_df["Country"], 
            country_df["Avg Return"], 
            color=[colors['primary'][i % len(colors['primary'])] for i in range(len(country_df))]
        )
        ax2.set_title("Average Returns by Country", color=colors['text'], pad=20)
        ax2.set_ylabel("Return (%)", color=colors['text'])
        ax2.tick_params(colors=colors['text'])
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', color=colors['text'], weight='bold')
        
        # Update legend text color to white
        for ax in [ax1, ax2]:
            if ax.get_legend():
                legend = ax.get_legend()
                for text in legend.get_texts():
                    text.set_color('white')
        
        st.pyplot(fig)
        
        # Show AI-generated country insight
        st.subheader("💡 AI Country Distribution Insight")
        with st.spinner("Analyzing geographical distribution..."):
            insight = get_country_insight(data, country_df)
            st.write(insight)
    else:
        st.info("No country distribution data available.")

    # ─── Historical Performance Chart ───
    st.subheader("📈 Historical Performance (5-Year Returns)")
    
    # Add toggle for view type
    view_type = st.radio(
        "Select View:",
        ["Individual Assets", "Average by Asset Type", "By Country"],
        horizontal=True,
        key="historical_view"
    )
    
    hist_df = get_historical_performance_df(data, by_type=(view_type == "Average by Asset Type"))
    if not hist_df.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # Set dark background
        fig.patch.set_facecolor(colors['background'])
        ax.set_facecolor(colors['background'])
        
        if view_type == "By Country":
            # Group by country and calculate average returns
            country_data = {}
            for asset in assets:
                country = asset.get("country", "Unknown")
                if "financial_details" in asset and "historical_performance" in asset["financial_details"]:
                    for year, return_str in asset["financial_details"]["historical_performance"].items():
                        if country not in country_data:
                            country_data[country] = {}
                        if year not in country_data[country]:
                            country_data[country][year] = []
                        country_data[country][year].append(float(return_str.strip('%')))
            
            # Calculate averages and plot
            for i, (country, year_data) in enumerate(country_data.items()):
                years = sorted(year_data.keys())
                avg_returns = [sum(year_data[year]) / len(year_data[year]) for year in years]
                ax.plot(years, avg_returns, marker='o', label=country, 
                       color=colors['primary'][i % len(colors['primary'])],
                       linewidth=2,
                       markersize=8)
        else:
            # Get unique assets for checkbox selection
            unique_assets = sorted(hist_df["Asset"].unique())
            
            # Add checkboxes for asset selection if in Individual Assets view
            if view_type == "Individual Assets":
                selected_assets = st.multiselect(
                    "Select assets to display:",
                    options=unique_assets,
                    default=unique_assets[:3]  # Default to first 3 assets
                )
            else:
                selected_assets = unique_assets
            
            # Plot each selected asset's performance
            for i, asset in enumerate(selected_assets):
                asset_data = hist_df[hist_df["Asset"] == asset]
                ax.plot(asset_data["Year"], asset_data["Return"], marker='o', label=asset, 
                       color=colors['primary'][i % len(colors['primary'])],
                       linewidth=2,
                       markersize=8)
        
        title = "5-Year Historical Returns by Country" if view_type == "By Country" else \
               "5-Year Historical Returns by Asset Type" if view_type == "Average by Asset Type" else \
               "5-Year Historical Returns by Asset"
        ax.set_title(title, color=colors['text'], pad=20)
        ax.set_xlabel("Year", color=colors['text'])
        ax.set_ylabel("Return (%)", color=colors['text'])
        ax.grid(True, linestyle='--', alpha=0.3, color='white')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', labelcolor='black')
        ax.tick_params(colors=colors['text'])
        
        # Set x-axis to show only whole number years
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        st.pyplot(fig)
        
        # Filter data for insights based on selected assets
        if view_type == "Individual Assets":
            filtered_data = {
                "financial_assets": [asset for asset in data.get("financial_assets", []) 
                                   if asset["name"] in selected_assets]
            }
            filtered_hist_df = hist_df[hist_df["Asset"].isin(selected_assets)]
        else:
            filtered_data = data
            filtered_hist_df = hist_df
        
        # Show AI-generated insight
        st.subheader("💡 AI Performance Insight")
        with st.spinner("Analyzing performance trends..."):
            insight = get_historical_performance_insight(filtered_data, filtered_hist_df, view_type)
            st.write(insight)
    else:
        st.info("No historical performance data available.")

    # ─── Asset Distribution Chart ───
    st.subheader("📊 Asset Distribution & Returns")
    df_assets = get_asset_distribution_df(data)
    if not df_assets.empty:
        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3))
        
        # Set dark background for the entire figure
        fig.patch.set_facecolor(colors['background'])
        ax1.set_facecolor(colors['background'])
        ax2.set_facecolor(colors['background'])
        
        # Asset Count by Type (Pie Chart)
        wedges, texts, autotexts = ax1.pie(
            df_assets["Count"], 
            labels=df_assets["Type"], 
            autopct='%1.1f%%',
            colors=colors['primary'][:len(df_assets)],
            textprops={'color': colors['text'], 'weight': 'bold', 'fontsize': 6}
        )
        ax1.set_title("Asset Distribution by Type", color=colors['text'], pad=10, fontsize=10)
        
        # Average Returns by Type (Bar Chart)
        bars = ax2.bar(
            df_assets["Type"], 
            df_assets["Avg Return"], 
            color=[colors['primary'][i % len(colors['primary'])] for i in range(len(df_assets))]
        )
        ax2.set_title("Average Returns by Asset Type", color=colors['text'], pad=10, fontsize=10)
        ax2.set_ylabel("Return (%)", color=colors['text'], fontsize=8)
        ax2.tick_params(colors=colors['text'], labelrotation=45, labelsize=8)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', color=colors['text'], weight='bold', fontsize=8)
        
        # Update legend text color to white
        for ax in [ax1, ax2]:
            if ax.get_legend():
                legend = ax.get_legend()
                for text in legend.get_texts():
                    text.set_color('white')
        
        # plt.tight_layout()
        st.pyplot(fig)
        
        # Filter data for recommendations based on selected assets
        if view_type == "Individual Assets":
            filtered_data = {
                "financial_assets": [asset for asset in data.get("financial_assets", []) 
                                   if asset["name"] in selected_assets]
            }
            filtered_df_assets = df_assets[df_assets["Type"].isin([asset["type"] for asset in filtered_data["financial_assets"]])]
        else:
            filtered_data = data
            filtered_df_assets = df_assets
        
        # Show AI-generated recommendations
        st.subheader("🤖 AI-Powered Portfolio Recommendations")
        with st.spinner("Generating personalized portfolio recommendations..."):
            recommendations = get_ai_recommendations(filtered_data, df_assets=filtered_df_assets, recommendation_type="assets")
            for rec in recommendations:
                st.write(rec)
    else:
        st.info("No asset data available.")

    # ─── Candlestick-style Bar Chart: Spending by Category ───
    st.subheader("📊 Spending by Category")
    bar_data = get_category_bar_data(data)
    if bar_data:
        df_bar = pd.DataFrame(bar_data.items(), columns=["Category", "Count"]).sort_values(by="Count", ascending=False)
        fig, ax = plt.subplots(figsize=(6, 2))
        
        # Set dark background
        fig.patch.set_facecolor(colors['background'])
        ax.set_facecolor(colors['background'])
        
        ax.bar(df_bar["Category"], df_bar["Count"], color="#6c5ce7", edgecolor="white")
        # ax.set_title("Spending by Category", color=colors['text'], fontsize=7)
        ax.set_ylabel("Frequency", color=colors['text'], fontsize=7)
        ax.set_xlabel("Category", color=colors['text'], fontsize=7)
        ax.tick_params(colors=colors['text'], labelrotation=45, labelsize=6)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        
        st.pyplot(fig)
        
        # Show AI-generated spending recommendations
        st.subheader("🤖 AI-Powered Spending Insights")
        with st.spinner("Analyzing spending patterns..."):
            spending_recommendations = get_ai_recommendations(data, bar_data=bar_data, recommendation_type="spending")
            for rec in spending_recommendations:
                st.write(rec)
    else:
        st.info("No transaction category data found.")