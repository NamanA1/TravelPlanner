import streamlit as st
import streamlit.components.v1 as components
import os
import re
from html import escape
from dotenv import load_dotenv

# ── LangChain imports (modern LCEL syntax) ─────────────────────────
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wandr · Travel Planner",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Raleway:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Raleway', sans-serif; }
.stApp { background: #fdf8f3; color: #2c2416; }

.hero {
    background: linear-gradient(160deg, #1a3a2a 0%, #2d5a3d 50%, #1a3a2a 100%);
    border-radius: 20px; padding: 3rem 2.5rem 2.5rem;
    margin-bottom: 2rem; text-align: center; position: relative; overflow: hidden;
}
.hero-tag { font-size:0.72rem;font-weight:600;letter-spacing:4px;text-transform:uppercase;color:#d4af50;margin-bottom:0.8rem; }
.hero h1 { font-family:'Playfair Display',serif;font-size:3.2rem;font-weight:700;color:#f5f0e8;margin:0 0 0.6rem;line-height:1.1; }
.hero h1 em { font-style:italic;color:#d4af50; }
.hero-sub { color:rgba(245,240,232,0.6);font-size:0.95rem;font-weight:300; }

.form-card { background:#fff;border:1px solid #e8e0d4;border-radius:16px;padding:2rem 2.2rem;box-shadow:0 4px 24px rgba(44,36,22,0.06);margin-bottom:1.5rem; }
.section-label { font-size:0.7rem;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:#8a7560;margin-bottom:1.2rem; }

.stTextInput input, .stSelectbox>div>div, .stNumberInput input {
    background:#fdf8f3!important; border:1.5px solid #e0d6c8!important;
    border-radius:10px!important; color:#2c2416!important; font-family:'Raleway',sans-serif!important;
}
label { color:#5a4a38!important; font-size:0.85rem!important; font-weight:500!important; }

.stButton>button {
    background:linear-gradient(135deg,#1a3a2a,#2d5a3d)!important; color:#f5f0e8!important;
    border:none!important; border-radius:12px!important; font-family:'Raleway',sans-serif!important;
    font-weight:600!important; font-size:1rem!important; padding:0.75rem 2rem!important;
    letter-spacing:1px!important; width:100%!important;
}
.stButton>button:hover { opacity:0.9!important; }

.chain-step {
    display:flex; align-items:center; gap:10px;
    background:#f5f0e8; border:1px solid #e0d6c8; border-radius:10px;
    padding:0.7rem 1.1rem; margin-bottom:0.5rem; font-size:0.85rem; color:#3a2e20;
}
.chain-num {
    background:#1a3a2a; color:#d4af50; border-radius:50%;
    width:24px; height:24px; display:flex; align-items:center; justify-content:center;
    font-size:0.75rem; font-weight:700; flex-shrink:0;
}
.chain-arrow { text-align:center; color:#d4af50; font-size:1.2rem; margin: 2px 0 2px 11px; }

.chat-wrap { background:#fff;border:1px solid #e0d6c8;border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.6rem; }
.chat-label { font-size:0.65rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px; }
.chat-msg { font-size:0.9rem; line-height:1.6; }

#MainMenu, footer, header { visibility:hidden; }
.block-container { padding-top:1.5rem!important; max-width:780px!important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────
for key in ["itinerary", "costs", "hotels", "chat_history", "last_context"]:
    if key not in st.session_state:
        st.session_state[key] = None
if st.session_state.chat_history is None:
    st.session_state.chat_history = []

# ── API key ────────────────────────────────────────────────────────
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

def make_llm(temp=0.9):
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=temp,
        max_output_tokens=2048,
    )

# ── Helper: run a prompt template as LCEL chain ────────────────────
def run_chain(template: str, variables: dict, temp=0.9) -> str:
    prompt = PromptTemplate.from_template(template)
    chain = prompt | make_llm(temp) | StrOutputParser()
    return chain.invoke(variables).strip()

# ── Hero ───────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-tag">✦ AI Travel Planner · Powered by LangChain</div>
  <h1>Plan your perfect<br><em>journey</em></h1>
  <p class="hero-sub">3 chained AI calls · Itinerary → Cost Estimate → Hotel Picks → Follow-up Chat</p>
</div>
""", unsafe_allow_html=True)

# ── Chain flow diagram ─────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.5rem;">
  <div class="chain-step"><div class="chain-num">1</div> <b>Itinerary Chain</b> — Generates your day-by-day travel plan</div>
  <div class="chain-arrow">↓</div>
  <div class="chain-step"><div class="chain-num">2</div> <b>Cost Chain</b> — Reads the itinerary and estimates daily + total costs</div>
  <div class="chain-arrow">↓</div>
  <div class="chain-step"><div class="chain-num">3</div> <b>Hotel Chain</b> — Uses itinerary locations to suggest matching hotels</div>
  <div class="chain-arrow">↓</div>
  <div class="chain-step"><div class="chain-num">4</div> <b>Memory Chat</b> — Remembers everything above for follow-up questions</div>
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

generate = st.button("✦ Generate Full Travel Plan")

# ── HTML card renderer ─────────────────────────────────────────────
def render_card(title1, title2, body_html, badges_html="", footer="", height=400):
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Raleway:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:transparent; font-family:'Raleway',sans-serif; padding:6px 4px 12px; }}
.wrap {{ background:linear-gradient(160deg,#1a3a2a,#2d5a3d); border-radius:20px; padding:3px; box-shadow:0 8px 40px rgba(26,58,42,0.2); }}
.inner {{ background:#fdf8f3; border-radius:18px; padding:1.8rem 2.2rem; }}
.header {{ display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:1rem; gap:1rem; }}
.title {{ font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; color:#1a3a2a; line-height:1.2; }}
.title span {{ color:#d4af50; font-style:italic; }}
.badges {{ display:flex; flex-direction:column; align-items:flex-end; gap:5px; flex-shrink:0; }}
.badge {{ padding:3px 12px; border-radius:20px; font-size:0.68rem; font-weight:600; letter-spacing:1px; text-transform:uppercase; white-space:nowrap; border:1px solid; }}
.divider {{ height:1px; background:linear-gradient(to right,#d4af50,transparent); margin:0.8rem 0 1.4rem; }}
.day-block {{ margin-bottom:1.5rem; }}
.day-label {{ font-size:0.65rem; font-weight:700; letter-spacing:3px; text-transform:uppercase; color:#d4af50; margin-bottom:0.35rem; }}
.day-text {{ color:#3a2e20; font-size:0.94rem; line-height:1.8; }}
.cost-row {{ display:flex; justify-content:space-between; padding:0.5rem 0; border-bottom:1px solid #f0e8dc; font-size:0.9rem; color:#3a2e20; }}
.cost-row:last-child {{ border-bottom:none; }}
.cost-label {{ color:#5a4a38; }}
.cost-value {{ font-weight:600; color:#2d5a3d; }}
.cost-total-row {{ display:flex; justify-content:space-between; padding:0.7rem 0; margin-top:0.4rem; border-top:2px solid #d4af50; }}
.cost-total-label {{ font-weight:700; color:#1a3a2a; font-size:1rem; }}
.cost-total-value {{ font-weight:700; color:#1a3a2a; font-size:1rem; }}
.hotel-card {{ background:#fff; border:1px solid #e8e0d4; border-radius:10px; padding:0.9rem 1.1rem; margin-bottom:0.8rem; }}
.hotel-name {{ font-family:'Playfair Display',serif; font-weight:700; color:#1a3a2a; font-size:1rem; margin-bottom:0.3rem; }}
.hotel-meta {{ font-size:0.8rem; color:#8a7560; margin-bottom:0.3rem; }}
.hotel-why {{ font-size:0.87rem; color:#3a2e20; line-height:1.6; }}
.footer {{ margin-top:1rem; font-size:0.7rem; color:#b0a08a; text-align:right; font-style:italic; }}
</style></head><body>
<div class="wrap"><div class="inner">
  <div class="header">
    <div class="title">{title1}<br><span>{title2}</span></div>
    <div class="badges">{badges_html}</div>
  </div>
  <div class="divider"></div>
  {body_html}
  <div class="footer">{footer}</div>
</div></div>
</body></html>"""
    components.html(html, height=height, scrolling=True)

# ══════════════════════════════════════════════════════════════════
# LANGCHAIN LCEL: 3 CHAINED CALLS
# ══════════════════════════════════════════════════════════════════
if generate:
    if not api_key:
        st.error("⚠ GOOGLE_API_KEY not found in .env file.")
    elif not city.strip():
        st.warning("Please enter a destination city.")
    else:
        # ── CHAIN 1: Itinerary ─────────────────────────────────────
        itin_template = """You are an expert travel guide. Write a day-by-day itinerary.

Destination: {city}
Duration: {days} days
Budget: {budget} (Low=hostels & street food, Medium=mid-range, High=luxury)
Language: Respond in {language}

Rules:
- Exactly {days} day sections.
- Label each section exactly as "Day 1", "Day 2", etc. in English regardless of language.
- Each day: 4-5 sentences. Morning sight, famous landmark, food recommendation, afternoon activity, evening plan.
- Recommend real places specific to {city}.
- Plain text only. No *, **, #, bullets or markdown.
- Separate days with a blank line."""

        with st.spinner("✦ Chain 1 of 3 — Generating your itinerary…"):
            itinerary_text = run_chain(itin_template, {
                "city": city, "days": days,
                "budget": budget_clean, "language": language
            }, temp=0.9)
            st.session_state.itinerary = itinerary_text

        # ── CHAIN 2: Cost Estimate ─────────────────────────────────
        cost_template = """You are a travel budget expert. Based on this itinerary for {city} ({days} days, {budget} budget), estimate costs.

ITINERARY:
{itinerary}

Respond with ONLY these lines, no extra text:
Accommodation per night: [amount in USD]
Food per day: [amount in USD]
Local transport per day: [amount in USD]
Activities & entrance fees total: [amount in USD]
Miscellaneous: [amount in USD]
TOTAL ESTIMATED COST: [amount in USD]

Use realistic prices for {city} matching a {budget} budget."""

        with st.spinner("✦ Chain 2 of 3 — Estimating costs from your itinerary…"):
            cost_text = run_chain(cost_template, {
                "city": city, "days": days,
                "budget": budget_clean, "itinerary": itinerary_text
            }, temp=0.3)
            st.session_state.costs = cost_text

        # ── CHAIN 3: Hotel Suggestions ─────────────────────────────
        hotel_template = """You are a hotel expert. Based on this itinerary for {city} ({budget} budget), suggest 3 real hotels.

ITINERARY:
{itinerary}

For each hotel respond in EXACTLY this format (no extra text, no markdown):
HOTEL: [Hotel Name]
AREA: [Neighbourhood/Area]
PRICE: [Price per night in USD]
WHY: [1 sentence why it suits this itinerary]

Separate each hotel with a blank line.
Suggest real hotels that actually exist in {city}, matched to {budget} budget level."""

        with st.spinner("✦ Chain 3 of 3 — Finding hotels near your itinerary spots…"):
            hotel_text = run_chain(hotel_template, {
                "city": city, "budget": budget_clean,
                "itinerary": itinerary_text
            }, temp=0.5)
            st.session_state.hotels = hotel_text

        # ── Seed chat history with context ────────────────────────
        seed_context = (
            f"The user has a {days}-day trip to {city} on a {budget_clean} budget.\n\n"
            f"ITINERARY:\n{itinerary_text}\n\n"
            f"COST ESTIMATE:\n{cost_text}\n\n"
            f"HOTEL SUGGESTIONS:\n{hotel_text}"
        )
        st.session_state.chat_history = [
            {"role": "system", "content": seed_context}
        ]
        st.session_state.last_context = {
            "city": city, "days": days,
            "budget": budget_clean, "language": language
        }

# ══════════════════════════════════════════════════════════════════
# RENDER RESULTS
# ══════════════════════════════════════════════════════════════════
if st.session_state.itinerary:
    ctx      = st.session_state.last_context or {}
    r_city   = ctx.get("city", "")
    r_days   = ctx.get("days", days)
    r_budget = ctx.get("budget", budget_clean)
    r_lang   = ctx.get("language", language)
    r_bc     = budget_colors.get(r_budget, budget_colors["Medium"])

    common_badges = f"""
        <span class="badge" style="background:#eef7f0;color:#2d6a4f;border-color:#b7dfc7;">📅 {r_days} Days</span>
        <span class="badge" style="background:{r_bc['bg']};color:{r_bc['color']};border-color:{r_bc['border']};">💰 {r_budget}</span>
        <span class="badge" style="background:#f0eefa;color:#5b3fa6;border-color:#c4b5fd;">🌐 {escape(r_lang)}</span>"""

    # ── Card 1: Itinerary ──────────────────────────────────────────
    st.markdown("### 🗺 Your Itinerary")
    raw    = st.session_state.itinerary
    blocks = re.split(r'\n(?=Day \d+)', raw, flags=re.IGNORECASE)
    if len(blocks) < 2:
        blocks = [b for b in raw.split("\n\n") if b.strip()]

    days_html = ""
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines   = block.split("\n", 1)
        label   = escape(lines[0].strip())
        content = escape(lines[1].strip() if len(lines) > 1 else block)
        content = content.replace("\n", "<br>")
        days_html += f"""
        <div class="day-block">
            <div class="day-label">{label}</div>
            <div class="day-text">{content}</div>
        </div>"""

    render_card("Your", escape(r_city) + " Itinerary",
                days_html, common_badges,
                "Chain 1 · LangChain LCEL + Gemini 2.0 Flash",
                height=300 + r_days * 190)

    # ── Card 2: Cost Estimate ──────────────────────────────────────
    st.markdown("### 💰 Cost Estimate")
    cost_lines = [l.strip() for l in st.session_state.costs.split("\n") if l.strip()]
    cost_html  = ""
    for line in cost_lines:
        if ":" in line:
            k, v = line.split(":", 1)
            k, v = escape(k.strip()), escape(v.strip())
            is_total = "TOTAL" in k.upper()
            if is_total:
                cost_html += f"""
                <div class="cost-total-row">
                    <span class="cost-total-label">✦ {k}</span>
                    <span class="cost-total-value">{v}</span>
                </div>"""
            else:
                cost_html += f"""
                <div class="cost-row">
                    <span class="cost-label">{k}</span>
                    <span class="cost-value">{v}</span>
                </div>"""

    budget_badge = f'<span class="badge" style="background:{r_bc["bg"]};color:{r_bc["color"]};border-color:{r_bc["border"]};">💰 {r_budget} Budget</span>'
    render_card("Cost", "Estimate", cost_html, budget_badge,
                "Chain 2 · Costs estimated from itinerary context", height=320)

    # ── Card 3: Hotels ─────────────────────────────────────────────
    st.markdown("### 🏨 Hotel Suggestions")
    hotel_blocks = re.split(r'\n\n+', st.session_state.hotels)
    hotels_html  = ""
    for hblock in hotel_blocks:
        hblock = hblock.strip()
        if not hblock:
            continue
        hdata = {}
        for line in hblock.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                hdata[k.strip().upper()] = escape(v.strip())
        if "HOTEL" in hdata:
            hotels_html += f"""
            <div class="hotel-card">
                <div class="hotel-name">🏨 {hdata.get('HOTEL','')}</div>
                <div class="hotel-meta">📍 {hdata.get('AREA','')} &nbsp;·&nbsp; 💵 {hdata.get('PRICE','')}/night</div>
                <div class="hotel-why">{hdata.get('WHY','')}</div>
            </div>"""

    render_card("Hotel", "Suggestions", hotels_html, budget_badge,
                "Chain 3 · Hotels matched to itinerary locations & budget", height=380)

    # ══════════════════════════════════════════════════════════════
    # MEMORY CHAT (Chain 4) — manual history, no deprecated memory
    # ══════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:700;color:#1a3a2a;margin-bottom:0.2rem;">
        💬 Follow-up Chat
    </div>
    <div style="font-size:0.85rem;color:#8a7560;margin-bottom:1rem;">
        The AI remembers your full itinerary, costs &amp; hotels. Ask anything.
    </div>""", unsafe_allow_html=True)

    # Show chat history (skip the hidden system message at index 0)
    for msg in st.session_state.chat_history[1:]:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-wrap">
                <div class="chat-label" style="color:#2d6a4f;">You</div>
                <div class="chat-msg">{escape(msg['content'])}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-wrap">
                <div class="chat-label" style="color:#d4af50;">✦ Wandr AI</div>
                <div class="chat-msg">{escape(msg['content']).replace(chr(10), '<br>')}</div>
            </div>""", unsafe_allow_html=True)

    chat_input = st.text_input(
        "chat",
        placeholder="e.g. Make Day 2 cheaper · Best area to stay · Vegetarian food options…",
        label_visibility="collapsed"
    )
    ask = st.button("Ask ➜")

    if ask and chat_input.strip():
        with st.spinner("Thinking…"):
            # Build LangChain message list from history
            lc_messages = []
            for msg in st.session_state.chat_history:
                if msg["role"] == "system":
                    lc_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))
                else:
                    lc_messages.append(AIMessage(content=msg["content"]))
            lc_messages.append(HumanMessage(content=chat_input))

            llm = make_llm(temp=0.7)
            response = llm.invoke(lc_messages)
            reply = response.content.strip()

            st.session_state.chat_history.append({"role": "user", "content": chat_input})
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()