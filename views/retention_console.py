import streamlit as st

def render(top_50_risk, generate_outreach_func):
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Intervention ROI Simulator")
    st.markdown("<p style='font-size: 0.9rem; color: #94a3b8; margin-top: -10px;'>If we offer angry customers money to stay, do we still make a profit? Play with the numbers to find out.</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        col_sim1, col_sim2 = st.columns(2)
        with col_sim1:
            retention_cost = st.number_input("Cost of Retention Offer ($/user)", min_value=0, value=50, step=10, help="How much are you willing to spend (e.g. statement credit) to save a single customer?")
            win_back_rate = st.slider("Expected Win-Back Success Rate (%)", 0, 100, 40, help="If we send the apology email, what percentage of customers will actually decide to stay?")
        
        total_campaign_cost = len(top_50_risk) * retention_cost
        projected_saved_revenue = (top_50_risk['Balance'].sum() * (win_back_rate / 100))
        net_roi = projected_saved_revenue - total_campaign_cost
        
        with col_sim2:
            st.metric("Total Campaign Cost", f"${total_campaign_cost:,.0f}")
            st.metric("Projected Saved Revenue", f"${projected_saved_revenue:,.0f}")
            st.metric("Net ROI", f"${net_roi:,.0f}", delta=f"{win_back_rate}% Success Rate")
    
    st.markdown("---")
    
    st.subheader("Top 50 'High-Risk' Customers")
    st.markdown("Users heavily impacted by payment failures, ranked by Live ML Prediction Risk.")
    
    top_50_risk_disp = top_50_risk.copy()
    top_50_risk_disp.reset_index(inplace=True, drop=True)
    top_50_risk_disp['Customer_ID'] = top_50_risk_disp.index.map(lambda x: f"CUST-{1000 + x}")
    cols = ['Customer_ID'] + [col for col in top_50_risk_disp.columns if col != 'Customer_ID']
    top_50_risk_disp = top_50_risk_disp[cols]
    
    if 'Exited' in top_50_risk_disp.columns:
        st.dataframe(top_50_risk_disp.drop(columns=['Exited']), use_container_width=True)
    else:
        st.dataframe(top_50_risk_disp, use_container_width=True)
    
    st.markdown("---")
    st.subheader("AI-Powered Customer Recovery")
    
    selected_cust_id = st.selectbox("Select Customer to Recover:", top_50_risk_disp['Customer_ID'].tolist())
    
    if selected_cust_id:
        cust_profile = top_50_risk_disp[top_50_risk_disp['Customer_ID'] == selected_cust_id].iloc[0]
        
        st.write(f"**Selected Profile:** {cust_profile['Geography']} | Age: {cust_profile['Age']} | Balance: ${cust_profile['Balance']:,.2f} | Failed TXs: {cust_profile.get('failed_transactions_last_30_days', 0)} | **Churn Risk:** {cust_profile.get('Churn Risk (%)', 0)}%")
        
        if st.button("Generate Personalized Recovery Email"):
            with st.spinner("Gemini is drafting the outreach..."):
                outreach_script = generate_outreach_func(cust_profile)
                st.success("Outreach Script Generated Successfully!")
                st.text_area("Copy and paste to CRM:", value=outreach_script, height=250)
