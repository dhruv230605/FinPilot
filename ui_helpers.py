import streamlit as st

def inject_fintech_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif !important;
        background: #130f40;
        color: #f5f6fa;
    }

    .bg-wave {
        position: fixed;
        top: 0;
        left: 0;
        z-index: -1;
        width: 100vw;
        height: 100vh;
        background: url("https://www.svgbackgrounds.com/wp-content/uploads/2021/01/wave-haikei.svg") no-repeat center center fixed;
        background-size: cover;
        opacity: 0.12;
        animation: floatwave 8s ease-in-out infinite;
    }

    @keyframes floatwave {
        0%, 100% { transform: translateY(0px);}
        50% { transform: translateY(-20px);}
    }

    .header-banner {
        background: linear-gradient(90deg, #6c5ce7 0%, #00b894 100%);
        border-radius: 22px;
        padding: 2.2rem 2rem 2rem 2rem;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        box-shadow: 0 8px 32px rgba(44, 62, 80, 0.25);
        gap: 24px;
    }

    .header-banner img {
        border-radius: 50%;
        border: 3px solid #fff;
        background: #fff;
        box-shadow: 0 2px 12px rgba(44, 62, 80, 0.22);
    }

    .tab-buttons {
        display: flex;
        justify-content: center;
        gap: 1.3rem;
        margin-bottom: 2.2rem;
    }

    .tab-buttons button {
        background: linear-gradient(90deg, #341f97 0%, #00b894 100%);
        border: none;
        padding: 0.7rem 1.5rem;
        color: white;
        border-radius: 12px;
        font-weight: bold;
        font-size: 1rem;
        cursor: pointer;
        transition: box-shadow 0.2s, transform 0.2s;
        box-shadow: 0 2px 8px rgba(44, 62, 80, 0.10);
    }

    .tab-buttons button:hover {
        background: linear-gradient(90deg, #6c5ce7 0%, #00b894 100%);
        transform: translateY(-3px) scale(1.04);
        box-shadow: 0 4px 16px rgba(44, 62, 80, 0.16);
    }

    .rec-card {
        background: linear-gradient(120deg, #e0eafc 60%, #cfdef3 100%);
        padding: 1.2rem 1rem;
        border-radius: 16px;
        color: black;
        box-shadow: 0 4px 18px rgba(44, 62, 80, 0.18);
        margin-bottom: 1.2rem;
        transition: transform 0.15s, box-shadow 0.15s;
        border: 2px solid #6c5ce7;
        position: relative;
    }

    .rec-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 8px 28px rgba(44, 62, 80, 0.22);
        border-color: #00b894;
    }

    .rec-card .priority {
        background: #00b894;
        color: #fff;
        padding: 0.2rem 0.7rem;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .rec-card .match {
        background: #6c5ce7;
        color: #fff;
        padding: 0.2rem 0.7rem;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .rec-card h4 {
        margin-top: 0.7rem;
        margin-bottom: 0.5rem;
        font-size: 1.25rem;
    }

    .rec-card .desc {
        font-size: 1.05rem;
        margin-bottom: 0.6rem;
    }

    .rec-card .allocation {
        font-size: 0.97rem;
        margin-bottom: 0.6rem;
        color: #dff9fb;
    }

    .rec-card .tag {
        background: #fdcb6e;
        color: #2d3436;
        padding: 0.18rem 0.8rem;
        border-radius: 7px;
        font-size: 0.92rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }

    .rec-card .btn {
        display: inline-block;
        margin-top: 0.7rem;
        background: linear-gradient(90deg, #00b894 0%, #6c5ce7 100%);
        color: #fff;
        padding: 0.45rem 1.2rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        transition: background 0.2s, color 0.2s;
    }

    .rec-card .btn:hover {
        background: linear-gradient(90deg, #6c5ce7 0%, #00b894 100%);
        color: #fff;
    }

    .login-box {
        margin-top: 10vh;
        max-width: 420px;
        margin-left: auto;
        margin-right: auto;
        background: #fff;
        padding: 2.2rem 2rem;
        border-radius: 18px;
        box-shadow: 0 10px 32px rgba(44, 62, 80, 0.09);
        text-align: center;
        border: 1px solid #6c5ce7;
    }

    .login-box h2 {
        color: #5f27cd;
        margin-bottom: 1.2rem;
    }

    .footer {
        margin-top: 2.5rem;
        text-align: center;
        color: #8e9bae;
        font-size: 0.98rem;
        padding-bottom: 1.2rem;
        opacity: 0.8;
    }
    </style>
    <div class="bg-wave"></div>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown(
        f"""
        <style>
            @keyframes fadeInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            @keyframes gradientFlow {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            @keyframes pulseGlow {{
                0% {{ box-shadow: 0 0 5px rgba(78, 205, 196, 0.5); }}
                50% {{ box-shadow: 0 0 20px rgba(78, 205, 196, 0.8); }}
                100% {{ box-shadow: 0 0 5px rgba(78, 205, 196, 0.5); }}
            }}
            .animated-header {{
                text-align: center;
                padding: 1.5rem;
                background: linear-gradient(45deg, #1A1A2E, #2A2A4A);
                background-size: 200% 200%;
                border-radius: 15px;
                margin-bottom: 2rem;
                animation: gradientFlow 15s ease infinite, pulseGlow 3s ease-in-out infinite;
            }}
            .animated-title {{
                color: #4ECDC4;
                margin-bottom: 0.5rem;
                font-size: 2.5rem;
                font-weight: 700;
                animation: fadeInUp 1s ease-out;
            }}
            .animated-tagline {{
                color: #FFFFFF;
                font-size: 1.2rem;
                margin: 0;
                font-weight: 300;
                animation: fadeInUp 1s ease-out 0.3s backwards;
            }}
            .animated-subtagline {{
                color: #FFFFFF;
                font-size: 1rem;
                margin-top: 0.5rem;
                font-style: italic;
                animation: fadeInUp 1s ease-out 0.6s backwards;
            }}
        </style>
        <div class="animated-header">
            <h1 class="animated-title">FinPilot</h1>
            <p class="animated-tagline">Navigate Your Financial Future with AI-Powered Precision</p>
            <p class="animated-subtagline">Smart Investments, Smarter You</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_footer():
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background-color: #1A1A2E; border-radius: 10px; margin-top: 2rem;'>
        <p style='color: #FFFFFF; margin: 0;'>© 2024 FinPilot. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)