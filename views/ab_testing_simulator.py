import streamlit as st
import numpy as np
from statsmodels.stats.proportion import proportions_ztest

def render():
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🧪 A/B Testing Simulator (Retention Campaign ROI)")
    st.markdown("Simulate a campaign where Group A (Control) receives no intervention, and Group B (Treatment) receives our AI-generated email and a $50 statement credit.")
    
    with st.container(border=True):
        col_ab1, col_ab2 = st.columns(2)
        with col_ab1:
            control_size = st.number_input("Control Group Size (N)", value=1000, step=100)
            control_retention = st.slider("Control Group Retention Rate (%)", 0, 100, 60)
        with col_ab2:
            treatment_size = st.number_input("Treatment Group Size (N)", value=1000, step=100)
            treatment_retention = st.slider("Treatment Group Retention Rate (%)", 0, 100, 68)
    
    # Phase 3: Z-Test Calculation
    control_success = int((control_retention / 100.0) * control_size)
    treatment_success = int((treatment_retention / 100.0) * treatment_size)
    
    counts = np.array([treatment_success, control_success])
    nobs = np.array([treatment_size, control_size])
    
    try:
        z_stat, p_val = proportions_ztest(counts, nobs)
        uplift = ((treatment_retention - control_retention) / control_retention) * 100 if control_retention > 0 else 0
        
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Relative Uplift", f"{uplift:+.2f}%")
        col_res2.metric("Z-Score", f"{z_stat:.3f}")
        col_res3.metric("P-Value", f"{p_val:.4f}")
        
        st.markdown("---")
        if p_val < 0.05:
            st.success(f"✅ **Statistically Significant:** Roll out campaign! (p < 0.05). We are confident that the treatment outperformed the control.")
        else:
            st.warning(f"⚠️ **Fail to Reject Null Hypothesis:** (p >= 0.05). The difference in retention is not statistically significant. Do not roll out the campaign.")
    except Exception as e:
        st.error("Please enter valid numbers for the A/B test.")
