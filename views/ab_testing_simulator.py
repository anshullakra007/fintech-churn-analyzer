import streamlit as st
import numpy as np
from statsmodels.stats.proportion import proportions_ztest

def render():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size: 2.2rem; color: #f4f4f5;'>Experimentation Lab</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1rem; color: #a1a1aa; max-width: 800px;'>Test your retention campaign hypotheses before full rollout. Simulate an A/B test where the Control Group gets nothing, and the Treatment Group gets your personalized AI outreach and incentive.</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container(border=True):
        col_ab1, col_ab2 = st.columns(2)
        with col_ab1:
            st.markdown("<h3 style='color: #94a3b8; font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;'>Scenario A: The Status Quo</h3>", unsafe_allow_html=True)
            control_size = st.number_input("How many users are in this group?", value=1000, step=100, key="c_size")
            control_retention = st.slider("What is our baseline retention rate? (%)", 0, 100, 60, key="c_ret")
        with col_ab2:
            st.markdown("<h3 style='color: #818cf8; font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;'>Scenario B: Our New Strategy</h3>", unsafe_allow_html=True)
            treatment_size = st.number_input("How many users receive the new offer?", value=1000, step=100, key="t_size")
            treatment_retention = st.slider("What is our target retention rate? (%)", 0, 100, 68, key="t_ret")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Z-Test Calculation
    control_success = int((control_retention / 100.0) * control_size)
    treatment_success = int((treatment_retention / 100.0) * treatment_size)
    
    counts = np.array([treatment_success, control_success])
    nobs = np.array([treatment_size, control_size])
    
    try:
        z_stat, p_val = proportions_ztest(counts, nobs)
        uplift = ((treatment_retention - control_retention) / control_retention) * 100 if control_retention > 0 else 0
        
        st.markdown("<h3 style='color: #e4e4e7; font-size: 1.4rem;'>The Verdict</h3>", unsafe_allow_html=True)
        
        col_res1, col_res2 = st.columns(2)
        col_res1.metric("Projected Uplift", f"{uplift:+.2f}%")
        col_res2.metric("Confidence Level", f"{(1 - p_val)*100:.1f}%")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if p_val < 0.05:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 1.5rem; border-radius: 8px;">
                <h4 style="color: #10b981; margin-top: 0; font-size: 1.2rem;">Green Light: High Confidence</h4>
                <p style="color: #d1fae5; margin-bottom: 0;">We are highly confident that the intervention outperformed the baseline. The risk of this being a false positive is less than 5%. <strong>Recommendation: Proceed with full campaign rollout.</strong></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 1.5rem; border-radius: 8px;">
                <h4 style="color: #f59e0b; margin-top: 0; font-size: 1.2rem;">Yellow Light: Too Risky to Deploy</h4>
                <p style="color: #fef3c7; margin-bottom: 0;">The difference in retention might just be statistical noise. We cannot confidently attribute the uplift to the intervention. <strong>Recommendation: Do not roll out. Redesign the offer or increase sample size.</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error("Please enter valid numbers to calculate significance.")
