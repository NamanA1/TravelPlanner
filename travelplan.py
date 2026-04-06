import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import os
import re
from html import escape
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wandr · Travel Planner",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Global CSS (for the Streamlit page itself) ─────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Raleway:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Raleway', sans-serif; }
.stApp { background: #fdf8f3; color: #2c2416; }

.hero {
    background: linear-gradient(160deg, #1a3a2a 0%, #2d5a3d 50%, #1a3a2a 100%);
    border-radius: 20px;
    padding: 3rem 2.5rem 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse at 20% 50%, rgba(212,175,80,0.15) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(255,255,255,0.05) 0%, transparent 50%);
    pointer-events: none;
}
.hero-tag {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 4px;
    text-transform: uppercase; color: #d4af50; margin-bottom: 0.8rem;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem; font-weight: 700;
    color: #f5f0e8; margin: 0 0 0.6rem; line-height: 1.1;
}
.hero h1 em { font-style: italic; color: #d4af50; }
.hero-sub { color: rgba(245,240,232,0.6); font-size: 0.95rem; font-weight: 300; }

.form-card {
    background: #ffffff; border: 1px solid #e8e0d4;
    border-radius: 16px; padding: 2rem 2.2rem;
    box-shadow: 0 4px 24px rgba(44,36,22,0.06); margin-bottom: 1.5rem;
}
.section-label {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 3px;
    text-transform: uppercase; color: #8a7560; margin-bottom: 1.2rem;
}
.stTextInput input, .stSelectbox > div > div, .stNumberInput input {
    background: #fdf8f3 !important; border: 1.5px solid #e0d6c8 !important;
    border-radius: 10px !important; color: #2c2416 !important;
    font-family: 'Raleway', sans-serif !important; font-size: 0.95rem !important;
}
label { color: #5a4a38 !important; font-size: 0.85rem !important; font-weight: 500 !important; }
.stButton > button {
    background: linear-gradient(135deg, #1a3a2a, #2d5a3d) !important;
    color: #f5f0e8 !important; border: none !important;
    border-radius: 12px !important; font-family: 'Raleway', sans-serif !important;
    font-weight: 600 !important; font-size: 1rem !important;
    padding: 0.75rem 2rem !important; letter-spacing: 1px !important; width: 100% !important;
}
.stButton > button:hover { opacity: 0.9 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 760px !important; }
</style>
""", unsafe_allow_html=True)

# ── API setup ──────────────────────────────────────────────────────
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# ── Hero ───────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-tag">✦ AI Travel Planner</div>
  <h1>Plan your perfect<br><em>journey</em></h1>
  <p class="hero-sub">Tell us where, how long, and how you like to travel — we'll do the rest.</p>
</div>
""", unsafe_allow_html=True)

# ── Form ───────────────────────────────────────────────────────────
st.markdown('<div class="form-card"><div class="section-label">Your Trip Details</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])
with col1:
    city = st.text_input("🌆 Destination City", placeholder="e.g. Tokyo, Paris, Bali…")
with col2:
    days = st.number_input("📅 Number of Days", min_value=1, max_value=30, value=5, step=1)

col3, col4 = st.columns(2)
with col3:
    language = st.selectbox("🌐 Output Language", [
        "English", "Hindi", "French", "Spanish", "German",
        "Japanese", "Arabic", "Portuguese", "Italian", "Korean"
    ])
with col4:
    budget = st.selectbox("💰 Budget Level", ["Low 🟢", "Medium 🟡", "High 🔴"])

st.markdown("</div>", unsafe_allow_html=True)

budget_clean = budget.split(" ")[0]

budget_colors = {
    "Low":    {"bg": "#eef7f0", "color": "#2d6a4f", "border": "#b7dfc7"},
    "Medium": {"bg": "#fef9ec", "color": "#92660a", "border": "#f5d87c"},
    "High":   {"bg": "#fdf0e8", "color": "#7a3a1a", "border": "#f0b88a"},
}
bc = budget_colors.get(budget_clean, budget_colors["Medium"])

# ── Generate ───────────────────────────────────────────────────────
generate = st.button("✦ Generate My Itinerary")

if generate:
    if not api_key:
        st.error("⚠ GOOGLE_API_KEY not found in your .env file.")
    elif not city.strip():
        st.warning("Please enter a destination city.")
    else:
        prompt = f"""
You are a knowledgeable travel guide. Create a detailed day-by-day travel itinerary.

Destination: {city}
Duration: {days} day(s)
Budget: {budget_clean} (Low = hostels & street food, Medium = mid-range, High = luxury)
Language: Respond entirely in {language}

Rules:
- Write exactly {days} day sections.
- Start each section with exactly "Day 1", "Day 2", etc. on its own line (even if responding in another language, keep the day label in English).
- Each day: 4-5 sentences covering morning, landmark, food, afternoon activity, evening.
- Match recommendations to the budget level.
- Mention real, famous places in {city}.
- Plain text only. No *, **, #, or any markdown. No bullet points.
- Separate each day with a blank line.
"""
        with st.spinner("Crafting your itinerary…"):
            try:
                model = genai.GenerativeModel(
                    "gemini-2.5-flash",
                    system_instruction="You are a warm, expert travel guide who writes beautiful, practical travel itineraries in plain text."
                )
                cfg = genai.GenerationConfig(temperature=1.0, max_output_tokens=2048)
                response = model.generate_content(prompt, generation_config=cfg)
                raw = response.text.strip()

                # ── Parse into day blocks ─────────────────────────────
                blocks = re.split(r'\n(?=Day \d+)', raw, flags=re.IGNORECASE)
                if len(blocks) < 2:
                    blocks = [b for b in raw.split("\n\n") if b.strip()]

                days_html = ""
                for block in blocks:
                    block = block.strip()
                    if not block:
                        continue
                    lines = block.split("\n", 1)
                    label   = escape(lines[0].strip())
                    content = escape(lines[1].strip() if len(lines) > 1 else block)
                    content = content.replace("\n", "<br>")
                    days_html += f"""
                        <div style="margin-bottom:1.6rem;">
                            <div style="font-size:0.68rem;font-weight:700;letter-spacing:3px;
                                        text-transform:uppercase;color:#d4af50;margin-bottom:0.4rem;">
                                {label}
                            </div>
                            <div style="color:#3a2e20;font-size:0.96rem;line-height:1.8;font-weight:400;">
                                {content}
                            </div>
                        </div>
                    """

                # ── Full self-contained HTML card ─────────────────────
                card_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Raleway:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; font-family: 'Raleway', sans-serif; padding: 8px 4px 16px; }}
  .wrap {{
      background: linear-gradient(160deg, #1a3a2a, #2d5a3d);
      border-radius: 20px;
      padding: 3px;
      box-shadow: 0 8px 40px rgba(26,58,42,0.2);
  }}
  .inner {{
      background: #fdf8f3;
      border-radius: 18px;
      padding: 2rem 2.2rem;
  }}
  .header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      margin-bottom: 1.2rem;
      gap: 1rem;
  }}
  .title {{
      font-family: 'Playfair Display', serif;
      font-size: 1.75rem;
      font-weight: 700;
      color: #1a3a2a;
      line-height: 1.2;
  }}
  .title span {{ color: #d4af50; font-style: italic; }}
  .badges {{ display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; }}
  .badge {{
      padding: 3px 12px; border-radius: 20px;
      font-size: 0.7rem; font-weight: 600; letter-spacing: 1px;
      text-transform: uppercase; white-space: nowrap; border: 1px solid;
  }}
  .divider {{
      height: 1px;
      background: linear-gradient(to right, #d4af50, transparent);
      margin: 1.2rem 0 1.6rem;
  }}
  .footer {{
      margin-top: 1.2rem;
      font-size: 0.72rem;
      color: #b0a08a;
      text-align: right;
      font-style: italic;
  }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="inner">
      <div class="header">
        <div class="title">Your <span>{escape(city)}</span><br>Itinerary</div>
        <div class="badges">
          <span class="badge" style="background:#eef7f0;color:#2d6a4f;border-color:#b7dfc7;">
            📅 {days} Day{'s' if days > 1 else ''}
          </span>
          <span class="badge" style="background:{bc['bg']};color:{bc['color']};border-color:{bc['border']};">
            💰 {budget_clean} Budget
          </span>
          <span class="badge" style="background:#f0eefa;color:#5b3fa6;border-color:#c4b5fd;">
            🌐 {escape(language)}
          </span>
        </div>
      </div>
      <div class="divider"></div>
      {days_html}
      <div class="footer">Generated with Gemini 2.5 Flash · Wandr AI Travel Planner</div>
    </div>
  </div>
</body>
</html>
"""
                # Estimate height: ~120px per day + fixed header
                estimated_height = 300 + (days * 180)
                components.html(card_html, height=estimated_height, scrolling=True)

            except Exception as e:
                st.error(f"Something went wrong: {e}")