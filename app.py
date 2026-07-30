import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import os

# --- Phase 4: Configure Gemini API ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.warning("GEMINI_API_KEY environment variable not set. AI insights will not be available.")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_recommendation(kpi_data):
    """Generates an executive summary using Gemini API."""
    prompt = f"""
    You are a Senior FinTech Operations Consultant. 
    Analyze the following current dashboard KPIs for a banking application:
    - Total Customers in view: {kpi_data['total_customers']}
    - Overall Churn Rate: {kpi_data['churn_rate']}%
    - Average Failed Transactions (last 30 days): {kpi_data['avg_failed_tx']}
    - Revenue at Risk (Balance of high-risk customers): ${kpi_data['revenue_risk']:,.2f}
    
    Based heavily on the number of failed transactions and the revenue at risk, 
    provide a concise, 3-sentence 'Executive Summary & Operational Recommendation' 
    alerting the operations and collections team on immediate actions. Do not use markdown formatting.
    """
    try:
        response = model.generate_content(prompt)
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
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI generation failed. (Error: {str(e)})"
# --- Phase 3: Streamlit App Configuration ---
st.set_page_config(page_title="FinTech Churn & Impact Analyzer", page_icon="💸", layout="wide")

st.title("💸 FinTech Customer Churn & Impact Analyzer")
st.markdown("Monitor customer churn metrics and the operational impact of payment gateway failures.")

