import streamlit as st

def render(kpi_dict, get_ai_recommendation_func):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="ai-alert-box">
        <strong style="color: #3b82f6; font-size: 1.2rem;">AI Operational Alert:</strong><br>
        <span style="font-size: 0.9rem; color: #94a3b8;">Gemini AI is ready to analyze your exact dashboard filters and recommend an immediate course of action.</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Generate AI Operational Insights", type="primary", use_container_width=True):
        with st.spinner("Analyzing dashboard metrics..."):
            ai_insight = get_ai_recommendation_func(kpi_dict)
        st.info(ai_insight, icon="🧠")
    else:
        st.info("Click the button above to generate a real-time AI report based on your current filters.", icon="ℹ️")
