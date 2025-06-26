import streamlit as st
from ui_helpers import inject_fintech_styles, render_header, render_footer
from backend.auth import register_user, login_user
from backend.chatbot import generate_chat_response, search_all_categories, llm
from backend.analytics import display_analytics, _format_asset_type
from backend.data_manager import show_data_dashboard
from dotenv import load_dotenv
from streamlit_sortables import sort_items
import os
import json

load_dotenv()
st.set_page_config(page_title="FinPilot", page_icon="📊", layout="wide")

# ───── Session ─────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "Recommendations"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_user_email" not in st.session_state:
    st.session_state.current_user_email = None
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False

# ───── Login Page ─────
def login_ui():
    inject_fintech_styles()
    st.markdown("<div class='bg-wave'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; padding: 2rem; background-color: #1A1A2E; border-radius: 10px; margin: 2rem 0;'>
            <h2>FinPilot Login</h2>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(email, password):
                st.session_state.authenticated = True
                st.session_state.current_user_email = email
                st.success("✅ Logged in successfully!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
    with tab2:
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            register_user(new_email, new_password)

# ───── Dashboard Tabs ─────
def render_navigation():
    render_header()
    st.markdown("<div class='bg-wave'></div>", unsafe_allow_html=True)
    st.markdown("""
        <style>
        .nav-container {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin: 1rem 0;
        }
        .nav-button {
            flex: 0 1 200px;
            text-align: center;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            background: linear-gradient(45deg, #1A1A2E, #2A2A4A);
            border: 1px solid #4ECDC4;
            color: white;
            transition: all 0.3s ease;
        }
        .nav-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(78, 205, 196, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    cols = st.columns([1, 1, 1])
    tab_icons = ["💡", "📈", "📊"]
    tab_names = ["Recommendations", "Analytics", "Data"]
    for i, (icon, name) in enumerate(zip(tab_icons, tab_names)):
        with cols[i]:
            if st.button(f"{icon} {name}", use_container_width=True):
                st.session_state.page = name
    st.markdown('</div>', unsafe_allow_html=True)

# ───── Recommendations ─────
def recommendation_ui():
    st.subheader("💡 AI-Powered Investment Strategies")
    col1, col2 = st.columns(2)
    with col1:
        risk_profile = st.selectbox(
            "Risk Profile",
            ["Conservative", "Moderate", "Aggressive"],
            help="Select your preferred risk level"
        )
    with col2:
        time_horizon = st.selectbox(
            "Investment Time Horizon",
            ["Short-term (< 1 year)", "Medium-term (1-5 years)", "Long-term (> 5 years)"],
            help="Select your investment time frame"
        )
    st.markdown("### 🎯 Investment Preferences")
    col1, col2 = st.columns([0.4, 0.6])
    with col1:
        if 'asset_order' not in st.session_state:
            st.session_state.asset_order = [
                "FD", "mutual_funds", "bonds", "equity", "gold",
                "NPS", "PPF", "ELSS", "SIP"
            ]
        with st.container():
            st.markdown("""
            <style>
            .stSortable {
                max-width: 300px;
                margin: 0 auto;
            }
            .sortable-title {
                font-size: 0.9em;
                color: #666;
                margin-bottom: 8px;
            }
            </style>
            """, unsafe_allow_html=True)
            st.markdown('<div class="sortable-title">Drag to arrange by priority (top = highest)</div>', unsafe_allow_html=True)
            display_names = {asset: _format_asset_type(asset) if '_' in asset else asset.upper()
                             for asset in st.session_state.asset_order}
            sorted_items = sort_items(
                [display_names[asset] for asset in st.session_state.asset_order],
                direction="vertical",
                key="asset_priority"
            )
            reverse_display = {v: k for k, v in display_names.items()}
            st.session_state.asset_order = [reverse_display[item] for item in sorted_items]
    with col2:
        query = st.text_input(
            "What kind of investment strategy are you looking for?",
            "e.g. low-risk investment",
            help="Describe your investment goals or preferences"
        )
    allocation_priorities = {
        asset: i+1 for i, asset in enumerate(st.session_state.asset_order)
    }
    if st.button("🔍 Get Recommendations"):
        with st.spinner("Analyzing market conditions and generating personalized recommendations..."):
            results = search_all_categories(query)
            if not results or not results.get("investment_strategies"):
                st.warning("No investment strategies found. Try a different search term.")
                return
            items = results["investment_strategies"]
            if items:
                st.markdown("### 📊 Personalized Investment Strategies")
                scored_items = []
                for item, score in items:
                    allocation = item.get("allocation_blueprint", {})
                    priority_score = 0
                    for asset, percentage in allocation.items():
                        if asset in allocation_priorities:
                            priority = allocation_priorities[asset]
                            priority_score += (percentage / 100) * (len(allocation_priorities) - priority + 1)
                    risk_match = 1 if risk_profile.lower() in item.get("risk_profile", "").lower() else 0.5
                    horizon_match = 1 if time_horizon.split()[0].lower() in item.get("time_horizon", "").lower() else 0.5
                    profile_match = (risk_match + horizon_match) / 2
                    total_score = (priority_score * 0.7) + (profile_match * 0.3)
                    scored_items.append((item, total_score))
                scored_items.sort(key=lambda x: x[1], reverse=True)
                for item, score in scored_items:
                    name = item.get("name", "Unnamed Strategy")
                    strategy_risk = item.get("risk_profile", "Not specified")
                    strategy_horizon = item.get("time_horizon", "Not specified")
                    target_return = item.get("target_annual_return", 0)
                    strategy_prompt = f"""Analyze this investment strategy for a user with the following preferences:
                    User Risk Profile: {risk_profile}
                    User Time Horizon: {time_horizon}
                    User Goals: {query}
                    Strategy Details:
                    {json.dumps(item, indent=2)}
                    Provide a brief analysis focusing on:
                    1. How well this strategy matches the user's profile
                    2. Key benefits and potential risks
                    3. Specific considerations for this user
                    Keep the response concise and actionable."""
                    try:
                        strategy_analysis = llm.invoke([{"role": "user", "content": strategy_prompt}]).content
                    except Exception as e:
                        strategy_analysis = f"""
                        This strategy appears suitable for {risk_profile.lower()} risk investors with a {time_horizon.lower()} time horizon.
                        Key benefits include potential returns of {target_return}% and a diversified allocation across multiple asset classes.
                        Consider your specific financial goals and risk tolerance when evaluating this strategy.
                        """
                    risk_match = 1 if risk_profile.lower() in strategy_risk.lower() else 0.5
                    horizon_match = 1 if time_horizon.split()[0].lower() in strategy_horizon.lower() else 0.5
                    match_pct = int(((risk_match + horizon_match) / 2) * 100)
                    priority = "high" if match_pct > 80 else "medium" if match_pct > 50 else "low"
                    allocation = item.get("allocation_blueprint", {})
                    allocation_desc = ", ".join([f"{k}: {v}%" for k, v in allocation.items()])
                    st.markdown(f"""
                    <div class='rec-card' style='width: 100%; margin-bottom: 15px; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>
                            <h3 style='margin: 0; font-size: 1.3em; color: black;'>{name}</h3>
                            <div style='display:flex;gap:10px;align-items:center;'>
                                <span class='priority' style='background: {"#4CAF50" if priority == "high" else "#FFC107" if priority == "medium" else "#F44336"}; padding: 4px 8px; border-radius: 4px; color: black; font-size: 0.8em;'>{priority.capitalize()} Priority</span>
                                <span class='match' style='background: #2196F3; padding: 4px 8px; border-radius: 4px; color: black; font-size: 0.8em;'>{match_pct}% match</span>
                            </div>
                        </div>
                        <div style='display:flex;gap:15px;margin-bottom:10px;font-size:0.9em;color:black;font-weight:500;'>
                            <span>Risk: {strategy_risk}</span>
                            <span>Horizon: {strategy_horizon}</span>
                            <span>Target Return: {target_return}%</span>
                        </div>
                        <p class='desc' style='font-size: 0.9em; margin: 8px 0; color: black;'>{strategy_analysis}</p>
                        <div style='font-size: 0.9em; color: ;'><strong>Allocation:</strong> {allocation_desc}</div>
                    </div>
                    """, unsafe_allow_html=True)

# ───── Main UI ─────
def main_ui():
    inject_fintech_styles()
    st.markdown("<div class='bg-wave'></div>", unsafe_allow_html=True)
    # --- Logout button at the very top ---
    logout_cols = st.columns([10, 1])
    with logout_cols[1]:
        logout = st.button("🚪 Logout", key="logout_top", use_container_width=True)
    if logout:
        st.session_state.authenticated = False
        st.session_state.current_user_email = None
        st.session_state.chat_history = []
        st.rerun()
    # --- Rest of UI ---
    render_navigation()
    if st.session_state.page == "Recommendations":
        recommendation_ui()
    elif st.session_state.page == "Analytics":
        display_analytics()
    elif st.session_state.page == "Data":
        show_data_dashboard()

# ───── Chat Handler ─────
def send_message(msg: str):
    st.session_state.chat_history.append(("user", msg))
    with st.spinner("FinPilot is thinking..."):
        try:
            reply = generate_chat_response(msg)
        except Exception as e:
            reply = f"⚠️ Error: {e}"
    st.session_state.chat_history.append(("bot", reply))

# ───── Run ─────
if not st.session_state.authenticated:
    login_ui()
else:
    main_ui()
    # Toggle chat panel
    if not st.session_state.chat_open and st.button("💬 Chat with me"):
        st.session_state.chat_open = True
        st.rerun()
    # Sidebar chat panel
    if st.session_state.chat_open:
        with st.sidebar:
            st.subheader("🤖 FinPilot Chat")
            for who, msg in st.session_state.chat_history:
                tag = "🧑 You:" if who == "user" else "🤖 FinPilot:"
                st.markdown(f"**{tag}** {msg}")
            st.markdown("---")
            if st.button("🗑️ Clear"):
                st.session_state.chat_history = []
                st.rerun()
            with st.form("chat_form"):
                user_input = st.text_input(
                    "Type your message…",
                    key="chat_input",
                    label_visibility="collapsed"
                )
                submit = st.form_submit_button("Send")
                if submit and user_input:
                    send_message(user_input)
                    st.rerun()
            if st.button("Close Chat"):
                st.session_state.chat_open = False
                st.session_state.chat_history = []
                st.rerun()
