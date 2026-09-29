import streamlit as st
from rag import ask

st.set_page_config(page_title="مساعد نظام العمل", page_icon="⚖️", layout="centered")

# ---------- Custom styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

    html, body, .stApp, .stMarkdown, button, input, textarea, p, div {
        font-family: 'Tajawal', sans-serif !important;
    }

    .stApp {
        direction: rtl;
        text-align: right;
        background: linear-gradient(180deg, #F7F5EF 0%, #EEF3EF 100%);
    }

    /* Hide Streamlit menu, header and footer */
    #MainMenu, header, footer, [data-testid="stToolbar"] { visibility: hidden; }

    /* Hero header */
    .hero {
        background: linear-gradient(135deg, #0E4D32 0%, #1B6B47 100%);
        border-radius: 20px;
        padding: 34px 30px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(14, 77, 50, 0.25);
        border-bottom: 4px solid #C9A227;
    }
    .hero-title { font-size: 2rem; font-weight: 800; margin-bottom: 8px; }
    .hero-sub { color: #E3EEE7; font-size: 1.05rem; line-height: 1.8; }
    .badges span {
        display: inline-block;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(201, 162, 39, 0.6);
        padding: 4px 14px;
        border-radius: 999px;
        margin: 16px 0 0 8px;
        font-size: 0.85rem;
    }

    /* Example question buttons */
    .stButton > button {
        border-radius: 14px;
        border: 1px solid #D7E3DB;
        background: white;
        color: #0E4D32;
        font-weight: 600;
        padding: 12px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: #0E4D32;
        background: #0E4D32;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(14, 77, 50, 0.2);
    }

    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        background: white;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border: 1px solid #ECEFEA;
        margin-bottom: 12px;
    }

    /* Sources expander */
    [data-testid="stExpander"] {
        border-radius: 12px;
        border: 1px solid #E3E9E4;
        background: #FAFBF9;
    }

    /* Chat input */
    [data-testid="stChatInput"] textarea { direction: rtl; text-align: right; }

    .section-label { color: #0E4D32; font-weight: 700; margin: 8px 0 12px 0; }
    .disclaimer { text-align: center; color: #6B7A70; font-size: 0.85rem; margin-top: 28px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Header ----------
st.markdown(
    """
    <div class="hero">
        <div class="hero-title">⚖️ المساعد الذكي لنظام العمل السعودي</div>
        <div class="hero-sub">اسأل عن حقوقك وواجباتك في العمل، واحصل على إجابة مستندة إلى مواد النظام مع ذكر المصدر.</div>
        <div class="badges">
            <span>245 مادة نظامية</span>
            <span>إجابات موثّقة بالمصدر</span>
            <span>مدعوم بالذكاء الاصطناعي</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Conversation memory ----------
if "messages" not in st.session_state:
    st.session_state.messages = []


def show_sources(sources):
    if sources:
        with st.expander("📜 المصادر — نص المواد الأصلي"):
            for s in sources:
                st.markdown(f"**{s['article']}**")
                st.write(s["text"])
                st.divider()


# ---------- Example questions ----------
clicked = None
if not st.session_state.messages:
    st.markdown('<div class="section-label">جرّب أحد هذه الأسئلة:</div>', unsafe_allow_html=True)
    examples = [
        "كم مدة الإجازة المرضية؟",
        "كيف تحسب مكافأة نهاية الخدمة؟",
        "كم ساعات العمل اليومية؟",
        "كم مدة إجازة الوضع للمرأة العاملة؟",
        "كم مدة فترة التجربة؟",
        "كيف يُحتسب أجر العمل الإضافي؟",
    ]
    for row in range(0, len(examples), 3):
        cols = st.columns(3)
        for col, ex in zip(cols, examples[row:row + 3]):
            if col.button(ex, use_container_width=True):
                clicked = ex
else:
    if st.button("🗑️ محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# ---------- Chat history ----------
AVATARS = {"user": "👤", "assistant": "⚖️"}

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=AVATARS[msg["role"]]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            show_sources(msg.get("sources"))

# ---------- New question ----------
typed = st.chat_input("اكتب سؤالك هنا...")
question = typed or clicked

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(question)

    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        with st.spinner("أبحث في مواد النظام..."):
            answer, sources = ask(question)
        st.markdown(answer)
        show_sources(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
    st.rerun()

st.markdown(
    '<div class="disclaimer">⚠️ هذه الإجابات للاسترشاد فقط ولا تغني عن الاستشارة القانونية المتخصصة.</div>',
    unsafe_allow_html=True,
)