# Load Data
@st.cache_data
def load_data():
    try:
        # Load the augmented dataset from Phase 1
        df = pd.read_csv("data/synthetic_churn_data.csv")
        return df
    except FileNotFoundError:
        st.error("Dataset not found. Please ensure 'data/synthetic_churn_data.csv' exists.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- Sidebar Filters ---
    st.sidebar.header("Filter Data")
    
    age_range = st.sidebar.slider("Age", int(df['Age'].min()), int(df['Age'].max()), (int(df['Age'].min()), int(df['Age'].max())))
    credit_range = st.sidebar.slider("Credit Score", int(df['CreditScore'].min()), int(df['CreditScore'].max()), (int(df['CreditScore'].min()), int(df['CreditScore'].max())))
    failed_tx = st.sidebar.slider("Max Failed Transactions (30 Days)", int(df['failed_transactions_last_30_days'].min()), int(df['failed_transactions_last_30_days'].max()), int(df['failed_transactions_last_30_days'].max()))
    
    # Apply Filters
    filtered_df = df[
        (df['Age'].between(age_range[0], age_range[1])) &
        (df['CreditScore'].between(credit_range[0], credit_range[1])) &
        (df['failed_transactions_last_30_days'] <= failed_tx)
    ]
    
    # --- Phase 5: Intervention ROI Simulator (Sidebar) ---
    st.sidebar.markdown("---")
    st.sidebar.header("🎯 Intervention ROI Simulator")
    retention_cost = st.sidebar.number_input("Cost of Retention Offer ($/user)", min_value=0, value=50, step=10)
    win_back_rate = st.sidebar.slider("Expected Win-Back Success Rate (%)", 0, 100, 40)
    
    # Calculate potential ROI based on top 50 high-risk users
    high_risk_df = filtered_df.sort_values(by=['failed_transactions_last_30_days', 'Balance'], ascending=[False, False])
    top_50_risk = high_risk_df.head(50)
    total_campaign_cost = len(top_50_risk) * retention_cost
    projected_saved_revenue = (top_50_risk['Balance'].sum() * (win_back_rate / 100))
    net_roi = projected_saved_revenue - total_campaign_cost
    
    st.sidebar.metric("Total Campaign Cost", f"${total_campaign_cost:,.0f}")
    st.sidebar.metric("Projected Saved Revenue", f"${projected_saved_revenue:,.0f}")
    st.sidebar.metric("Net ROI", f"${net_roi:,.0f}", delta=f"{win_back_rate}% Success Rate")
    
    # --- KPI Calculations ---
    total_customers = len(filtered_df)
    churn_rate = (filtered_df['Exited'].mean() * 100) if total_customers > 0 else 0
    avg_failed_tx = filtered_df['failed_transactions_last_30_days'].mean()
    revenue_at_risk = filtered_df[filtered_df['Exited'] == 1]['Balance'].sum()
    
    # --- AI Root Cause Analysis (Phase 4) ---
    kpi_dict = {
        'total_customers': total_customers,
        'churn_rate': round(churn_rate, 2),
        'avg_failed_tx': round(avg_failed_tx, 2),
        'revenue_risk': revenue_at_risk
    }
    
    with st.spinner("Generating AI Operational Insights..."):
        ai_insight = get_ai_recommendation(kpi_dict)
    
    st.warning(f"**🤖 AI Operational Alert:**\n\n{ai_insight}")
    st.markdown("---")

    # --- KPI Display ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric("Overall Churn Rate", f"{churn_rate:.2f}%")
    col3.metric("Revenue at Risk", f"${revenue_at_risk:,.2f}")
    
    st.markdown("---")
    
    # --- Visualizations ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Churn Rate vs. Failed Transactions")
        churn_by_tx = filtered_df.groupby('failed_transactions_last_30_days')['Exited'].mean().reset_index()
        churn_by_tx['Churn Rate (%)'] = churn_by_tx['Exited'] * 100
        fig_tx = px.bar(churn_by_tx, x='failed_transactions_last_30_days', y='Churn Rate (%)', 
                        labels={'failed_transactions_last_30_days': 'Failed Transactions'},
                        color='Churn Rate (%)', color_continuous_scale='Reds')
        st.plotly_chart(fig_tx, use_container_width=True)
        
    with col_chart2:
        st.subheader("Customer Balance Distribution")
        fig_bal = px.histogram(filtered_df, x="Balance", color="Exited", 
                               marginal="box", barmode="overlay",
                               labels={"Exited": "Churned (1=Yes, 0=No)"},
                               color_discrete_map={0: '#2ecc71', 1: '#e74c3c'})
        st.plotly_chart(fig_bal, use_container_width=True)
        
    st.markdown("---")
    
    # --- Data Table: High-Risk Customers ---
    st.subheader("⚠️ Top 50 'High-Risk' Customers (Highest Probable Churn)")
    st.markdown("Users heavily impacted by payment failures, ranked by Balance.")
    
    # In a real model, we would use predict_proba(). 
    # For this dashboard, we approximate risk by failed transactions and balance.
    # high_risk_df is already calculated above for the ROI simulator
    
    # Add a pseudo-CustomerID for selection purposes
    top_50_risk = top_50_risk.copy()
    top_50_risk.reset_index(inplace=True)
    top_50_risk['Customer_ID'] = top_50_risk.index.map(lambda x: f"CUST-{1000 + x}")
    
    # Move Customer_ID to front
    cols = ['Customer_ID'] + [col for col in top_50_risk.columns if col != 'Customer_ID' and col != 'index']
    top_50_risk = top_50_risk[cols]
    
    st.dataframe(top_50_risk.drop(columns=['Exited']), use_container_width=True)

    st.markdown("---")
    
    # --- Phase 5: Targeted Customer Recovery & AI Outreach ---
    st.subheader("🤖 Phase 5: AI-Powered Customer Recovery")
    st.markdown("Select a high-risk customer from the table above to instantly generate a hyper-personalized retention outreach script.")
    
    selected_cust_id = st.selectbox("Select Customer to Recover:", top_50_risk['Customer_ID'].tolist())
    
    if selected_cust_id:
        cust_profile = top_50_risk[top_50_risk['Customer_ID'] == selected_cust_id].iloc[0]
        
        st.write(f"**Selected Profile:** {cust_profile['Geography']} | Age: {cust_profile['Age']} | Balance: ${cust_profile['Balance']:,.2f} | Failed TXs: {cust_profile['failed_transactions_last_30_days']}")
        
        if st.button("Generate Personalized Recovery Email"):
            with st.spinner("Gemini is drafting the outreach..."):
                outreach_script = generate_customer_outreach_script(cust_profile)
                st.success("Outreach Script Generated Successfully!")
                st.text_area("Copy and paste to CRM:", value=outreach_script, height=250)
