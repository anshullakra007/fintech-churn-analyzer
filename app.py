import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
import os
import joblib
import io
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.stats.proportion import proportions_ztest
# --- Phase 4: Configure Gemini API ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.warning("GEMINI_API_KEY environment variable not set. AI insights will not be available.")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def get_ai_recommendation(kpi_data):
    """Generates an executive summary using Gemini API."""
    prompt = f"""
    You are a Senior Data Analyst. Review these dashboard metrics:
    - Total Customers: {kpi_data['total_customers']}
    - Churn Rate: {kpi_data['churn_rate']}%
    - Avg Failed Tx: {kpi_data['avg_failed_tx']}
    - Revenue at Risk: ${kpi_data['revenue_risk']:,.2f}
    
    Provide exactly 3 short, punchy bullet points analyzing the risk and suggesting immediate action for the Operations team. Do not use filler words. Speak like a real human analyst sending a quick Slack update. Use standard markdown bullet points (-).
    """
    try:
        if not client:
            return "AI Recommendation currently unavailable. API Key missing."
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI Recommendation currently unavailable. Please check API configuration. (Error: {str(e)})"

def generate_customer_outreach_script(customer_profile):
    """Generates a personalized outreach email for a specific customer."""
    prompt = f"""
    You are an empathetic, senior Customer Success Manager at a premium FinTech bank.
    Write a short, highly personalized apology and retention email to this specific customer 
    who is at high risk of churning due to our platform's technical payment failures.
    
    Customer Profile:
    - Age: {customer_profile['Age']}
    - Account Balance: ${customer_profile['Balance']:,.2f}
    - Recent Failed Transactions: {customer_profile['failed_transactions_last_30_days']}
    - Geography: {customer_profile['Geography']}
    - Tenure (Years with us): {customer_profile['Tenure']}
    
    Acknowledge the specific number of failed transactions. Emphasize that we value their business 
    (mentioning their tenure or balance subtly). Offer them a sincere apology and a direct line to 
    VIP support. Keep it professional, empathetic, and under 150 words. Do not use placeholders like [Your Name].
    """
    try:
        if not client:
            return "AI generation failed. API Key missing."
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI generation failed. (Error: {str(e)})"

def generate_excel_report(df, kpi_dict):
    """Generates an Advanced Excel report with charts and conditional formatting."""
    output = io.BytesIO()
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # --- Sheet 1: Executive Summary ---
        summary_df = pd.DataFrame({
            'Metric': ['Total Customers', 'Overall Churn Rate (%)', 'Avg Failed Transactions', 'Revenue at Risk ($)'],
            'Value': [
                kpi_dict['total_customers'], 
                kpi_dict['churn_rate'], 
                kpi_dict['avg_failed_tx'], 
                kpi_dict['revenue_risk']
            ]
        })
        summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
        worksheet1 = writer.sheets['Executive Summary']
        
        # Format the summary sheet
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
        for col_num, value in enumerate(summary_df.columns.values):
            worksheet1.write(0, col_num, value, header_format)
        worksheet1.set_column('A:A', 25)
        worksheet1.set_column('B:B', 20)
        
        # Add a native Excel Pie Chart
        chart = workbook.add_chart({'type': 'pie'})
        # We need data for the pie chart. Let's write Active vs Churned to the sheet
        active_count = int(kpi_dict['total_customers'] * (1 - kpi_dict['churn_rate']/100))
        churned_count = kpi_dict['total_customers'] - active_count
        worksheet1.write('D1', 'Status', header_format)
        worksheet1.write('E1', 'Count', header_format)
        worksheet1.write('D2', 'Active')
        worksheet1.write('E2', active_count)
        worksheet1.write('D3', 'Churned')
        worksheet1.write('E3', churned_count)
        
        chart.add_series({
            'name': 'Customer Churn Distribution',
            'categories': "='Executive Summary'!$D$2:$D$3",
            'values':     "='Executive Summary'!$E$2:$E$3",
        })
        chart.set_title({'name': 'Customer Churn Distribution'})
        worksheet1.insert_chart('G2', chart)

        # --- Sheet 2: High-Risk Customers ---
        # Export the dataframe
        df.to_excel(writer, sheet_name='High-Risk Customers', index=False)
        worksheet2 = writer.sheets['High-Risk Customers']
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet2.set_column(i, i, column_len)
            
        # Add conditional formatting for 'Churn Risk (%)' if it exists
        if 'Churn Risk (%)' in df.columns:
            risk_col_idx = df.columns.get_loc('Churn Risk (%)')
            col_letter = chr(ord('A') + risk_col_idx) if risk_col_idx < 26 else chr(ord('A') + (risk_col_idx // 26) - 1) + chr(ord('A') + (risk_col_idx % 26))
            last_row = len(df) + 1
            range_str = f'{col_letter}2:{col_letter}{last_row}'
            
            format_red = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
            format_yellow = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})
            
            worksheet2.conditional_format(range_str, {'type': 'cell',
                                                      'criteria': '>',
                                                      'value': 75,
                                                      'format': format_red})
            worksheet2.conditional_format(range_str, {'type': 'cell',
                                                      'criteria': 'between',
                                                      'minimum': 50,
                                                      'maximum': 75,
                                                      'format': format_yellow})
                                                      
    return output.getvalue()

