import streamlit as st

def render(top_50_risk, generate_outreach_func):
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        st.write("I've compiled a roster of the users most likely to leave due to operational friction. We can attempt to win them back, but let's make sure it's profitable first. Adjust the simulation dials below to see if an intervention campaign makes financial sense.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container(border=True):
        col_sim1, col_sim2 = st.columns([1, 1])
        with col_sim1:
            st.markdown("<br>", unsafe_allow_html=True)
            retention_cost = st.number_input("Cost per Retention Offer ($)", min_value=0, value=50, step=10, help="How much are you willing to spend (e.g., statement credit) to save a single user?")
            win_back_rate = st.slider("Expected Win-Back Rate (%)", 0, 100, 40, help="If we send a personalized apology, what percentage of users will actually stay?")
        
        total_campaign_cost = len(top_50_risk) * retention_cost
        projected_saved_revenue = (top_50_risk['Balance'].sum() * (win_back_rate / 100))
        net_roi = projected_saved_revenue - total_campaign_cost
        
        with col_sim2:
            st.markdown("""
            <style>
            .roi-panel {
                background: rgba(99, 102, 241, 0.05);
                border-radius: 12px;
                padding: 1.5rem;
                border: 1px solid rgba(99, 102, 241, 0.2);
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='roi-panel'>", unsafe_allow_html=True)
            st.metric("Total Campaign Cost", f"${total_campaign_cost:,.0f}")
            st.metric("Projected Saved Revenue", f"${projected_saved_revenue:,.0f}")
            
            roi_color = "#34d399" if net_roi >= 0 else "#f87171"
            st.markdown(f"**Net ROI Projection**<br><span style='font-size: 2.2rem; font-weight: 700; color: {roi_color};'>${net_roi:,.0f}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='font-size: 1.8rem; color: #f4f4f5;'>High-Risk User Roster</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.05rem; color: #a1a1aa; margin-top: -10px;'>Ranked dynamically by our live Random Forest model.</p>", unsafe_allow_html=True)
    
    top_50_risk_disp = top_50_risk.copy()
    top_50_risk_disp.reset_index(inplace=True, drop=True)
    top_50_risk_disp['Customer_ID'] = top_50_risk_disp.index.map(lambda x: f"USR-{1000 + x}")
    cols = ['Customer_ID'] + [col for col in top_50_risk_disp.columns if col != 'Customer_ID']
    top_50_risk_disp = top_50_risk_disp[cols]
    
    if 'Exited' in top_50_risk_disp.columns:
        st.dataframe(top_50_risk_disp.drop(columns=['Exited']), width='stretch', height=300)
    else:
        st.dataframe(top_50_risk_disp, width='stretch', height=300)
    
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        st.write("Pick any user from the roster above. I will use Gemini 2.5 to analyze their friction points and draft a highly personalized apology and retention offer.")
    
    with st.container(border=True):
        selected_cust_id = st.selectbox("Select a User to Recover:", top_50_risk_disp['Customer_ID'].tolist())
        
        if selected_cust_id:
            cust_profile = top_50_risk_disp[top_50_risk_disp['Customer_ID'] == selected_cust_id].iloc[0]
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px; margin-bottom: 1rem; font-size: 0.95rem;">
                <strong style="color: #6366f1;">Target Profile:</strong><br>
                Region: {cust_profile['Geography']} &nbsp;|&nbsp; 
                Age: {cust_profile['Age']} &nbsp;|&nbsp; 
                Balance: ${cust_profile['Balance']:,.2f} &nbsp;|&nbsp; 
                Failed Txs: {cust_profile.get('failed_transactions_last_30_days', 0)} &nbsp;|&nbsp; 
                <strong style="color: #ef4444;">Churn Risk: {cust_profile.get('Churn Risk (%)', 0)}%</strong>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🪄 Draft Personalized Email", type="primary"):
                with st.spinner("Analyzing the user's friction points and drafting..."):
                    outreach_script = generate_outreach_func(cust_profile)
                    
                    st.markdown("""
                    <style>
                    .generated-text {
                        background: rgba(15, 23, 42, 0.6);
                        border-left: 4px solid #34d399;
                        padding: 1.5rem;
                        border-radius: 8px;
                        font-family: 'Outfit', sans-serif;
                        color: #e2e8f0;
                        white-space: pre-wrap;
                        margin-top: 1rem;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    st.success("Draft ready for review!")
                    st.markdown(f"<div class='generated-text'>{outreach_script}</div>", unsafe_allow_html=True)
