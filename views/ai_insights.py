import streamlit as st

def render(kpi_dict, get_ai_recommendation_func):
    st.markdown("<br>", unsafe_allow_html=True)
    with st.spinner("Generating AI Operational Insights..."):
        ai_insight = get_ai_recommendation_func(kpi_dict)

    st.markdown(f"""
    <div class="ai-alert-box">
        <strong style="color: #3b82f6; font-size: 1.2rem;">AI Operational Alert:</strong><br>
        <span style="font-size: 0.9rem; color: #94a3b8;">Gemini AI is analyzing your exact dashboard filters above and recommending an immediate course of action.</span><br><br>
        {ai_insight}
    </div>
    """, unsafe_allow_html=True)