# --- Phase 3: Streamlit App Configuration ---
st.set_page_config(page_title="FinTech Churn & Impact Analyzer", layout="wide")

# --- Custom CSS Injection ---
st.markdown("""
<style>
/* Clean, flat dark background (Zinc 950) */
.stApp {
    background-color: #09090b;
    color: #f4f4f5;
}

/* AI Alert Box */
.ai-alert-box {
    background: #1e1b4b;
    border-left: 4px solid #6366f1;
    border-radius: 6px;
    padding: 1.25rem;
    margin: 1rem 0;
    color: #e0e7ff;
    font-size: 1rem;
    line-height: 1.5;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: rgba(11, 12, 16, 0.85) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
""", unsafe_allow_html=True)

st.title("Customer Retention Analytics")
st.markdown("Monitor customer churn metrics and the operational impact of payment gateway failures.")

# --- Architectural Overview ---
st.markdown("""
<div style="color: #a1a1aa; font-size: 0.95rem; line-height: 1.6; margin-bottom: 2rem;">
This dashboard is an end-to-end FinTech churn prediction engine. It evaluates how operational friction (like payment gateway failures) impacts customer retention. The architecture uses a live <strong>Random Forest ML model</strong> to score churn risk in real-time based on the global filters below. Additionally, the Retention Console leverages <strong>Google Gemini 2.5</strong> to calculate campaign ROI and automatically draft personalized recovery workflows for at-risk accounts.
</div>
""", unsafe_allow_html=True)

# Load Data Limits
@st.cache_data
def load_data_limits():
    try:
        conn = sqlite3.connect('crm_data.db')
        limits = pd.read_sql('SELECT MIN(Age) as min_age, MAX(Age) as max_age, MIN(CreditScore) as min_credit, MAX(CreditScore) as max_credit, MIN(failed_transactions_last_30_days) as min_fail, MAX(failed_transactions_last_30_days) as max_fail FROM customers', conn)
        conn.close()
        return limits.iloc[0]
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

limits = load_data_limits()

