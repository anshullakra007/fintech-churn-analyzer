import streamlit as st

def render(kpi_dict, get_ai_recommendation_func):
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    .ai-hero {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.8) 0%, rgba(17, 24, 39, 0.9) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 10px 40px -10px rgba(99, 102, 241, 0.2);
        position: relative;
        overflow: hidden;
    }
    .ai-hero::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 60%);
        animation: pulse 8s infinite alternate;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.5; }
        100% { transform: scale(1.05); opacity: 1; }
    }
    .ai-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(to right, #a78bfa, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        position: relative;
    }
    .ai-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        max-width: 600px;
        margin: 0 auto 2rem auto;
        position: relative;
    }
    .ai-insight-result {
        background: rgba(15, 23, 42, 0.7);
        border-left: 4px solid #818cf8;
        padding: 2rem;
        border-radius: 12px;
        font-size: 1.15rem;
        line-height: 1.8;
        color: #e2e8f0;
        margin-top: 2rem;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="ai-hero">
        <div class="ai-title">✨ Gemini Operational Strategist</div>
        <div class="ai-subtitle">
            Don't just stare at the data. Let Gemini 2.5 instantly analyze your current audience filters and give you three bulletproof action items.
        </div>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("Generate Strategic Action Plan", type="primary", width='stretch'):
            with st.spinner("Gemini is crunching the metrics..."):
                ai_insight = get_ai_recommendation_func(kpi_dict)
            
            st.markdown(f"""
            <div class="ai-insight-result">
                <strong style="color: #818cf8; font-size: 1.25rem;">Immediate Action Required:</strong><br><br>
                {ai_insight.replace('-', '<br>•')}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align: center; color: #64748b; margin-top: 1rem;'>Awaiting your command.</p>", unsafe_allow_html=True)