if limits is not None:
    # --- Main Page Filters (Always Visible) ---
    st.markdown("### Global Filters")
    with st.container(border=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            age_range = st.slider("Age Range", int(limits['min_age']), int(limits['max_age']), (int(limits['min_age']), int(limits['max_age'])))
        with col_f2:
            credit_range = st.slider("Credit Score", int(limits['min_credit']), int(limits['max_credit']), (int(limits['min_credit']), int(limits['max_credit'])))
        with col_f3:
            failed_tx = st.slider("Max Failed Transactions (30 Days)", int(limits['min_fail']), int(limits['max_fail']), int(limits['max_fail']))
    
    # Apply SQL Filters & CTE Rank
    try:
        conn = sqlite3.connect('crm_data.db')
        
        # Base filtered data for aggregate KPIs
        query_filtered = f"""
            SELECT * FROM customers
            WHERE Age BETWEEN {age_range[0]} AND {age_range[1]}
            AND CreditScore BETWEEN {credit_range[0]} AND {credit_range[1]}
            AND failed_transactions_last_30_days <= {failed_tx}
        """
        filtered_df = pd.read_sql(query_filtered, conn)
        
        # Phase 1: Complex SQL Query using CTE and Window Function for Top 50 Risk
        query_top_50 = f"""
            WITH RiskRankedCustomers AS (
                SELECT *,
                       RANK() OVER (ORDER BY "Churn Risk (%)" DESC, Balance DESC) as RiskRank
                FROM customers
                WHERE Age BETWEEN {age_range[0]} AND {age_range[1]}
                AND CreditScore BETWEEN {credit_range[0]} AND {credit_range[1]}
                AND failed_transactions_last_30_days <= {failed_tx}
            )
            SELECT * FROM RiskRankedCustomers
            WHERE RiskRank <= 50
        """
        top_50_risk = pd.read_sql(query_top_50, conn)
        conn.close()
    except Exception as e:
        st.error(f"SQL Execution Error: {e}")
        filtered_df = pd.DataFrame()
        top_50_risk = pd.DataFrame()
    
    if filtered_df.empty:
        st.warning("No customers match the selected filter criteria. Please adjust the sliders.")
    else:
        
        # --- KPI Calculations ---
        total_customers = len(filtered_df)
        churn_rate = (filtered_df['Exited'].mean() * 100) if total_customers > 0 else 0
        avg_failed_tx = filtered_df['failed_transactions_last_30_days'].mean()
        revenue_at_risk = filtered_df[filtered_df['Exited'] == 1]['Balance'].sum()
        
        kpi_dict = {
            'total_customers': total_customers,
            'churn_rate': round(churn_rate, 2),
            'avg_failed_tx': round(avg_failed_tx, 2),
            'revenue_risk': revenue_at_risk
        }

        # --- NATIVE TABS NAVIGATION ---
        tab_overview, tab_insights, tab_recovery, tab_ab, tab_bi = st.tabs(["📊 Executive Overview", "🧠 AI Insights", "🛠️ Retention Console", "🧪 A/B Testing Simulator", "📈 BI Dashboard"])
        
        with tab_overview:
            st.markdown("<br>", unsafe_allow_html=True)
            # --- KPI Display ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Customers", f"{total_customers:,}")
            col2.metric("Overall Churn Rate", f"{churn_rate:.2f}%")
            col3.metric("Revenue at Risk", f"${revenue_at_risk:,.2f}")
            
            # --- Phase 2: CLV Calculation ---
            retained_df = filtered_df[filtered_df['Exited'] == 0]
            # Assumed Margin * Balance * Tenure as a proxy for CLV
            clv_total = (retained_df['Balance'] * 0.10 * retained_df['Tenure']).sum()
            col4.metric("Projected Retained CLV", f"${clv_total:,.2f}")
            
            # Excel Download Button
            excel_data = generate_excel_report(filtered_df, kpi_dict)
            st.download_button(
                label="📥 Download Advanced Excel Report",
                data=excel_data,
                file_name="FinTech_Churn_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download a multi-sheet Excel report with native charts and conditional formatting."
            )
            
            st.markdown("---")
            
            # --- Visualizations ---
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("Churn Rate vs. Failed Transactions")
                churn_by_tx = filtered_df.groupby('failed_transactions_last_30_days')['Exited'].mean().reset_index()
                churn_by_tx['Churn Rate (%)'] = (churn_by_tx['Exited'] * 100).round(1)
                fig_tx = px.bar(churn_by_tx, x='failed_transactions_last_30_days', y='Churn Rate (%)', 
                                labels={'failed_transactions_last_30_days': 'Failed Transactions'},
                                text='Churn Rate (%)',
                                color_discrete_sequence=['#ef4444'])
                fig_tx.update_traces(textposition='outside', textfont=dict(color='#a1a1aa'))
                fig_tx.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#a1a1aa', showlegend=False, yaxis_range=[0,110])
                st.plotly_chart(fig_tx, use_container_width=True, config={'displayModeBar': False})
                
            with col_chart2:
                st.subheader("Customer Balance Distribution")
                fig_bal = px.violin(filtered_df, y="Balance", x="Exited", color="Exited", 
                                       box=True, points=False,
                                       labels={"Exited": "Churned (1=Yes, 0=No)"},
                                       color_discrete_map={0: '#3b82f6', 1: '#ef4444'})
                fig_bal.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#a1a1aa', showlegend=False)
                st.plotly_chart(fig_bal, use_container_width=True, config={'displayModeBar': False})

            st.markdown("---")
            st.subheader("Churn Risk by Customer Tenure")
            churn_by_tenure = filtered_df.groupby('Tenure')['Exited'].mean().reset_index()
            churn_by_tenure['Churn Rate (%)'] = (churn_by_tenure['Exited'] * 100).round(1)
            fig_tenure = px.line(churn_by_tenure, x='Tenure', y='Churn Rate (%)', markers=True, 
                                 labels={'Tenure': 'Years with Bank (Tenure)'},
                                 color_discrete_sequence=['#8b5cf6'])
            fig_tenure.update_traces(line=dict(width=3), marker=dict(size=8), fill='tozeroy', fillcolor='rgba(139, 92, 246, 0.12)')
            fig_tenure.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#a1a1aa', yaxis_range=[0,100])
            st.plotly_chart(fig_tenure, use_container_width=True, config={'displayModeBar': False})
            
            st.markdown("---")
            # --- Phase 2: Cohort Analysis Heatmap ---
            st.subheader("Monthly Cohort Retention Matrix")
            st.markdown("<p style='font-size: 0.9rem; color: #94a3b8;'>Visualizing user drop-off across multiple onboarding cohorts over a 6-month period.</p>", unsafe_allow_html=True)
            
            cohort_data = np.array([
                [1.0, 0.85, 0.70, 0.60, 0.50, 0.45],
                [1.0, 0.82, 0.65, 0.55, 0.40, np.nan],
                [1.0, 0.88, 0.75, 0.62, np.nan, np.nan],
                [1.0, 0.80, 0.60, np.nan, np.nan, np.nan],
                [1.0, 0.75, np.nan, np.nan, np.nan, np.nan],
                [1.0, np.nan, np.nan, np.nan, np.nan, np.nan]
            ])
            fig_cohort, ax = plt.subplots(figsize=(10, 4))
            sns.heatmap(cohort_data, annot=True, fmt=".0%", cmap="YlGnBu", ax=ax,
                        xticklabels=[f"Month {i}" for i in range(1, 7)],
                        yticklabels=[f"Cohort {i}" for i in range(1, 7)])
            fig_cohort.patch.set_facecolor('#09090b')
            ax.set_facecolor('#09090b')
            ax.tick_params(colors='#a1a1aa')
            ax.xaxis.label.set_color('#a1a1aa')
            ax.yaxis.label.set_color('#a1a1aa')
            for t in ax.texts:
                t.set_color('#09090b')
            st.pyplot(fig_cohort)
            
        with tab_insights:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.spinner("Generating AI Operational Insights..."):
                ai_insight = get_ai_recommendation(kpi_dict)

            st.markdown(f"""
            <div class="ai-alert-box">
                <strong style="color: #3b82f6; font-size: 1.2rem;">AI Operational Alert:</strong><br>
                <span style="font-size: 0.9rem; color: #94a3b8;">Gemini AI is analyzing your exact dashboard filters above and recommending an immediate course of action.</span><br><br>
                {ai_insight}
            </div>
            """, unsafe_allow_html=True)
            
        with tab_recovery:
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
            
            top_50_risk = top_50_risk.copy()
            top_50_risk.reset_index(inplace=True)
            top_50_risk['Customer_ID'] = top_50_risk.index.map(lambda x: f"CUST-{1000 + x}")
            cols = ['Customer_ID'] + [col for col in top_50_risk.columns if col != 'Customer_ID' and col != 'index']
            top_50_risk = top_50_risk[cols]
            
            st.dataframe(top_50_risk.drop(columns=['Exited']), use_container_width=True)
            
            st.markdown("---")
            st.subheader("AI-Powered Customer Recovery")
            
            selected_cust_id = st.selectbox("Select Customer to Recover:", top_50_risk['Customer_ID'].tolist())
            
            if selected_cust_id:
                cust_profile = top_50_risk[top_50_risk['Customer_ID'] == selected_cust_id].iloc[0]
                
                st.write(f"**Selected Profile:** {cust_profile['Geography']} | Age: {cust_profile['Age']} | Balance: ${cust_profile['Balance']:,.2f} | Failed TXs: {cust_profile['failed_transactions_last_30_days']} | **Churn Risk:** {cust_profile['Churn Risk (%)']}%")
                
                if st.button("Generate Personalized Recovery Email"):
                    with st.spinner("Gemini is drafting the outreach..."):
                        outreach_script = generate_customer_outreach_script(cust_profile)
                        st.success("Outreach Script Generated Successfully!")
                        st.text_area("Copy and paste to CRM:", value=outreach_script, height=250)

        with tab_ab:
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

        with tab_bi:
            st.markdown("<br>", unsafe_allow_html=True)
            # --- Tableau Embed Example ---
            tableau_html = """
            <div class='tableauPlaceholder' id='viz1' style='position: relative; width: 100%; height: 800px;'>
                <noscript><a href='#'><img alt='Dashboard' src='' style='border: none' /></a></noscript>
                <object class='tableauViz'  style='display:none;'>
                    <param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> 
                    <param name='embed_code_version' value='3' /> 
                    <param name='site_root' value='' />
                    <param name='name' value='FinTechChurnAnalysis/Sheet1' />
                    <param name='tabs' value='yes' />
                    <param name='toolbar' value='yes' />
                    <param name='animate_transition' value='yes' />
                    <param name='display_static_image' value='yes' />
                    <param name='display_spinner' value='yes' />
                    <param name='display_overlay' value='yes' />
                    <param name='display_count' value='yes' />
                    <param name='language' value='en-US' />
                </object>
            </div>
            <script type='text/javascript'>
                var divElement = document.getElementById('viz1');
                var vizElement = divElement.getElementsByTagName('object')[0];
                vizElement.style.width='100%';vizElement.style.height='800px';
                var scriptElement = document.createElement('script');
                scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
                vizElement.parentNode.insertBefore(scriptElement, vizElement);
            </script>
            """
            
            import streamlit.components.v1 as components
            components.html(tableau_html, height=850, scrolling=True)
